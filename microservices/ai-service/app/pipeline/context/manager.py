import uuid
import json
from typing import List, Dict, Optional

from app.core.prompt import SYSTEM_PROMPT
from app.pipeline.tools.meta.retriever import ToolRetriever
from app.pipeline.context.tokenizor import tokenizer
from app.pipeline.context.summerizer import Summarizer
from app.models.data_pipeline import DataPipeline
from app.pipeline.context.memory.ltm import LongTermMemoryManager


class ContextManager:
    """Coordinates conversation context, tools, and token budget for LLM inference."""

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

        self.ctx: List[dict] = []
        self.loaded_summary: str = ""


    async def load(self) -> None:
        self.ctx, self.loaded_summary = await self.data_pipeline.load(self.conversation_id)


    def add(self, role: str, content: str) -> None:
        msg_id = str(uuid.uuid4())
        self.ctx.append({"id": msg_id, "role": role, "content": content})
        self.data_pipeline.persist_message(self.conversation_id, msg_id, role, content)


    def get_latest_user_prompt(self) -> str:
        for msg in reversed(self.ctx):
            if msg.get("role") == "user" and msg.get("content"):
                return msg["content"]
        return ""



    async def build(self) -> List[Dict[str, str]]:
        prompt = self.get_latest_user_prompt()

        # 1. Retrieve tools and relevant memories
        tools = await self.tr.aretrieve(prompt) if prompt else []
        ltm_records = await self.ltm.get_memories(self.conversation_id, query=prompt) if prompt else []
        ltm_facts = [m.content for m in ltm_records if getattr(m, "content", None)]

        # 2. Compose system message
        system_parts = []
        if self.loaded_summary:
            system_parts.append(f"Previous conversation summary:\n{self.loaded_summary}")
        if ltm_facts:
            system_parts.append("Relevant long-term memory:\n" + "\n".join(f"- {f}" for f in ltm_facts))
        system_parts.append(SYSTEM_PROMPT)
        system_parts.append(f"Available Tools:\n{json.dumps(tools, indent=2) if tools else '[]'}")

        # 3. Compact history if needed
        if self.summarizer:
            self.ctx, self.loaded_summary = await self.summarizer.maybe_compact(
                self.ctx, self.conversation_id, self.loaded_summary
            )

        # 4. Assemble ChatML messages
        messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
        for msg in self.ctx:
            role = "user" if msg.get("role") in ("output", "tool") else msg.get("role", "user")
            messages.append({"role": role, "content": msg.get("content", "")})

        return tokenizer.enforce_budget(messages)
