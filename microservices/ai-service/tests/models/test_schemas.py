import pytest
from pydantic import ValidationError
from app.models.schemas import Fact, ChatMessage, ToolCall, LLMResponse


def test_fact_schema():
    f = Fact(content="User prefers Python", key="pref", importance=0.8)
    assert f.content == "User prefers Python"
    assert f.key == "pref"
    assert f.importance == 0.8


def test_chat_message_schema():
    msg = ChatMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"


def test_tool_call_schema():
    tc = ToolCall(tool="web_search", arguments={"query": "python"})
    assert tc.tool == "web_search"
    assert tc.arguments == {"query": "python"}


def test_llm_response_valid():
    raw = '{"action": "final", "answer": "Hello World", "ltm": ["fact1"]}'
    resp = LLMResponse.parse(raw)
    assert resp.is_final is True
    assert resp.is_tool is False
    assert resp.answer == "Hello World"
    assert resp.ltm == ["fact1"]


def test_llm_response_invalid_schema_raises():
    raw = '{"action": "invalid_action_type"}'
    with pytest.raises(ValidationError):
        LLMResponse.parse(raw)


def test_llm_response_invalid_json_raises():
    raw = "not a valid json"
    with pytest.raises(ValidationError):
        LLMResponse.parse(raw)
