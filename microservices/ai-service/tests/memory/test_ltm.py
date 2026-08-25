import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.pipeline.memory.ltm import LongTermMemoryManager


@pytest.mark.anyio
async def test_store_memory_invalid_input():
    ltm = LongTermMemoryManager()
    assert await ltm.store_memory(owner_id="", content="Some fact") is None
    assert await ltm.store_memory(owner_id="user_123", content="") is None
    assert await ltm.store_memory(owner_id="user_123", content="   ") is None


@pytest.mark.anyio
@patch("app.pipeline.memory.ltm.db_session")
async def test_store_memory_new_with_generated_key(mock_db_session):
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    mock_db_session.return_value.__enter__.return_value = mock_db

    ltm = LongTermMemoryManager()
    ltm.embedder.embed = AsyncMock(return_value=[0.1] * 768)

    mem = await ltm.store_memory(
        owner_id="user_123",
        content="My favorite editor is Neovim",
    )

    assert mem is not None
    assert mem.owner_id == "user_123"
    assert mem.content == "My favorite editor is Neovim"
    assert mem.key.startswith("mem_")
    assert mock_db.add.called


@pytest.mark.anyio
@patch("app.pipeline.memory.ltm.db_session")
async def test_store_memory_update_existing(mock_db_session):
    mock_existing = MagicMock()
    mock_existing.content = "Old content"
    mock_existing.importance = 0.5
    mock_existing.embedding = None

    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_existing
    mock_db_session.return_value.__enter__.return_value = mock_db

    ltm = LongTermMemoryManager()
    ltm.embedder.embed = AsyncMock(return_value=[0.2] * 768)

    mem = await ltm.store_memory(
        owner_id="user_123",
        content="Updated preference for Neovim",
        key="editor_pref",
        importance=0.9,
    )

    assert mem is mock_existing
    assert mock_existing.content == "Updated preference for Neovim"
    assert mock_existing.importance == 0.9
    assert mock_db.flush.called


@pytest.mark.anyio
@patch("app.pipeline.memory.ltm.db_session")
async def test_get_memories(mock_db_session):
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_db_session.return_value.__enter__.return_value = mock_db

    ltm = LongTermMemoryManager()
    results = await ltm.get_memories("user_123")
    assert results == []


@pytest.mark.anyio
@patch("app.pipeline.memory.ltm.db_session")
async def test_search_memories(mock_db_session):
    mock_db = MagicMock()
    mock_db.bind.dialect.name = "postgresql"
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    mock_db_session.return_value.__enter__.return_value = mock_db

    ltm = LongTermMemoryManager()
    ltm.embedder.embed = AsyncMock(return_value=[0.1] * 768)

    results = await ltm.search_memories(owner_id="user_123", query_text="editor")
    assert results == []
