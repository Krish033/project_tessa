import pytest
from unittest.mock import Mock, patch, MagicMock
from app.pipeline.context.data_pipeline import DataPipeline


@patch("app.pipeline.context.data_pipeline.db_session")
def test_data_pipeline_persist_message(mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value.__enter__.return_value = mock_db

    dp = DataPipeline()
    dp.persist_message("1fb369f7-4299-439d-8ec7-4775751a5f5b", "msg_1", "user", "hello")
    assert mock_db.add.called


@patch("app.pipeline.context.data_pipeline.db_session")
def test_data_pipeline_fetch_latest_summary_empty(mock_db_session):
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
    mock_db_session.return_value.__enter__.return_value = mock_db

    dp = DataPipeline()
    summary, last_id = dp.fetch_latest_summary("1fb369f7-4299-439d-8ec7-4775751a5f5b")
    assert summary is None
    assert last_id is None


@pytest.mark.anyio
@patch("app.pipeline.context.data_pipeline.db_session")
async def test_data_pipeline_load(mock_db_session):
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_db_session.return_value.__enter__.return_value = mock_db

    dp = DataPipeline()
    messages, summary = await dp.load("1fb369f7-4299-439d-8ec7-4775751a5f5b")
    assert messages == []
    assert summary == ""
