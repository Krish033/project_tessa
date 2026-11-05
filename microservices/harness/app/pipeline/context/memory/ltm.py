import uuid
import hashlib
from typing import List, Optional, Union

from app.core.database import db_session
from app.models.models import LongTermMemory
from app.models.schemas import Fact
from app.pipeline.context.memory.embedder import Embedder


class LongTermMemoryManager:
    """Manages creation, updates, and vector retrieval of long-term memories."""

    def __init__(self, embedder: Optional[Embedder] = None):
        self.embedder = embedder or Embedder()


    # Get Memories from DB
    async def get_memories(
        self,
        owner_id: str,
        query: Optional[str] = None,
        top_k: int = 5,
    ) -> List[LongTermMemory]:
        """Retrieve memories for an owner, optionally filtered/ranked by semantic query."""
        if not owner_id:
            return []

        embedding = await self.embedder.embed(query) if query else None

        with db_session() as db:
            q = db.query(LongTermMemory).filter_by(owner_id=owner_id)

            if embedding:
                is_pg = getattr(getattr(db, "bind", None), "dialect", None) and db.bind.dialect.name == "postgresql"
                order_clause = LongTermMemory.embedding.cosine_distance(embedding) if is_pg else LongTermMemory.importance.desc()
                return q.filter(LongTermMemory.embedding.isnot(None)).order_by(order_clause).limit(top_k).all()

            return q.order_by(LongTermMemory.importance.desc()).limit(top_k).all()


    #Create Memory in DB
    async def create_memory(
        self,
        owner_id: str,
        content: str,
        key: Optional[str] = None,
        importance: float = 0.5,
    ) -> Optional[LongTermMemory]:
        """Create a new long-term memory."""
        if not owner_id or not content.strip():
            return None

        clean_text = content.strip()
        memory_key = key or f"mem_{hashlib.sha256(clean_text.lower().encode()).hexdigest()[:16]}"
        embedding = await self.embedder.embed(clean_text)

        with db_session() as db:
            memory = LongTermMemory(
                id=uuid.uuid4(),
                owner_id=owner_id,
                key=memory_key,
                content=clean_text,
                importance=importance,
                embedding=embedding,
            )
            db.add(memory)
            db.flush()
            return memory


    # Update Memory in DB
    async def update_memory(
        self,
        owner_id: str,
        key: str,
        content: str,
        importance: float = 0.5,
    ) -> Optional[LongTermMemory]:
        """Update an existing long-term memory."""
        if not owner_id or not key or not content.strip():
            return None

        clean_text = content.strip()
        embedding = await self.embedder.embed(clean_text)

        with db_session() as db:
            memory = db.query(LongTermMemory).filter_by(owner_id=owner_id, key=key).first()
            if not memory:
                return None
            memory.content = clean_text
            memory.importance = max(memory.importance, importance)
            if embedding:
                memory.embedding = embedding
            db.flush()
            return memory

        
    #Upsert Memory in DB
    async def store_memory(
        self,
        owner_id: str,
        content: Union[str, Fact],
        key: Optional[str] = None,
        importance: float = 0.5,
    ) -> Optional[LongTermMemory]:
        """Upsert memory: updates if key exists, otherwise creates a new record."""
        if not owner_id or not content:
            return None

        text = content.content if isinstance(content, Fact) else str(content).strip()
        if not text:
            return None

        mem_key = (content.key if isinstance(content, Fact) and content.key else key) or f"mem_{hashlib.sha256(text.lower().encode()).hexdigest()[:16]}"
        mem_importance = content.importance if isinstance(content, Fact) else importance

        with db_session() as db:
            exists = db.query(LongTermMemory).filter_by(owner_id=owner_id, key=mem_key).first()

        if exists:
            return await self.update_memory(owner_id, mem_key, text, mem_importance)
        return await self.create_memory(owner_id, text, mem_key, mem_importance)
