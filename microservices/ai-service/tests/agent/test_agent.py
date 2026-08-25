import pytest
from unittest.mock import Mock, AsyncMock
from app.agent import AgentLoop
from app.utils import _extract_json_object, _format_tool_activity, JsonResponse, _sanitize_json_escapes



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


@pytest.mark.anyio
async def test_agent_loop_primitive_json_response():
    mock_ctx = Mock()
    mock_ctx.build = AsyncMock(return_value=[{"role": "user", "content": "What is 25 * 48?"}])
    mock_ctx.add = Mock()

    mock_llm = Mock()
    # LLM outputs a bare integer or string
    mock_llm.run_stream = AsyncMock(return_value=("", "1200"))

    mock_executor = Mock()

    agent = AgentLoop(
        ctx=mock_ctx,
        llm=mock_llm,
        executor=mock_executor,
        max_iterations=5,
        verbose=False,
    )

    answer = await agent.run("What is 25 * 48?")
    assert answer == "1200"


def test_sanitize_json_escapes():
    from app.utils import _sanitize_json_escapes
    # \\. and \\p in regex/paths should be sanitized to \\\\. and \\\\p
    raw = r'{"pattern": ".*\.py$", "path": "C:\Users\projects\data", "valid": "\n\t\""}'
    sanitized = _sanitize_json_escapes(raw)
    import json
    parsed = json.loads(sanitized)
    assert parsed["pattern"] == r".*\.py$"
    assert parsed["path"] == r"C:\Users\projects\data"
    assert parsed["valid"] == '\n\t"'


@pytest.mark.anyio
async def test_agent_loop_unescaped_regex_tool_call():
    mock_ctx = Mock()
    mock_ctx.build = AsyncMock(return_value=[{"role": "user", "content": "find files"}])
    mock_ctx.add = Mock()

    # Model outputs tool call with invalid escape sequence \.
    step1_resp = '{\n  "action": "tool",\n  "tool": "search_files",\n  "arguments": {\n    "file_pattern": ".*\\.py$"\n  }\n}'
    step2_resp = '{"action": "final", "answer": "Found files", "ltm": []}'

    mock_llm = Mock()
    mock_llm.run_stream = AsyncMock(
        side_effect=[
            ("", step1_resp),
            ("", step2_resp),
        ]
    )

    mock_executor = Mock()
    mock_executor.execute = AsyncMock(return_value={"result": "file1.py"})

    agent = AgentLoop(
        ctx=mock_ctx,
        llm=mock_llm,
        executor=mock_executor,
        max_iterations=5,
        verbose=False,
    )

    answer = await agent.run("find files")
    assert answer == "Found files"
    mock_executor.execute.assert_awaited_once_with("search_files", {"file_pattern": ".*\\.py$"})


def test_json_response_final():
    raw = '```json\n{"action": "final", "answer": "The total is 42", "ltm": ["User prefers Python"]}\n```'
    resp = JsonResponse.parse(raw)
    assert resp.is_final is True
    assert resp.is_tool is False
    assert resp.answer == "The total is 42"
    assert resp.ltm_facts == ["User prefers Python"]
    assert resp["action"] == "final"
    assert resp.get("answer") == "The total is 42"


def test_json_response_tool():
    raw = '{"action": "tool", "tool": "web_search", "arguments": {"query": "deep learning"}}'
    resp = JsonResponse.parse(raw)
    assert resp.is_tool is True
    assert resp.is_final is False
    assert resp.tool_name == "web_search"
    assert resp.arguments == {"query": "deep learning"}
    assert '"tool": "web_search"' in resp.format_tool_call()


def test_json_response_legacy_action_as_tool_name():
    raw = '{"action": "get_os_info", "section": "all"}'
    resp = JsonResponse.parse(raw)
    assert resp.is_tool is True
    assert resp.tool_name == "get_os_info"
    assert resp.arguments == {"section": "all"}


def test_json_response_plain_text_fallback():
    raw = "Just a direct string reply without any JSON structure."
    resp = JsonResponse.parse(raw)
    assert resp.is_final is True
    assert resp.answer == "Just a direct string reply without any JSON structure."
