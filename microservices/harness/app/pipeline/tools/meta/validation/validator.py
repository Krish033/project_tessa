"""
Tool validation layer.

Two-phase validation before any tool executes:

  Phase 1 — ToolValidator (schema shape):
    - Tool name exists in registry
    - All required fields present
    - No unknown fields
    - Correct Python types per JSON Schema type
    - String length constraints (minLength / maxLength from schema)
    - URL format for fields annotated format="uri"

  Phase 2 — ArgumentValidator (value semantics):
    - validate_required()      – required fields non-empty
    - validate_types()         – runtime type coercion / strict check
    - validate_constraints()   – per-field semantic rules (email, maxLength, min/max)
    - validate_cross_arguments() – cross-field rules (e.g. end > start)

Both raise ValidationError on failure. ValidationError carries a list of
FieldError items so callers can surface all problems at once.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------

@dataclass
class FieldError:
    field: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field}] {self.message}"


class ValidationError(Exception):
    """Raised when one or more validation checks fail."""

    def __init__(self, errors: list[FieldError]):
        self.errors = errors
        super().__init__("; ".join(str(e) for e in errors))


# ---------------------------------------------------------------------------
# JSON Schema → Python type map
# ---------------------------------------------------------------------------

_JSON_TYPE_MAP: dict[str, type | tuple[type, ...]] = {
    "string":  str,
    "integer": int,
    "number":  (int, float),
    "boolean": bool,
    "array":   list,
    "object":  dict,
}


# ---------------------------------------------------------------------------
# Phase 1 — ToolValidator
# ---------------------------------------------------------------------------

class ToolValidator:
    """
    Validates that a tool call is structurally correct against the tool's
    JSON Schema (parameters dict). Raises ValidationError on failure.
    """

    def validate(self, tool_name: str, tool, arguments: dict) -> None:
        """
        Entry point. Call before executing any tool.

        Args:
            tool_name:  Name the LLM requested (already resolved).
            tool:       Tool dataclass from the registry.
            arguments:  Raw argument dict from the LLM response.
        """
        errors: list[FieldError] = []
        schema: dict = tool.parameters or {}
        properties: dict = schema.get("properties", {})
        required: list[str] = schema.get("required", [])

        # 1. Required fields present
        for req in required:
            if req not in arguments:
                errors.append(FieldError(req, "required field is missing"))

        # 2. No unknown fields
        for arg in arguments:
            if properties and arg not in properties:
                errors.append(FieldError(arg, f"unknown field — not in schema for '{tool_name}'"))

        # 3. Per-field type + constraint checks
        for arg_name, value in arguments.items():
            prop = properties.get(arg_name)
            if prop is None:
                continue  # already flagged as unknown above

            field_errors = self._check_field(arg_name, value, prop)
            errors.extend(field_errors)

        if errors:
            raise ValidationError(errors)

    # ------------------------------------------------------------------

    def _check_field(self, name: str, value: Any, prop: dict) -> list[FieldError]:
        errors: list[FieldError] = []
        expected_type = prop.get("type")
        fmt = prop.get("format", "")

        # Type check
        if expected_type and expected_type in _JSON_TYPE_MAP:
            py_type = _JSON_TYPE_MAP[expected_type]
            # bool is a subclass of int in Python — handle explicitly
            if expected_type == "integer" and isinstance(value, bool):
                errors.append(FieldError(name, f"expected integer, got bool"))
            elif not isinstance(value, py_type):
                errors.append(FieldError(name, f"expected {expected_type}, got {type(value).__name__}"))

        # String-specific checks
        if isinstance(value, str):
            min_len = prop.get("minLength")
            max_len = prop.get("maxLength")
            if min_len is not None and len(value) < min_len:
                errors.append(FieldError(name, f"too short: min {min_len} chars, got {len(value)}"))
            if max_len is not None and len(value) > max_len:
                errors.append(FieldError(name, f"too long: max {max_len} chars, got {len(value)}"))
            if fmt == "uri" and not _is_valid_url(value):
                errors.append(FieldError(name, f"invalid URL: '{value}'"))
            if fmt == "email" and not _is_valid_email(value):
                errors.append(FieldError(name, f"invalid email: '{value}'"))

        # Numeric range checks
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            minimum = prop.get("minimum")
            maximum = prop.get("maximum")
            if minimum is not None and value < minimum:
                errors.append(FieldError(name, f"value {value} is below minimum {minimum}"))
            if maximum is not None and value > maximum:
                errors.append(FieldError(name, f"value {value} exceeds maximum {maximum}"))

        return errors


# ---------------------------------------------------------------------------
# Phase 2 — ArgumentValidator
# ---------------------------------------------------------------------------

class ArgumentValidator:
    """
    Validates the *semantic* correctness of tool arguments — values, not just types.

    Tools may optionally declare an `argument_constraints` dict on their schema:

        "argument_constraints": {
            "to":      {"format": "email"},
            "subject": {"min_length": 1, "max_length": 200},
            "body":    {"max_bytes": 1_000_000},
        }

    This class also runs the four standard passes in order.
    Raises ValidationError if any pass finds errors.
    """

    def validate(self, tool, arguments: dict) -> None:
        errors: list[FieldError] = []
        errors.extend(self.validate_required(tool, arguments))
        errors.extend(self.validate_types(tool, arguments))
        errors.extend(self.validate_constraints(tool, arguments))
        errors.extend(self.validate_cross_arguments(tool, arguments))
        if errors:
            raise ValidationError(errors)

    # ------------------------------------------------------------------
    # Pass 1 — required fields are non-empty (not just present)
    # ------------------------------------------------------------------

    def validate_required(self, tool, arguments: dict) -> list[FieldError]:
        errors: list[FieldError] = []
        required = (tool.parameters or {}).get("required", [])
        for req in required:
            val = arguments.get(req)
            if val is None or (isinstance(val, str) and not val.strip()):
                errors.append(FieldError(req, "required field is empty or blank"))
        return errors

    # ------------------------------------------------------------------
    # Pass 2 — runtime type coercion / strict check
    # ------------------------------------------------------------------

    def validate_types(self, tool, arguments: dict) -> list[FieldError]:
        """
        Attempts safe coercion for LLM-produced values (e.g. "5" → 5 for integers).
        Mutates `arguments` in-place on successful coercion.
        Reports an error when coercion fails.
        """
        errors: list[FieldError] = []
        properties = (tool.parameters or {}).get("properties", {})
        for name, value in list(arguments.items()):
            prop = properties.get(name)
            if not prop:
                continue
            expected = prop.get("type")
            if not expected or expected not in _JSON_TYPE_MAP:
                continue

            py_type = _JSON_TYPE_MAP[expected]

            if expected == "integer":
                if isinstance(value, bool):
                    errors.append(FieldError(name, "expected integer, got bool"))
                elif isinstance(value, str):
                    try:
                        arguments[name] = int(value)
                    except ValueError:
                        errors.append(FieldError(name, f"cannot coerce '{value}' to integer"))
            elif expected == "number":
                if isinstance(value, str):
                    try:
                        arguments[name] = float(value)
                    except ValueError:
                        errors.append(FieldError(name, f"cannot coerce '{value}' to number"))
            elif expected == "boolean":
                if isinstance(value, str):
                    if value.lower() in ("true", "1", "yes"):
                        arguments[name] = True
                    elif value.lower() in ("false", "0", "no"):
                        arguments[name] = False
                    else:
                        errors.append(FieldError(name, f"cannot coerce '{value}' to boolean"))

        return errors

    # ------------------------------------------------------------------
    # Pass 3 — semantic value constraints from argument_constraints
    # ------------------------------------------------------------------

    def validate_constraints(self, tool, arguments: dict) -> list[FieldError]:
        errors: list[FieldError] = []
        constraints: dict = (tool.parameters or {}).get("argument_constraints", {})

        # Also derive implicit constraints from JSON Schema property annotations
        properties = (tool.parameters or {}).get("properties", {})
        merged: dict[str, dict] = {}
        for name, prop in properties.items():
            c: dict = {}
            if prop.get("format") == "email":
                c["format"] = "email"
            if prop.get("format") == "uri":
                c["format"] = "uri"
            if "minLength" in prop:
                c["min_length"] = prop["minLength"]
            if "maxLength" in prop:
                c["max_length"] = prop["maxLength"]
            if c:
                merged[name] = c
        # explicit argument_constraints take precedence
        for name, c in constraints.items():
            merged.setdefault(name, {}).update(c)

        for name, rules in merged.items():
            value = arguments.get(name)
            if value is None:
                continue

            fmt = rules.get("format")
            if fmt == "email" and not _is_valid_email(str(value)):
                errors.append(FieldError(name, f"invalid email address: '{value}'"))
            if fmt == "uri" and not _is_valid_url(str(value)):
                errors.append(FieldError(name, f"invalid URL: '{value}'"))

            min_len = rules.get("min_length")
            max_len = rules.get("max_length")
            max_bytes = rules.get("max_bytes")

            if isinstance(value, str):
                if min_len is not None and len(value) < min_len:
                    errors.append(FieldError(name, f"too short: min {min_len} chars"))
                if max_len is not None and len(value) > max_len:
                    errors.append(FieldError(name, f"too long: max {max_len} chars, got {len(value)}"))
                if max_bytes is not None and len(value.encode()) > max_bytes:
                    errors.append(FieldError(name, f"exceeds max byte size of {max_bytes}"))

        return errors

    # ------------------------------------------------------------------
    # Pass 4 — cross-argument rules (override in subclass or via tool hook)
    # ------------------------------------------------------------------

    def validate_cross_arguments(self, tool, arguments: dict) -> list[FieldError]:
        """
        Checks cross-field rules declared under tool.parameters["cross_argument_rules"].

        Supported rule types:
          - {"type": "end_after_start", "start": "start_time", "end": "end_time"}
        """
        errors: list[FieldError] = []
        rules: list[dict] = (tool.parameters or {}).get("cross_argument_rules", [])

        for rule in rules:
            rule_type = rule.get("type")
            if rule_type == "end_after_start":
                start_field = rule.get("start")
                end_field = rule.get("end")
                start_val = arguments.get(start_field)
                end_val = arguments.get(end_field)
                if start_val and end_val and end_val <= start_val:
                    errors.append(FieldError(
                        end_field,
                        f"'{end_field}' must be after '{start_field}'"
                    ))

        return errors


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_valid_url(value: str) -> bool:
    try:
        result = urlparse(value)
        return result.scheme in ("http", "https", "ftp") and bool(result.netloc)
    except Exception:
        return False


def _is_valid_email(value: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value.strip()))
