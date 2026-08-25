import re
from typing import List
import asyncio
from sqlalchemy import select
from app.core.database import db_session
from app.models.models import ToolModel
from app.pipeline.memory.embedder import Embedder


class ToolRetriever:

    def __init__(self):
        self.embedder = Embedder()

    
    def _retrieve_sync(self, query_embedding: list, user_prompt: str, top_k: int = 10) -> List[dict]:
        """Blocking DB vector search with intent-based core tool boosting."""

        with db_session() as db:
            
            stmt = (
                select(ToolModel)
                .where(ToolModel.embedding.isnot(None))
                .order_by(ToolModel.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )

            result = db.execute(stmt)
            vector_candidates = result.scalars().all()
            retrieved_names = {t.tool_name for t in vector_candidates}

            return [tool.to_dict() for tool in vector_candidates]


    # retrieve the tools from db (sync, safe to call outside async contexts)
    def retrieve(self, user_prompt: str, top_k: int = 10) -> List[dict]:

        if not user_prompt:
            return []

        query_embedding = self.embedder._embed_sync(user_prompt)
        return self._retrieve_sync(query_embedding, user_prompt, top_k)


       
    # async alias — fully non-blocking
    async def aretrieve(self, user_prompt: str, top_k: int = 10) -> List[dict]:
        if not user_prompt:
            return []
            
        query_embedding = await self.embedder.aembed(user_prompt)
        return await asyncio.to_thread(self._retrieve_sync, query_embedding, user_prompt, top_k)