import pytest
from unittest.mock import AsyncMock, Mock

from app.pipeline.context.manager import ContextManager


@pytest.mark.anyio
async def test_build():
    manager = ContextManager()

    manager.tr.aretrieve = AsyncMock(return_value=[])
    manager._fetch_ltm = AsyncMock(return_value=[])
    manager._maybe_compact = AsyncMock()

    manager._enforce_budget = Mock(
        side_effect=lambda messages: messages
    )

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


