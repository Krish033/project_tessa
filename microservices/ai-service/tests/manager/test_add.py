from unittest.mock import Mock
from app.pipeline.context.manager import ContextManager


def test_add():
    manager = ContextManager()
    manager._persist_message = Mock()

    manager.add("user", "hello")

    assert len(manager.ctx) == 1
    assert manager.ctx[0]["role"] == "user"
    assert manager.ctx[0]["content"] == "hello"

    manager._persist_message.assert_called_once_with(
        manager.ctx[0]["id"],
        "user",
        "hello"
    )
