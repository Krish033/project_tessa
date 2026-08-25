from unittest.mock import Mock, AsyncMock, patch
from app.pipeline.llm import ReasoningStreamParser, QwenLLM


def test_parser_plain_content():
    content_chunks = []
    parser = ReasoningStreamParser(on_content=lambda c: content_chunks.append(c))

    parser.feed("Hello ")
    parser.feed("world!")
    parser.flush()

    assert parser.full_content == "Hello world!"
    assert parser.full_reasoning == ""
    assert "".join(content_chunks) == "Hello world!"


def test_parser_with_think_tags():
    reasoning_chunks = []
    content_chunks = []

    parser = ReasoningStreamParser(
        on_reasoning=lambda r: reasoning_chunks.append(r),
        on_content=lambda c: content_chunks.append(c),
    )

    parser.feed("<think>Let me think...</think>Final answer.")
    parser.flush()

    assert parser.full_reasoning == "Let me think..."
    assert parser.full_content == "Final answer."


def test_parser_split_chunks():
    parser = ReasoningStreamParser()

    parser.feed("<th")
    parser.feed("ink>Reasoning here</th")
    parser.feed("ink>Result")
    parser.flush()

    assert parser.full_reasoning == "Reasoning here"
    assert parser.full_content == "Result"


@patch("app.pipeline.llm.ollama.AsyncClient")
@patch("app.pipeline.llm.ollama.Client")
def test_qwen_llm_options(mock_client, mock_async_client):
    llm = QwenLLM(model_name="test-model")
    opts = llm.get_options()
    assert "temperature" in opts
    assert opts["temperature"] == 0.0
    assert "num_ctx" in opts


@patch("app.pipeline.llm.ollama.AsyncClient")
@patch("app.pipeline.llm.ollama.Client")
def test_qwen_llm_run_sync(mock_client_cls, mock_async_client_cls):
    mock_client = Mock()
    mock_client.chat.return_value = {"message": {"content": "Sync response"}}
    mock_client_cls.return_value = mock_client

    llm = QwenLLM(model_name="test-model")
    res = llm.run([{"role": "user", "content": "hi"}])
    assert res == "Sync response"
