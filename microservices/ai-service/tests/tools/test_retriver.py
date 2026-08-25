import pytest
from unittest.mock import Mock, AsyncMock
from app.pipeline.tools.meta.retriever import ToolRetriever


def test_retrieve_empty_prompt():
    tr = ToolRetriever()
    result = tr.retrieve("", top_k=5)
    assert result == []


@pytest.mark.anyio
async def test_aretrieve():
    retriever = ToolRetriever()
    retriever.embedder.embed = AsyncMock(
        return_value=[0.1, 0.2, 0.3]
    )
    retriever._retrieve_sync = Mock(
        return_value=[{"tool_name": "calculator"}]
    )

    result = await retriever.aretrieve("calculate 10 + 20")
    assert result == [{"tool_name": "calculator"}]
    retriever.embedder.embed.assert_awaited_once_with("calculate 10 + 20")
    retriever._retrieve_sync.assert_called_once_with(
        [0.1, 0.2, 0.3],
        "calculate 10 + 20",
        10
    )


def test_retrieve():
    retriever = ToolRetriever()
    retriever.embedder.embed = AsyncMock(
        return_value=[0.1, 0.2, 0.3]
    )
    retriever._retrieve_sync = Mock(
        return_value=[{"tool_name": "calculator"}]
    )

    result = retriever.retrieve("calculate 10 + 20")
    assert result == [{"tool_name": "calculator"}]
    retriever._retrieve_sync.assert_called_once_with(
        [0.1, 0.2, 0.3],
        "calculate 10 + 20",
        10
    )
