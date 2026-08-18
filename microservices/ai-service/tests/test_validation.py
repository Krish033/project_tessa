"""
Tests for ToolValidator and ArgumentValidator.

Run with:
    pytest tests/test_validation.py -v
"""

import pytest
from dataclasses import dataclass, field
from typing import Callable

from app.pipeline.tools.meta.validation.validator import (
    ToolValidator,
    ArgumentValidator,
    ValidationError,
    FieldError,
    _is_valid_email,
    _is_valid_url,
)


# ---------------------------------------------------------------------------
# Minimal Tool stub (mirrors registry.Tool without the DB dependency)
# ---------------------------------------------------------------------------

@dataclass
class StubTool:
    name: str
    description: str = ""
    function: Callable = lambda **kw: "ok"
    parameters: dict = field(default_factory=dict)
    permissions: dict = field(default_factory=dict)


def make_tool(name: str, properties: dict, required: list = None, **extra) -> StubTool:
    params = {"type": "object", "properties": properties, "required": required or []}
    params.update(extra)
    return StubTool(name=name, parameters=params)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_tv = ToolValidator()
_av = ArgumentValidator()


def tv(tool, args):
    """Run ToolValidator, return list of field names that errored."""
    try:
        _tv.validate(tool.name, tool, args)
        return []
    except ValidationError as e:
        return [err.field for err in e.errors]


def av(tool, args):
    """Run ArgumentValidator, return list of field names that errored."""
    try:
        _av.validate(tool, args)
        return []
    except ValidationError as e:
        return [err.field for err in e.errors]


# ===========================================================================
# ToolValidator tests
# ===========================================================================

class TestToolValidator:

    def test_valid_call_passes(self):
        tool = make_tool("web_search",
                         {"query": {"type": "string"}, "max_results": {"type": "integer"}},
                         required=["query"])
        assert tv(tool, {"query": "python async", "max_results": 5}) == []

    def test_missing_required_field(self):
        tool = make_tool("web_search",
                         {"query": {"type": "string"}},
                         required=["query"])
        errors = tv(tool, {})
        assert "query" in errors

    def test_unknown_field_rejected(self):
        tool = make_tool("web_search",
                         {"query": {"type": "string"}},
                         required=["query"])
        errors = tv(tool, {"query": "hello", "evil_param": "x"})
        assert "evil_param" in errors

    def test_wrong_type_string_for_integer(self):
        tool = make_tool("paginate",
                         {"page": {"type": "integer"}},
                         required=["page"])
        errors = tv(tool, {"page": "not-a-number"})
        assert "page" in errors

    def test_bool_rejected_for_integer(self):
        tool = make_tool("paginate",
                         {"page": {"type": "integer"}},
                         required=["page"])
        errors = tv(tool, {"page": True})
        assert "page" in errors

    def test_string_too_short(self):
        tool = make_tool("search",
                         {"query": {"type": "string", "minLength": 3}},
                         required=["query"])
        errors = tv(tool, {"query": "hi"})
        assert "query" in errors

    def test_string_too_long(self):
        tool = make_tool("search",
                         {"query": {"type": "string", "maxLength": 5}},
                         required=["query"])
        errors = tv(tool, {"query": "toolongquery"})
        assert "query" in errors

    def test_valid_url_passes(self):
        tool = make_tool("fetch_url",
                         {"url": {"type": "string", "format": "uri"}},
                         required=["url"])
        assert tv(tool, {"url": "https://example.com"}) == []

    def test_invalid_url_rejected(self):
        tool = make_tool("fetch_url",
                         {"url": {"type": "string", "format": "uri"}},
                         required=["url"])
        errors = tv(tool, {"url": "not-a-url"})
        assert "url" in errors

    def test_valid_email_format_passes(self):
        tool = make_tool("send_email",
                         {"to": {"type": "string", "format": "email"}},
                         required=["to"])
        assert tv(tool, {"to": "krishna@example.com"}) == []

    def test_invalid_email_format_rejected(self):
        tool = make_tool("send_email",
                         {"to": {"type": "string", "format": "email"}},
                         required=["to"])
        errors = tv(tool, {"to": "not-an-email"})
        assert "to" in errors

    def test_number_below_minimum(self):
        tool = make_tool("rate",
                         {"score": {"type": "number", "minimum": 0, "maximum": 10}},
                         required=["score"])
        errors = tv(tool, {"score": -1})
        assert "score" in errors

    def test_number_above_maximum(self):
        tool = make_tool("rate",
                         {"score": {"type": "number", "minimum": 0, "maximum": 10}},
                         required=["score"])
        errors = tv(tool, {"score": 11})
        assert "score" in errors

    def test_optional_field_absent_is_ok(self):
        tool = make_tool("search",
                         {"query": {"type": "string"}, "max_results": {"type": "integer"}},
                         required=["query"])
        assert tv(tool, {"query": "test"}) == []

    def test_array_type_accepted(self):
        tool = make_tool("batch",
                         {"items": {"type": "array"}},
                         required=["items"])
        assert tv(tool, {"items": [1, 2, 3]}) == []

    def test_object_type_accepted(self):
        tool = make_tool("api",
                         {"headers": {"type": "object"}},
                         required=["headers"])
        assert tv(tool, {"headers": {"Authorization": "Bearer tok"}}) == []


# ===========================================================================
# ArgumentValidator tests
# ===========================================================================

class TestArgumentValidator:

    def test_required_field_blank_string_rejected(self):
        tool = make_tool("send_email",
                         {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                         required=["to", "subject", "body"])
        errors = av(tool, {"to": "a@b.com", "subject": "  ", "body": "hello"})
        assert "subject" in errors

    def test_integer_string_coerced(self):
        tool = make_tool("paginate",
                         {"page": {"type": "integer"}},
                         required=["page"])
        args = {"page": "3"}
        av(tool, args)
        assert args["page"] == 3

    def test_boolean_string_coerced(self):
        tool = make_tool("toggle",
                         {"enabled": {"type": "boolean"}},
                         required=["enabled"])
        args = {"enabled": "true"}
        av(tool, args)
        assert args["enabled"] is True

    def test_bad_boolean_string_rejected(self):
        tool = make_tool("toggle",
                         {"enabled": {"type": "boolean"}},
                         required=["enabled"])
        errors = av(tool, {"enabled": "maybe"})
        assert "enabled" in errors

    def test_email_constraint_from_argument_constraints(self):
        tool = make_tool(
            "send_email",
            {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
            required=["to", "subject", "body"],
            argument_constraints={"to": {"format": "email"}},
        )
        errors = av(tool, {"to": "bad-email", "subject": "Hi", "body": "text"})
        assert "to" in errors

    def test_valid_email_constraint_passes(self):
        tool = make_tool(
            "send_email",
            {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
            required=["to", "subject", "body"],
            argument_constraints={"to": {"format": "email"}},
        )
        assert av(tool, {"to": "user@domain.com", "subject": "Hi", "body": "text"}) == []

    def test_max_length_constraint(self):
        tool = make_tool(
            "send_email",
            {"subject": {"type": "string", "maxLength": 200}},
            required=["subject"],
        )
        errors = av(tool, {"subject": "x" * 201})
        assert "subject" in errors

    def test_max_bytes_constraint(self):
        tool = make_tool(
            "send_email",
            {"body": {"type": "string"}},
            required=["body"],
            argument_constraints={"body": {"max_bytes": 10}},
        )
        errors = av(tool, {"body": "this string is definitely more than ten bytes long"})
        assert "body" in errors

    def test_cross_argument_end_after_start(self):
        tool = make_tool(
            "calendar_create",
            {"start_time": {"type": "string"}, "end_time": {"type": "string"}},
            required=["start_time", "end_time"],
            cross_argument_rules=[
                {"type": "end_after_start", "start": "start_time", "end": "end_time"}
            ],
        )
        errors = av(tool, {"start_time": "2024-01-01T10:00", "end_time": "2024-01-01T09:00"})
        assert "end_time" in errors

    def test_cross_argument_valid_order_passes(self):
        tool = make_tool(
            "calendar_create",
            {"start_time": {"type": "string"}, "end_time": {"type": "string"}},
            required=["start_time", "end_time"],
            cross_argument_rules=[
                {"type": "end_after_start", "start": "start_time", "end": "end_time"}
            ],
        )
        assert av(tool, {"start_time": "2024-01-01T09:00", "end_time": "2024-01-01T10:00"}) == []

    def test_multiple_errors_all_reported(self):
        tool = make_tool(
            "send_email",
            {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
            required=["to", "subject", "body"],
            argument_constraints={"to": {"format": "email"}, "subject": {"max_length": 5}},
        )
        try:
            _av.validate(tool, {"to": "bad", "subject": "toolongsubject", "body": "hi"})
            assert False, "should have raised"
        except ValidationError as e:
            fields = [err.field for err in e.errors]
            assert "to" in fields
            assert "subject" in fields


# ===========================================================================
# Helper function tests
# ===========================================================================

class TestHelpers:

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "a.b+c@domain.co.uk",
        "123@test.org",
    ])
    def test_valid_emails(self, email):
        assert _is_valid_email(email)

    @pytest.mark.parametrize("email", [
        "notanemail",
        "@nodomain.com",
        "missing@",
        "spaces in@email.com",
    ])
    def test_invalid_emails(self, email):
        assert not _is_valid_email(email)

    @pytest.mark.parametrize("url", [
        "https://example.com",
        "http://localhost:8000/api",
        "ftp://files.server.net/file.txt",
    ])
    def test_valid_urls(self, url):
        assert _is_valid_url(url)

    @pytest.mark.parametrize("url", [
        "not-a-url",
        "example.com",         # no scheme
        "://missing-scheme",
    ])
    def test_invalid_urls(self, url):
        assert not _is_valid_url(url)
