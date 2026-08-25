from app.pipeline.context.manager import ContextManager

def test_get_latest_user_prompt():
    manager = ContextManager()

    manager.ctx = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
        {"role": "user", "content": "what is Python?"},
    ]

    result = manager.get_latest_user_prompt()
    assert result == "what is Python?"

