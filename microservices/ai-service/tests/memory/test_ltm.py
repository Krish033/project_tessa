import pytest
from unittest.mock import Mock, patch, MagicMock
from app.pipeline.memory.ltm import LongTermMemoryManager


def test_is_memory_candidate():
    ltm = LongTermMemoryManager()
    assert ltm.is_memory_candidate("My name is John Doe") is True
    assert ltm.is_memory_candidate("I prefer dark mode in IDE") is True
    assert ltm.is_memory_candidate("I work as a software engineer") is True

    # Non-memory candidates
    assert ltm.is_memory_candidate("hi") is False
    assert ltm.is_memory_candidate("okay") is False
    assert ltm.is_memory_candidate("what is the weather today?") is False
    assert ltm.is_memory_candidate("") is False


def test_extract_candidate():
    ltm = LongTermMemoryManager()
    cand1 = ltm.extract_candidate("My name is Alice")
    assert cand1 is not None
    assert "user_name" in cand1[0]
    assert cand1[2] == 1.0

    cand2 = ltm.extract_candidate("I prefer Python for backend development")
    assert cand2 is not None
    assert "user_preference" in cand2[0]


def test_process_message_non_user_ignored():
    ltm = LongTermMemoryManager()
    res = ltm.process_message(role="assistant", content="My name is Alice")
    assert res is None


@patch("app.pipeline.memory.ltm.db_session")
def test_store_memory_new(mock_db_session):
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    mock_db_session.return_value.__enter__.return_value = mock_db

    ltm = LongTermMemoryManager()
    ltm.embedder.embed = Mock(return_value=[0.1] * 768)

    mem = ltm.store_memory(
        owner_id="user_123",
        content="My favorite editor is Neovim",
    )

    assert mem is not None
    assert mem.owner_id == "user_123"
    assert mem.content == "My favorite editor is Neovim"
    assert mock_db.add.called


@patch("app.pipeline.memory.ltm.db_session")
def test_get_memories(mock_db_session):
    mock_db = MagicMock()
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_db_session.return_value.__enter__.return_value = mock_db

    ltm = LongTermMemoryManager()
    results = ltm.get_memories("user_123")
    assert results == []
