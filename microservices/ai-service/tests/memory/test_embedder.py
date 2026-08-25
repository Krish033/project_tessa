import pytest
from unittest.mock import AsyncMock
from app.pipeline.memory.embedder import Embedder


@pytest.mark.anyio
async def test_embed_async():
    embedder = Embedder()
    embedder.client.embed = AsyncMock(
        return_value={"embeddings": [[0.1, 0.2, 0.3]]}
    )

    result = await embedder.embed("hello")
    assert result == [0.1, 0.2, 0.3]
    embedder.client.embed.assert_awaited_once_with(
        model="nomic-embed-text", input="hello"
    )


@pytest.mark.anyio
async def test_embed_custom_model():
    embedder = Embedder(model="custom-embed-model")
    embedder.client.embed = AsyncMock(
        return_value={"embeddings": [[0.4, 0.5, 0.6]]}
    )

    result = await embedder.embed("testing custom model")
    assert result == [0.4, 0.5, 0.6]
    embedder.client.embed.assert_awaited_once_with(
        model="custom-embed-model", input="testing custom model"
    )
