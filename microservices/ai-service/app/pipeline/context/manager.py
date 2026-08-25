import uuid
import json
import asyncio
from typing import List, Dict, Optional

from app.pipeline.prompt import SYSTEM_PROMPT
from app.pipeline.tools.meta.retriever import ToolRetriever
from app.pipeline.context.tokenizor import tokenizer
from app.pipeline.context.summerizer import Summarizer
from app.pipeline.context.data_pipeline import DataPipeline
from app.pipeline.memory.ltm import LongTermMemoryManager


class ContextManager:
    """
    Coordinates short-term in-memory context, DB persistence via DataPipeline,
    tool & memory retrieval, token budgeting, and summarization.
    """

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        llm=None,
        data_pipeline: Optional[DataPipeline] = None,
        summarizer: Optional[Summarizer] = None,
        retriever: Optional[ToolRetriever] = None,
        ltm: Optional[LongTermMemoryManager] = None,
    ):
        self.conversation_id = conversation_id or "1fb369f7-4299-439d-8ec7-4775751a5f5b"
        self.llm = llm
        self.data_pipeline = data_pipeline or DataPipeline()
        self.summarizer = summarizer or (Summarizer(llm) if llm else None)
        self.tr = retriever or ToolRetriever()
        self.ltm = ltm or LongTermMemoryManager()

        # In-memory context: list of {"id", "role", "content"} dicts
        self.ctx: List[dict] = []
        self.loaded_summary: str = ""

    async def load(self) -> None:
        """Load conversation state and summary from database."""
        self.ctx, self.loaded_summary = await self.data_pipeline.load(self.conversation_id)

    def add(self, role: str, content: str) -> None:
        """Add a message to in-memory context and persist it to the database."""
        msg_id = str(uuid.uuid4())
        self.ctx.append({"id": msg_id, "role": role, "content": content})
        self.data_pipeline.persist_message(self.conversation_id, msg_id, role, content)

    def get_latest_user_prompt(self) -> str:
        """Get the most recent user prompt from in-memory context."""
        for msg in reversed(self.ctx):
            if msg.get("role") == "user" and msg.get("content"):
                return msg["content"]
        return ""

    async def build(self) -> List[Dict[str, str]]:
        """
        Build the ChatML message list for LLM inference:
          1. Retrieve tools and relevant LTM memories concurrently.
          2. Compose system prompt (with summary + LTM facts).
          3. Compact message history if trigger threshold is reached.
          4. Convert context to ChatML messages and enforce token budget.
        """
        user_prompt = self.get_latest_user_prompt()

        # Step 1: Retrieve tools and LTM facts concurrently
        async def _empty(): return []
        tools_task = asyncio.create_task(self.tr.aretrieve(user_prompt) if user_prompt else _empty())
        ltm_task = asyncio.create_task(self.ltm.search_memory_texts(self.conversation_id, user_prompt) if user_prompt else _empty())
        tools, ltm_facts = await asyncio.gather(tools_task, ltm_task)

        tools_str = json.dumps(tools, indent=2) if tools else "[]"

        # Step 2: Compose system prompt
        system_content = SYSTEM_PROMPT
        if self.loaded_summary:
            system_content = f"Previous conversation summary:\n{self.loaded_summary}\n\n" + system_content
        if ltm_facts:
            facts_str = "\n".join(f"- {f}" for f in ltm_facts)
            system_content = f"Relevant long-term memory:\n{facts_str}\n\n" + system_content
        system_content += f"\n\nAvailable Tools:\n{tools_str}"

        # Step 3: Compact if summarizer is available
        if self.summarizer:
            self.ctx, self.loaded_summary = await self.summarizer.maybe_compact(
                self.ctx, self.conversation_id, self.loaded_summary
            )

        # Step 4: Build final ChatML message list
        messages = [{"role": "system", "content": system_content}]
        for msg in self.ctx:
            role = msg.get("role", "user")
            if role in ("output", "tool"):
                role = "user"
            messages.append({"role": role, "content": msg.get("content", "")})

        # Step 5: Enforce token budget
        return tokenizer.enforce_budget(messages)
