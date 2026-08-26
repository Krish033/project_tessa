import pytest
from unittest.mock import Mock, AsyncMock
from pydantic import ValidationError
from app.agent import AgentLoop
from app.models.schemas import LLMResponse


@pytest.mark.anyio
async def test_agent_loop_final_answer():
    mock_ctx = Mock()
    mock_ctx.build = AsyncMock(return_value=[{"role": "user", "content": "hi"}])
    mock_ctx.add = Mock()

    mock_llm = Mock()
    mock_llm.run = Mock(
        return_value='{"action": "final", "answer": "Hello there!", "ltm": []}'
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

    step1_resp = '{"action": "tool", "tool": "get_os_info", "arguments": {}}'
    step2_resp = '{"action": "final", "answer": "Windows 11", "ltm": []}'

    mock_llm = Mock()
    mock_llm.run = Mock(
        side_effect=[
            step1_resp,
            step2_resp,
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


def test_llm_response_final():
    raw = '```json\n{"action": "final", "answer": "The total is 42", "ltm": ["User prefers Python"]}\n```'
    resp = LLMResponse.parse(raw)
    assert resp.is_final is True
    assert resp.is_tool is False
    assert resp.answer == "The total is 42"
    assert resp.ltm_facts == ["User prefers Python"]


def test_llm_response_tool():
    raw = '{"action": "tool", "tool": "web_search", "arguments": {"query": "deep learning"}}'
    resp = LLMResponse.parse(raw)
    assert resp.is_tool is True
    assert resp.is_final is False
    assert resp.tool_name == "web_search"
    assert resp.arguments == {"query": "deep learning"}
    assert '"tool": "web_search"' in resp.format_tool_call()


def test_llm_response_invalid_raises():
    raw = "not a valid json response"
    with pytest.raises(ValidationError):
        LLMResponse.parse(raw)
