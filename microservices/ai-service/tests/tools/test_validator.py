import pytest
from app.pipeline.tools.meta.registry import Tool
from app.pipeline.tools.meta.validation import (
    ToolValidator,
    ArgumentValidator,
    ValidationError,
    FieldError,
)


def dummy_func(**kwargs):
    return kwargs


def test_field_error_str():
    err = FieldError("query", "is required")
    assert str(err) == "[query] is required"


def test_tool_validator_valid_arguments():
    tool = Tool(
        name="search",
        description="Search",
        function=dummy_func,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 2},
                "count": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "required": ["query"],
        },
    )

    validator = ToolValidator()
    # Should not raise
    validator.validate("search", tool, {"query": "python", "count": 10})


def test_tool_validator_missing_required():
    tool = Tool(
        name="search",
        description="Search",
        function=dummy_func,
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    )

    validator = ToolValidator()
    with pytest.raises(ValidationError) as exc:
        validator.validate("search", tool, {})

    assert any(e.field == "query" and "required" in e.message for e in exc.value.errors)


def test_tool_validator_unknown_fields():
    tool = Tool(
        name="search",
        description="Search",
        function=dummy_func,
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    )

    validator = ToolValidator()
    with pytest.raises(ValidationError) as exc:
        validator.validate("search", tool, {"query": "test", "extra_param": 123})

    assert any(e.field == "extra_param" for e in exc.value.errors)


def test_tool_validator_type_mismatch():
    tool = Tool(
        name="search",
        description="Search",
        function=dummy_func,
        parameters={
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
            },
        },
    )

    validator = ToolValidator()
    with pytest.raises(ValidationError) as exc:
        validator.validate("search", tool, {"count": "not_an_int"})

    assert any(e.field == "count" for e in exc.value.errors)


def test_argument_validator_coercion():
    tool = Tool(
        name="test",
        description="test",
        function=dummy_func,
        parameters={
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "active": {"type": "boolean"},
                "ratio": {"type": "number"},
            },
        },
    )

    validator = ArgumentValidator()
    args = {"count": "42", "active": "true", "ratio": "3.14"}
    validator.validate(tool, args)

    assert args["count"] == 42
    assert args["active"] is True
    assert args["ratio"] == 3.14


def test_argument_validator_blank_required_rejected():
    tool = Tool(
        name="test",
        description="test",
        function=dummy_func,
        parameters={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    )

    validator = ArgumentValidator()
    with pytest.raises(ValidationError) as exc:
        validator.validate(tool, {"name": "   "})

    assert any(e.field == "name" for e in exc.value.errors)
