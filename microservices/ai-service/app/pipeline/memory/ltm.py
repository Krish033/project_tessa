import logging
import re
import uuid
from typing import List, Optional, Tuple
from app.core.database import db_session
from app.models.models import LongTermMemory
from app.pipeline.memory.embedder import Embedder

logger = logging.getLogger(__name__)


class LongTermMemoryManager:
    """Manages long-term user memories with validation, deduplication, and owner isolation."""

    def __init__(self):
        self.embedder = Embedder()

    # Rule patterns for detecting memory candidates (facts/preferences vs transient chat)
    MEMORY_PATTERNS = [
        (r"\bmy name is ([A-Za-z0-9_\s]+)", "user_name", 1.0),
        (r"\bi (?:prefer|like|use|love) ([A-Za-z0-9_\s]+) (?:for|in|as)", "user_preference", 0.8),
        (r"\bi work (?:as|at|with) ([A-Za-z0-9_\s]+)", "user_work", 0.7),
        (r"\bmy ([A-Za-z0-9_]+) is ([A-Za-z0-9_\s]+)", "user_fact", 0.7),
    ]

    NON_MEMORY_PATTERNS = [
        r"^(?:hi|hello|hey|greetings|bye|goodbye)\b",
        r"^(?:okay|ok|sure|thanks|thank you|got it|cool)\b",
        r"\b(?:weather|time|date|status|wifi|running|search|find)\b",
    ]

    def is_memory_candidate(self, content: str) -> bool:
        """Determine if a message content is a valid long-term memory candidate."""
        if not content or len(content.strip()) < 3:
            return False
        text = content.strip().lower()
        for pat in self.NON_MEMORY_PATTERNS:
            if re.search(pat, text):
                return False
        return True

    def extract_candidate(self, content: str) -> Optional[Tuple[str, str, float]]:
        """Extract (key, normalized_content, importance) from candidate text."""
        if not content or not content.strip() or not self.is_memory_candidate(content):
            return None
        text = content.strip()
        text_lower = text.lower()

        for pat, key_prefix, importance in self.MEMORY_PATTERNS:
            match = re.search(pat, text_lower)
            if match:
                value = match.group(1).strip()
                key = f"{key_prefix}_{re.sub(r'[^a-z0-9]', '_', value)}"
                return key, text, importance

        key = f"mem_{hash(text) & 0xFFFFFFFF}"
        return key, text, 0.8

    def process_message(self, role: str, content: str, owner_id: str = "default_user") -> Optional[LongTermMemory]:
        """Validate, extract, and persist long-term memory candidate if valid."""
        if role != "user" or not self.is_memory_candidate(content):
            return None
        return self.store_memory(owner_id=owner_id, content=content)

    def store_memory(
        self,
        owner_id: str,
        content: str,
        key: Optional[str] = None,
        importance: float = 0.5,
        action: str = "AUTO"  # AUTO / INSERT / UPDATE / IGNORE / MERGE
    ) -> Optional[LongTermMemory]:
        """Store or update a long-term memory with owner isolation and deduplication logic."""
        if not owner_id or not content or not content.strip():
            logger.warning("OPTIONAL MEMORY WARNING: Missing owner_id or content for memory storage.")
            return None

        if not key:
            candidate = self.extract_candidate(content)
            if not candidate:
                return None
            key, content, importance = candidate

        # Generate embedding for the content
        try:
            vector = self.embedder.embed(content)
        except Exception as e:
            logger.warning(f"OPTIONAL MEMORY WARNING: Embedding generation failed: {e}")
            vector = None

        try:
            with db_session() as db:
                existing = db.query(LongTermMemory).filter_by(
                    owner_id=owner_id,
                    key=key
                ).first()

                if existing:
                    # Update embedding if it was missing
                    if existing.embedding is None and vector is not None:
                        existing.embedding = vector
                        db.flush()

                    if action == "IGNORE" or existing.content == content:
                        db.expunge(existing)
                        return existing

                    if action in ("UPDATE", "AUTO", "MERGE"):
                        existing.content = content
                        existing.importance = max(existing.importance, importance)
                        if vector is not None:
                            existing.embedding = vector
                        db.flush()
                        db.expunge(existing)
                        return existing

                # INSERT new memory
                new_mem = LongTermMemory(
                    id=uuid.uuid4(),
                    owner_id=owner_id,
                    key=key,
                    content=content,
                    importance=importance,
                    embedding=vector
                )
                db.add(new_mem)
                db.flush()
                db.expunge(new_mem)
                return new_mem

        except Exception as e:
            logger.warning(f"OPTIONAL MEMORY FAILURE: Failed to persist memory for owner {owner_id}: {e}")
            return None

    def search_memories(self, owner_id: str, query_text: str, top_k: int = 5) -> List[LongTermMemory]:
        """Retrieve semantically relevant memories using cosine similarity on embeddings."""
        if not owner_id or not query_text:
            return []

        try:
            query_vector = self.embedder.embed(query_text)
        except Exception as e:
            logger.warning(f"OPTIONAL MEMORY WARNING: Query embedding failed: {e}")
            return []

        try:
            with db_session() as db:
                query = db.query(LongTermMemory).filter(
                    LongTermMemory.owner_id == owner_id,
                    LongTermMemory.embedding.isnot(None)
                )

                if db.bind.dialect.name == "postgresql":
                    query = query.order_by(LongTermMemory.embedding.cosine_distance(query_vector))
                else:
                    # SQLite fallback for unit tests
                    query = query.order_by(LongTermMemory.importance.desc())

                results = query.limit(top_k).all()
                for item in results:
                    db.expunge(item)
                return results
        except Exception as e:
            logger.warning(f"OPTIONAL MEMORY FAILURE: Vector search failed for owner {owner_id}: {e}")
            return []

    def get_memories(self, owner_id: str) -> List[LongTermMemory]:
        """Retrieve memories strictly isolated by owner_id."""
        if not owner_id:
            return []

        try:
            with db_session() as db:
                results = db.query(LongTermMemory).filter_by(
                    owner_id=owner_id
                ).order_by(LongTermMemory.importance.desc()).all()
                for item in results:
                    db.expunge(item)
                return results
        except Exception as e:
            logger.warning(f"OPTIONAL MEMORY FAILURE: Failed to load memories for owner {owner_id}: {e}")
            return []
