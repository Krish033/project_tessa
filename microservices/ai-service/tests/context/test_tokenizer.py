from app.pipeline.context.tokenizor import Tokenizer, tokenizer


def test_tokenizer_count_empty():
    tok = Tokenizer()
    assert tok.count("") == 0
    assert tok.count(None) == 0


def test_tokenizer_count_text():
    tok = Tokenizer()
    count = tok.count("Hello, world! This is a test sentence.")
    assert count > 0


def test_tokenizer_count_messages():
    tok = Tokenizer()
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    count = tok.count_messages(messages)
    assert count > 0
    assert count >= tok.count("Hello") + tok.count("Hi there!")


def test_tokenizer_enforce_budget():
    tok = Tokenizer()
    tok.max_tokens = 20  # Artificial low budget
    messages = [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "first message that is very very long and exceeds"},
        {"role": "assistant", "content": "second message"},
        {"role": "user", "content": "third message"},
    ]
    trimmed = tok.enforce_budget(messages, headroom=5)
    assert len(trimmed) < 4
    assert trimmed[0]["role"] == "system"
