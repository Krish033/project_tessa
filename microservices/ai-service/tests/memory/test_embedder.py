import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.pipeline.memory.embedder import Embedder


def test_embed_sync():
    embedder = Embedder()
    embedder.client.embed = Mock(
        return_value={"embeddings": [[0.1, 0.2, 0.3]]}
    )

    result = embedder._embed_sync("hello")
    assert result == [0.1, 0.2, 0.3]
    embedder.client.embed.assert_called_once_with(
        model="nomic-embed-text", input="hello"
    )


@pytest.mark.anyio
async def test_aembed():
    embedder = Embedder()
    embedder.async_client.embed = AsyncMock(
        return_value={"embeddings": [[0.4, 0.5, 0.6]]}
    )

    result = await embedder.aembed("hello")
    assert result == [0.4, 0.5, 0.6]
    embedder.async_client.embed.assert_awaited_once_with(
        model="nomic-embed-text", input="hello"
    )


def test_embed_wrapper():
    embedder = Embedder()
    embedder._embed_sync = Mock(return_value=[0.1, 0.2, 0.3])

    res = embedder.embed("test")
    assert res == [0.1, 0.2, 0.3]
