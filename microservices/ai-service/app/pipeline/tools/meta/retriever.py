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

    def _get_essential_tool_names(self, user_prompt: str) -> set[str]:
        """Detect intent keywords to guarantee essential tools are included."""
        essential = set()
        prompt_lower = user_prompt.lower()

        # URL / Web intent
        if re.search(r"https?://|\bwww\.|online|website|url|link\b", prompt_lower):
            essential.update(["fetch_url", "browser", "web_search"])
        elif re.search(r"\bsearch|google|news|find|lookup\b", prompt_lower):
            essential.update(["web_search", "news_search", "fetch_url"])

        # File / Code intent
        if re.search(r"\bfile|folder|code|dir|read|edit|write|search_files\b", prompt_lower):
            essential.update(["read_file", "write_file", "edit_file", "search_files"])

        # Command / OS intent
        if re.search(r"\bcommand|terminal|bash|shell|run|os|system|specs|ram|cpu\b", prompt_lower):
            essential.update(["execute_command", "get_os_info"])

        return essential

    def _retrieve_sync(self, query_embedding: list, user_prompt: str, top_k: int = 10) -> List[dict]:
        """Blocking DB vector search with intent-based core tool boosting."""
        essential_names = self._get_essential_tool_names(user_prompt)

        with db_session() as db:
            # 1. Fetch vector nearest tools
            stmt = (
                select(ToolModel)
                .where(ToolModel.embedding.isnot(None))
                .order_by(ToolModel.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
            result = db.execute(stmt)
            vector_candidates = result.scalars().all()
            retrieved_names = {t.tool_name for t in vector_candidates}

            # 2. Fetch any essential intent-matched tools missing from vector top-k
            missing_essential = essential_names - retrieved_names
            essential_tools = []
            if missing_essential:
                stmt_ess = select(ToolModel).where(ToolModel.tool_name.in_(missing_essential))
                essential_tools = db.execute(stmt_ess).scalars().all()

            # 3. Combine essential + vector tools (deduplicated)
            combined = essential_tools + [t for t in vector_candidates if t.tool_name not in missing_essential]
            return [tool.to_dict() for tool in combined]

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