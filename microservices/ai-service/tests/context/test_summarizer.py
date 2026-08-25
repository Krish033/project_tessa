import uuid
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.pipeline.context.summerizer import Summarizer


@pytest.mark.anyio
@patch("app.pipeline.context.summerizer.db_session")
async def test_summarizer_run_stream(mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_db

    mock_llm = Mock()
    mock_llm.run_stream = AsyncMock(return_value=("", "Summary of conversation."))

    summarizer = Summarizer(mock_llm)
    conv_id = str(uuid.uuid4())
    last_msg_id = str(uuid.uuid4())
    messages = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
    ]

    result = await summarizer.summarize(messages, conv_id, last_msg_id)

    assert result == "Summary of conversation."
    assert mock_db.add.called


@pytest.mark.anyio
@patch("app.pipeline.context.summerizer.db_session")
async def test_summarizer_sync_run(mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_db

    mock_llm = Mock(spec=["run"])
    mock_llm.run.return_value = "Sync summary result."

    summarizer = Summarizer(mock_llm)
    conv_id = str(uuid.uuid4())
    last_msg_id = str(uuid.uuid4())
    messages = [{"role": "user", "content": "hello"}]

    result = await summarizer.summarize(messages, conv_id, last_msg_id)

    assert result == "Sync summary result."
    assert mock_db.add.called


@pytest.mark.anyio
async def test_summarizer_maybe_compact_below_trigger():
    summarizer = Summarizer(Mock())
    ctx = [{"role": "user", "content": "hi"}]
    retained, summary = await summarizer.maybe_compact(ctx, "conv_1", "old summary")
    assert retained == ctx
    assert summary == "old summary"
