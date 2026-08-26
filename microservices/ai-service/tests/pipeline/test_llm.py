from unittest.mock import Mock, patch
from app.pipeline.llm import QwenLLM, OPTIONS
from app.core.config import config


def test_qwen_llm_options():
    assert OPTIONS["temperature"] == 0.0
    assert OPTIONS["num_ctx"] == config.OLLAMA_NUM_CTX
    assert OPTIONS["num_thread"] == config.OLLAMA_NUM_THREAD
    assert OPTIONS["num_predict"] == config.OLLAMA_NUM_PREDICT


@patch("app.pipeline.llm.ollama.Client")
def test_qwen_llm_run_sync(mock_client_cls):
    mock_client = Mock()
    mock_client.chat.return_value = {"message": {"content": "Sync response"}}
    mock_client_cls.return_value = mock_client

    llm = QwenLLM(model_name="test-model")
    res = llm.run([{"role": "user", "content": "hi"}])
    assert res == "Sync response"
    mock_client.chat.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "hi"}],
        options=OPTIONS,
        think=False,
        keep_alive=-1,
    )
