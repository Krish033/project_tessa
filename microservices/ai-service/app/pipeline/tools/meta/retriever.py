import asyncio
from typing import List, Optional
from sqlalchemy import select
from app.core.database import db_session
from app.models.models import ToolModel
from app.pipeline.memory.embedder import Embedder


class ToolRetriever:

    def __init__(self, embedder: Optional[Embedder] = None):
        self.embedder = embedder or Embedder()

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
            return [tool.to_dict() for tool in vector_candidates]

    async def aretrieve(self, user_prompt: str, top_k: int = 10) -> List[dict]:
        """Async retrieve tools from DB using non-blocking vector search."""
        if not user_prompt:
            return []

        res = self.embedder.embed(user_prompt)
        query_embedding = await res if asyncio.iscoroutine(res) else res
        return await asyncio.to_thread(self._retrieve_sync, query_embedding, user_prompt, top_k)

    def retrieve(self, user_prompt: str, top_k: int = 10) -> List[dict]:
        """Sync retrieve tools from DB (safe for synchronous callers)."""
        if not user_prompt:
            return []

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                res = self.embedder.embed(user_prompt)
                query_embedding = pool.submit(asyncio.run, res).result() if asyncio.iscoroutine(res) else res
        except RuntimeError:
            res = self.embedder.embed(user_prompt)
            query_embedding = asyncio.run(res) if asyncio.iscoroutine(res) else res

        return self._retrieve_sync(query_embedding, user_prompt, top_k)