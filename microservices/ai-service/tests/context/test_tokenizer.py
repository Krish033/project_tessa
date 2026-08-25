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
