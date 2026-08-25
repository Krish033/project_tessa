import pytest
from app.pipeline.tools.meta.registry import Tool, ToolRegistry


def dummy_func(x: int) -> int:
    return x * 2


def test_tool_dataclass():
    tool = Tool(
        name="test_tool",
        description="A test tool",
        function=dummy_func,
        parameters={"type": "object", "properties": {"x": {"type": "integer"}}},
        permissions={"read": True},
    )
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.function(5) == 10
    assert tool.permissions == {"read": True}


def test_registry_register_and_get():
    registry = ToolRegistry()
    tool = Tool(
        name="calc",
        description="Calculator",
        function=dummy_func,
        parameters={},
    )
    registry.register(tool)

    assert registry.exists("calc") is True
    retrieved = registry.get("calc")
    assert retrieved == tool


def test_registry_duplicate_raises_value_error():
    registry = ToolRegistry()
    tool = Tool(name="calc", description="Calc", function=dummy_func, parameters={})
    registry.register(tool)

    with pytest.raises(ValueError, match="Tool already registered: calc"):
        registry.register(tool)


def test_registry_get_nonexistent_raises_key_error():
    registry = ToolRegistry()
    with pytest.raises(KeyError, match="Tool not found: unknown_tool"):
        registry.get("unknown_tool")


def test_registry_get_all():
    registry = ToolRegistry()
    tool1 = Tool(name="tool1", description="1", function=dummy_func, parameters={})
    tool2 = Tool(name="tool2", description="2", function=dummy_func, parameters={})

    registry.register(tool1)
    registry.register(tool2)

    all_tools = registry.get_all()
    assert len(all_tools) == 2
    assert tool1 in all_tools
    assert tool2 in all_tools


def test_registry_exists_false_for_missing():
    registry = ToolRegistry()
    assert registry.exists("missing") is False
