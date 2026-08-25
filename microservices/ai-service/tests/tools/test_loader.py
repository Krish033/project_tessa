from unittest.mock import patch, MagicMock
from app.pipeline.tools.meta.registry import ToolRegistry
from app.pipeline.tools.loader import load_tools


def test_load_tools_registers_all_tools():
    registry = ToolRegistry()
    load_tools(registry, sync_db=False)

    all_tools = registry.get_all()
    assert len(all_tools) > 10

    assert registry.exists("execute_command")
    assert registry.exists("get_os_info")
    assert registry.exists("web_search")
    assert registry.exists("fetch_url")
    assert registry.exists("read_file")
    assert registry.exists("write_file")
    assert registry.exists("edit_file")


@patch("app.pipeline.tools.loader.db_session")
@patch("app.pipeline.tools.loader.Embedder")
def test_sync_tools_to_db(mock_embedder_cls, mock_db_session):
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [0.1] * 768
    mock_embedder_cls.return_value = mock_embedder

    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    mock_db_session.return_value.__enter__.return_value = mock_db

    registry = ToolRegistry()
    load_tools(registry, sync_db=True)

    # Should have called db.add for registered tools
    assert mock_db.add.called
