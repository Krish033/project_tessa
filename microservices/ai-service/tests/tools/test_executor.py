import pytest
from unittest.mock import Mock
from app.pipeline.tools.meta.registry import Tool, ToolRegistry
from app.pipeline.tools.meta.executor import ToolExecutor
from app.pipeline.tools.meta.validation import ValidationError


def add_numbers(a: int, b: int) -> int:
    return a + b


async def async_fetch(query: str) -> str:
    return f"Fetched: {query}"


@pytest.mark.anyio
async def test_executor_sync_tool():
    registry = ToolRegistry()
    tool = Tool(
        name="add",
        description="Add two numbers",
        function=add_numbers,
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    )
    registry.register(tool)

    executor = ToolExecutor(registry)
    result = await executor.execute("add", {"a": 3, "b": 4})

    assert result == {
        "tool": "add",
        "success": True,
        "result": 7,
    }


@pytest.mark.anyio
async def test_executor_async_tool():
    registry = ToolRegistry()
    tool = Tool(
        name="fetch",
        description="Async fetch",
        function=async_fetch,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    )
    registry.register(tool)

    executor = ToolExecutor(registry)
    result = await executor.execute("fetch", {"query": "python"})

    assert result == {
        "tool": "fetch",
        "success": True,
        "result": "Fetched: python",
    }


@pytest.mark.anyio
async def test_executor_unregistered_tool():
    registry = ToolRegistry()
    executor = ToolExecutor(registry)

    with pytest.raises(KeyError, match="Tool not found: nonexistent"):
        await executor.execute("nonexistent", {})


@pytest.mark.anyio
async def test_executor_validation_failure():
    registry = ToolRegistry()
    tool = Tool(
        name="add",
        description="Add numbers",
        function=add_numbers,
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    )
    registry.register(tool)

    executor = ToolExecutor(registry)
    # Missing required argument 'b'
    with pytest.raises(ValidationError):
        await executor.execute("add", {"a": 3})


# ---------------------------------------------------------------------------
# Permission + Safety integration tests
# ---------------------------------------------------------------------------

def _make_dangerous_tool():
    """Create a tool marked as DANGEROUS for testing."""
    from app.pipeline.tools.meta.policies.safety import Safety, Risk, PermissionLevel
    return Tool(
        name="danger_tool",
        description="A dangerous tool",
        function=lambda: "executed",
        parameters={"type": "object", "properties": {}, "required": []},
        safety=Safety(risk=Risk.HIGH, permission=PermissionLevel.DANGEROUS),
    )


def _make_approval_tool():
    """Create a tool that requires approval for testing."""
    from app.pipeline.tools.meta.policies.safety import Safety, Risk, PermissionLevel
    return Tool(
        name="approval_tool",
        description="Needs approval",
        function=lambda: "executed",
        parameters={"type": "object", "properties": {}, "required": []},
        safety=Safety(risk=Risk.CRITICAL, permission=PermissionLevel.DANGEROUS, requires_approval=True),
    )


def _make_restricted_tool():
    """Create a tool with restricted argument patterns."""
    from app.pipeline.tools.meta.policies.safety import Safety, Risk, PermissionLevel
    return Tool(
        name="file_delete",
        description="Delete a file",
        function=lambda path: f"deleted {path}",
        parameters={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
        safety=Safety(
            risk=Risk.HIGH,
            permission=PermissionLevel.WRITE,
            restricted_args={"path": [".env", "/etc"]},
        ),
    )


@pytest.mark.anyio
async def test_executor_dangerous_tool_denied_by_default():
    from app.pipeline.tools.meta.policies.permission_manager import PermissionManager
    registry = ToolRegistry()
    registry.register(_make_dangerous_tool())
    executor = ToolExecutor(registry, permission_manager=PermissionManager())

    with pytest.raises(PermissionError, match="Permission denied"):
        await executor.execute("danger_tool", {})


@pytest.mark.anyio
async def test_executor_dangerous_tool_allowed_with_override():
    from app.pipeline.tools.meta.policies.permission_manager import PermissionManager
    registry = ToolRegistry()
    registry.register(_make_dangerous_tool())
    pm = PermissionManager()
    pm.allow_tool("danger_tool")
    executor = ToolExecutor(registry, permission_manager=pm)

    result = await executor.execute("danger_tool", {})
    assert result["success"] is True
    assert result["result"] == "executed"


@pytest.mark.anyio
async def test_executor_safety_policy_blocks_restricted_args():
    from app.pipeline.tools.meta.policies.safety import SafetyError
    registry = ToolRegistry()
    registry.register(_make_restricted_tool())
    executor = ToolExecutor(registry)

    with pytest.raises(SafetyError, match=".env"):
        await executor.execute("file_delete", {"path": "/project/.env"})


@pytest.mark.anyio
async def test_executor_safety_policy_allows_safe_args():
    registry = ToolRegistry()
    registry.register(_make_restricted_tool())
    executor = ToolExecutor(registry)

    result = await executor.execute("file_delete", {"path": "/tmp/test.txt"})
    assert result["success"] is True
    assert result["result"] == "deleted /tmp/test.txt"


@pytest.mark.anyio
async def test_executor_approval_denied(monkeypatch):
    from app.pipeline.tools.meta.policies.safety import SafetyError
    from app.pipeline.tools.meta.policies.permission_manager import PermissionManager
    registry = ToolRegistry()
    registry.register(_make_approval_tool())
    pm = PermissionManager()
    pm.allow_tool("approval_tool")
    executor = ToolExecutor(registry, permission_manager=pm)

    # Simulate user typing "n" at the approval prompt
    monkeypatch.setattr("builtins.input", lambda _: "n")

    with pytest.raises(SafetyError, match="User denied approval"):
        await executor.execute("approval_tool", {})


@pytest.mark.anyio
async def test_executor_approval_granted(monkeypatch):
    from app.pipeline.tools.meta.policies.permission_manager import PermissionManager
    registry = ToolRegistry()
    registry.register(_make_approval_tool())
    pm = PermissionManager()
    pm.allow_tool("approval_tool")
    executor = ToolExecutor(registry, permission_manager=pm)

    # Simulate user typing "y" at the approval prompt
    monkeypatch.setattr("builtins.input", lambda _: "y")

    result = await executor.execute("approval_tool", {})
    assert result["success"] is True

