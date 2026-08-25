import pytest
from unittest.mock import AsyncMock
from app.pipeline.context.manager import ContextManager


@pytest.mark.anyio
async def test_build():
    manager = ContextManager()

    manager.tr.aretrieve = AsyncMock(return_value=[])
    manager.ltm.search_memory_texts = AsyncMock(return_value=[])

    manager.ctx = [
        {
            "id": "1",
            "role": "user",
            "content": "What is Python?"
        }
    ]

    result = await manager.build()

    assert result[0]["role"] == "system"
    assert "Available Tools:" in result[0]["content"]

    assert result[1] == {
        "role": "user",
        "content": "What is Python?"
    }
