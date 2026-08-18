import os
import re
from typing import List, Optional

try:
    from transformers import AutoTokenizer
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False


class Tokenizer:
    """
    Counts tokens for context budget management.
    Uses HuggingFace tokenizer when available, otherwise falls back
    to a simple char/4 heuristic (good enough for budget decisions).
    """

    _hf_tokenizer = None
    _init_attempted = False

    def __init__(self):
        # Read max tokens from env; margin is applied by ContextManager
        self.max_tokens = int(os.getenv("MAX_MODEL_TOKENS", "32768"))
        if not Tokenizer._init_attempted:
            Tokenizer._init_attempted = True
            self._try_load_hf()

    def _try_load_hf(self) -> None:
        if not _TRANSFORMERS_AVAILABLE:
            return
        for model_id in ["Qwen/Qwen2.5-1.5B", "gpt2"]:
            try:
                Tokenizer._hf_tokenizer = AutoTokenizer.from_pretrained(
                    model_id, local_files_only=True, trust_remote_code=True
                )
                return
            except Exception:
                continue

    def count(self, text: str) -> int:
        """Return approximate token count for text."""
        if not text:
            return 0
        if Tokenizer._hf_tokenizer is not None:
            try:
                return len(Tokenizer._hf_tokenizer.encode(text, add_special_tokens=False))
            except Exception:
                pass
        # Fallback: ~4 chars per token (industry standard approximation)
        return max(1, len(text) // 4)

    def count_messages(self, messages: List[dict]) -> int:
        """Count total tokens across a list of message dicts (role + content)."""
        total = 0
        for msg in messages:
            total += self.count(msg.get("role", ""))
            total += self.count(msg.get("content", ""))
        return total


# Module-level singleton
tokenizer = Tokenizer()