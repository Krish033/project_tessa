import pytest
from unittest.mock import Mock, AsyncMock
from app.agent import _extract_json_object, _format_tool_activity, AgentLoop


def test_extract_json_object_simple():
    text = 'Here is the response: {"action": "final", "answer": "Hello!"} thanks.'
    result = _extract_json_object(text)
    assert result == {"action": "final", "answer": "Hello!"}


def test_extract_json_object_with_think_tags():
    text = '<think>I need to search</think>{"action": "tool", "tool": "web_search", "arguments": {"query": "python"}}'
    result = _extract_json_object(text)
    assert result == {
        "action": "tool",
        "tool": "web_search",
        "arguments": {"query": "python"},
    }


def test_extract_json_object_nested():
    text = '```json\n{"action": "tool", "tool": "edit_file", "arguments": {"nested": {"a": 1}}}\n```'
    result = _extract_json_object(text)
    assert result["arguments"]["nested"]["a"] == 1


def test_extract_json_object_none_on_invalid():
    assert _extract_json_object("no json here") is None


def test_format_tool_activity():
    assert "Searching the web" in _format_tool_activity("web_search", {"query": "python"})
    assert "Checking system information" in _format_tool_activity("get_os_info", {})
    assert "Running command" in _format_tool_activity("execute_command", {"command": "dir"})
    assert "Fetching webpage" in _format_tool_activity("fetch_url", {"url": "https://python.org"})


@pytest.mark.anyio
async def test_agent_loop_final_answer():
    mock_ctx = Mock()
    mock_ctx.build = AsyncMock(return_value=[{"role": "user", "content": "hi"}])
    mock_ctx.add = Mock()

    mock_llm = Mock()
    mock_llm.run_stream = AsyncMock(
        return_value=("", '{"action": "final", "answer": "Hello there!", "ltm": []}')
    )

    mock_executor = Mock()

    agent = AgentLoop(
        ctx=mock_ctx,
        llm=mock_llm,
        executor=mock_executor,
        max_iterations=5,
        verbose=False,
    )

    answer = await agent.run("hi")

    assert answer == "Hello there!"
    mock_ctx.add.assert_any_call("user", "hi")
    mock_ctx.add.assert_any_call("assistant", "Hello there!")


@pytest.mark.anyio
async def test_agent_loop_tool_execution():
    mock_ctx = Mock()
    mock_ctx.build = AsyncMock(return_value=[{"role": "user", "content": "check os"}])
    mock_ctx.add = Mock()

    # Step 1 returns tool call, Step 2 returns final answer
    step1_resp = '{"action": "tool", "tool": "get_os_info", "arguments": {}}'
    step2_resp = '{"action": "final", "answer": "Windows 11", "ltm": []}'

    mock_llm = Mock()
    mock_llm.run_stream = AsyncMock(
        side_effect=[
            ("", step1_resp),
            ("", step2_resp),
        ]
    )

    mock_executor = Mock()
    mock_executor.execute = AsyncMock(return_value={"result": "OS: Windows 11"})

    agent = AgentLoop(
        ctx=mock_ctx,
        llm=mock_llm,
        executor=mock_executor,
        max_iterations=5,
        verbose=False,
    )

    answer = await agent.run("check os")

    assert answer == "Windows 11"
    mock_executor.execute.assert_awaited_once_with("get_os_info", {})
