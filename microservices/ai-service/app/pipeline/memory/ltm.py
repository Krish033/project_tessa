import asyncio
import hashlib
import logging
import uuid
from typing import List, Optional

from app.core.database import db_session
from app.models.models import LongTermMemory
from app.pipeline.memory.embedder import Embedder

logger = logging.getLogger(__name__)


class LongTermMemoryManager:
    """
    Manages persistence and semantic vector retrieval of long-term memories
    extracted directly by the LLM.
    """

    def __init__(self, embedder: Optional[Embedder] = None):
        self.embedder = embedder or Embedder()

    async def store_memory(
        self,
        owner_id: str,
        content: str,
        key: Optional[str] = None,
        importance: float = 0.5,
        action: str = "AUTO",
    ) -> Optional[LongTermMemory]:
        """Store or update a long-term memory with owner isolation and deduplication."""
        if not owner_id or not content or not content.strip():
            logger.warning("Missing owner_id or content for memory storage.")
            return None

        clean_content = content.strip()
        key = key or f"mem_{hashlib.sha256(clean_content.lower().encode('utf-8')).hexdigest()[:16]}"
        vector = await self._safe_embed(clean_content)

        return await asyncio.to_thread(
            self._upsert_memory, owner_id, key, clean_content, importance, vector, action
        )

    def _upsert_memory(
        self,
        owner_id: str,
        key: str,
        content: str,
        importance: float,
        vector: Optional[List[float]],
        action: str,
    ) -> Optional[LongTermMemory]:
        """Handle database session and upsert dispatch for long-term memory."""
        try:
            with db_session() as db:
                existing = db.query(LongTermMemory).filter_by(owner_id=owner_id, key=key).first()
                if existing:
                    return self._update_existing_memory(db, existing, content, importance, vector, action)
                return self._create_new_memory(db, owner_id, key, content, importance, vector)
        except Exception as e:
            logger.warning(f"Failed to persist memory for owner '{owner_id}': {e}")
            return None

    def _update_existing_memory(
        self,
        db,
        existing: LongTermMemory,
        content: str,
        importance: float,
        vector: Optional[List[float]],
        action: str,
    ) -> LongTermMemory:
        """Update an existing memory row according to action policy."""
        if existing.embedding is None and vector is not None:
            existing.embedding = vector

        if action in ("UPDATE", "AUTO", "MERGE") and existing.content != content:
            existing.content = content
            existing.importance = max(existing.importance, importance)
            if vector is not None:
                existing.embedding = vector

        db.flush()
        db.expunge(existing)
        return existing

    def _create_new_memory(
        self,
        db,
        owner_id: str,
        key: str,
        content: str,
        importance: float,
        vector: Optional[List[float]],
    ) -> LongTermMemory:
        """Insert and return a newly created memory record."""
        new_mem = LongTermMemory(
            id=uuid.uuid4(),
            owner_id=owner_id,
            key=key,
            content=content,
            importance=importance,
            embedding=vector,
        )
        db.add(new_mem)
        db.flush()
        db.expunge(new_mem)
        return new_mem

    async def search_memories(self, owner_id: str, query_text: str, top_k: int = 5) -> List[LongTermMemory]:
        """Retrieve semantically relevant memories using cosine similarity on embeddings."""
        if not owner_id or not query_text:
            return []

        vector = await self._safe_embed(query_text)
        if vector is None:
            return []

        return await asyncio.to_thread(self._search_db, owner_id, vector, top_k)

    async def search_memory_texts(self, owner_id: str, query_text: str, top_k: int = 5) -> List[str]:
        """Retrieve semantically relevant memory text strings."""
        memories = await self.search_memories(owner_id, query_text, top_k)
        return [m.content for m in memories if m and m.content]


    def _search_db(self, owner_id: str, vector: List[float], top_k: int) -> List[LongTermMemory]:
        """Execute vector search query in worker thread."""
        try:
            with db_session() as db:
                query = db.query(LongTermMemory).filter(
                    LongTermMemory.owner_id == owner_id,
                    LongTermMemory.embedding.isnot(None),
                )
                is_postgres = getattr(getattr(db, "bind", None), "dialect", None) and db.bind.dialect.name == "postgresql"
                order_by = LongTermMemory.embedding.cosine_distance(vector) if is_postgres else LongTermMemory.importance.desc()
                results = query.order_by(order_by).limit(top_k).all()
                for item in results:
                    db.expunge(item)
                return results
        except Exception as e:
            logger.warning(f"Vector search failed for owner '{owner_id}': {e}")
            return []

    async def get_memories(self, owner_id: str) -> List[LongTermMemory]:
        """Retrieve all memories strictly isolated by owner_id."""
        if not owner_id:
            return []

        return await asyncio.to_thread(self._get_db, owner_id)

    def _get_db(self, owner_id: str) -> List[LongTermMemory]:
        """Execute get memories query in worker thread."""
        try:
            with db_session() as db:
                results = (
                    db.query(LongTermMemory)
                    .filter_by(owner_id=owner_id)
                    .order_by(LongTermMemory.importance.desc())
                    .all()
                )
                for item in results:
                    db.expunge(item)
                return results
        except Exception as e:
            logger.warning(f"Failed to load memories for owner '{owner_id}': {e}")
            return []

    async def _safe_embed(self, text: str) -> Optional[List[float]]:
        """Safely generate an embedding vector or return None on failure."""
        try:
            res = self.embedder.embed(text)
            if asyncio.iscoroutine(res):
                return await res
            return res
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            return None
