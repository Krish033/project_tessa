"""
Safety Policy — evaluates whether a *specific operation* is safe.

Permission asks:  "Can the agent use this tool?"
Safety Policy asks: "Is THIS particular operation safe?"

The policy reads the tool's own Safety metadata — no hardcoded tool-name checks.
Argument-level rules come from Safety.restricted_args.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.pipeline.tools.meta.policies.safety import Risk, Safety, SafetyError


@dataclass
class PolicyDecision:
    """Result of a safety policy evaluation."""
    allowed: bool
    denied: bool
    requires_approval: bool
    risk: Risk
    reason: str = ""


class SafetyPolicy:
    """
    Evaluates operation-level safety using tool metadata + argument inspection.

    Pipeline:
      1. Read the tool's declared Safety metadata (risk, requires_approval).
      2. Check arguments against restricted_args patterns.
      3. If any restricted pattern matches → deny with reason.
      4. Otherwise → allow, carrying the approval requirement through.
    """

    def evaluate(
        self,
        tool_name: str,
        safety: Safety,
        arguments: dict,
    ) -> PolicyDecision:
        """
        Evaluate whether executing a tool with the given arguments is safe.

        Returns a PolicyDecision. Callers should check:
          - decision.denied → block execution
          - decision.requires_approval → prompt user first
        """
        # Start from the tool's declared risk level
        risk = safety.risk

        # Check restricted argument patterns
        violations = self._check_restricted_args(safety, arguments)

        if violations:
            reason = (
                f"Safety policy denied '{tool_name}': "
                + "; ".join(violations)
            )
            return PolicyDecision(
                allowed=False,
                denied=True,
                requires_approval=False,
                risk=risk,
                reason=reason,
            )

        # No violations — tool is allowed
        return PolicyDecision(
            allowed=True,
            denied=False,
            requires_approval=safety.requires_approval,
            risk=risk,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _check_restricted_args(
        self,
        safety: Safety,
        arguments: dict,
    ) -> list[str]:
        """
        Check arguments against Safety.restricted_args patterns.

        restricted_args is a dict mapping argument names to lists of
        forbidden substrings.  Example:

            restricted_args={"path": [".env", "/etc", "/sys"]}

        If an argument's string value contains any forbidden substring,
        it's flagged as a violation.
        """
        violations: list[str] = []

        for arg_name, patterns in safety.restricted_args.items():
            value = arguments.get(arg_name)
            if value is None or not isinstance(value, str):
                continue

            value_lower = value.lower()
            for pattern in patterns:
                if pattern.lower() in value_lower:
                    violations.append(
                        f"argument '{arg_name}' contains restricted "
                        f"pattern '{pattern}' (value: '{value}')"
                    )

        return violations
