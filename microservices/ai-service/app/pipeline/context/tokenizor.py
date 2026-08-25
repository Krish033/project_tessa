import os
import logging
from typing import List, Optional, Any

logger = logging.getLogger(__name__)

try:
    from tokenizers import Tokenizer as HFTokenizer
    _TOKENIZERS_AVAILABLE = True
except ImportError:
    _TOKENIZERS_AVAILABLE = False


class Tokenizer:
    """
    Counts tokens for context budget management.
    Uses the fast Qwen tokenizer via HuggingFace tokenizers when available,
    otherwise falls back to a character-based heuristic (~4 chars/token).
    """

    _hf_tokenizer: Optional[Any] = None
    _init_attempted: bool = False

    def __init__(self, model_id: str = "Qwen/Qwen2.5-1.5B"):
        self.model_id = model_id
        self.max_tokens = int(os.getenv("MAX_MODEL_TOKENS", "32768"))
        if not Tokenizer._init_attempted:
            Tokenizer._init_attempted = True
            self._load_tokenizer()

    def _load_tokenizer(self) -> None:
        if not _TOKENIZERS_AVAILABLE:
            return
        try:
            Tokenizer._hf_tokenizer = HFTokenizer.from_pretrained(self.model_id)
        except Exception as e:
            logger.debug(f"Could not load '{self.model_id}' tokenizer, using fallback: {e}")

    def count(self, text: Optional[str]) -> int:
        """Return token count for text."""
        if not text:
            return 0

        if Tokenizer._hf_tokenizer is not None:
            try:
                return len(Tokenizer._hf_tokenizer.encode(text).ids)
            except Exception:
                pass

        # Fallback: ~4 chars per token approximation
        return max(1, len(text) // 4)

    def count_messages(self, messages: List[dict]) -> int:
        """Count total tokens across a list of message dicts (role + content)."""
        total = 0
        for msg in messages:
            total += self.count(msg.get("role", ""))
            total += self.count(msg.get("content", ""))
        return total

    def enforce_budget(self, messages: List[dict], headroom: int = 10_000) -> List[dict]:
        """Drop oldest non-system messages until total tokens fit within model budget."""
        budget = self.max_tokens - headroom
        while True:
            total = self.count_messages(messages)
            if total <= budget:
                break
            # Drop the oldest non-system message
            for i, m in enumerate(messages):
                if m.get("role") != "system":
                    messages.pop(i)
                    break
            else:
                break  # Only system prompt left
        return messages


# Module-level singleton
tokenizer = Tokenizer()