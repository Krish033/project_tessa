import uuid
import json
import asyncio
from typing import List, Dict, Optional

from sqlalchemy import select

from app.core.database import db_session
from app.models.models import Message, ContextSummary
from app.pipeline.prompt import SYSTEM_PROMPT
from app.pipeline.tools.meta.retriever import ToolRetriever
from app.pipeline.context.tokenizor import tokenizer
from app.pipeline.memory.ltm import LongTermMemoryManager


# After 10 messages in ctx, compress the oldest 7 into a summary,
# keeping the most recent 3 as live context.
COMPACTION_TRIGGER = 10   # compress when ctx hits this many messages
MESSAGES_TO_COMPRESS = 7  # how many oldest messages to summarize
MESSAGES_TO_KEEP = 3      # how many most-recent messages to retain after summary

# Stay 10 000 tokens below the model max
TOKEN_HEADROOM = 10_000


class ContextManager:
    """ Manages in-memory short-term context with:
      - DB persistence (messages + summaries)
      - Token budget enforcement (10k below model max)
      - Auto-compaction: every 10 messages, summarize the oldest 7
      - Conversation loading: restore from latest summary + remaining messages
    """

    def __init__(self, conversation_id: Optional[str] = None, llm=None):
        # Lazy import to avoid circular dependency at module load time
        from app.pipeline.context.summerizer import Summarizer

        self.conversation_id = conversation_id or "1fb369f7-4299-439d-8ec7-4775751a5f5b"
        self.llm = llm
        self.summarizer: Optional[Summarizer] = Summarizer(llm) if llm else None
        self.tr = ToolRetriever()
        self._ltm = LongTermMemoryManager()

        # In-memory context: list of {"id", "role", "content"} dicts
        self.ctx: List[dict] = []

        # Summary text prepended to system prompt (from latest DB summary)
        self.loaded_summary: str = ""

 

    async def load(self) -> None:

        """ Load conversation from DB:
          1. Get the latest ContextSummary row (if any).
          2. Load only messages *after* last_message_id.
          3. Store summary text to prepend to system prompt.
        """

        self.ctx = []
        self.loaded_summary = ""

        latest_summary, after_id = await asyncio.to_thread(self._fetch_latest_summary)

        if latest_summary:
            self.loaded_summary = latest_summary

        messages = await asyncio.to_thread(self._fetch_messages_after, after_id)
        self.ctx = messages




    # Fetch latest summary from DB
    def _fetch_latest_summary(self):
        """Return (summary_text, last_message_id) from the most recent summary row."""
        with db_session() as db:
            row = (
                db.query(ContextSummary)
                .filter_by(conversation_id=self.conversation_id)
                .order_by(ContextSummary.created_at.desc())
                .first()
            )
            if row:
                return row.summary, str(row.last_message_id) if row.last_message_id else None
            return None, None



    # Fetch messages after the given message id
    def _fetch_messages_after(self, after_message_id: Optional[str]) -> List[dict]:
        """Return messages after the given message id (or all if None)."""
        with db_session() as db:
            if after_message_id:
                # Get the created_at of the boundary message
                boundary = db.query(Message).filter_by(id=after_message_id).first()
                if boundary:
                    rows = (
                        db.query(Message)
                        .filter(
                            Message.conversation_id == self.conversation_id,
                            Message.created_at > boundary.created_at,
                        )
                        .order_by(Message.created_at)
                        .all()
                    )
                else:
                    rows = []
            else:
                rows = (
                    db.query(Message)
                    .filter_by(conversation_id=self.conversation_id)
                    .order_by(Message.created_at)
                    .all()
                )
            return [
                {"id": str(m.id), "role": m.role, "content": m.content}
                for m in rows
            ]

    
    # Add messages to the context manager
    def add(self, role: str, content: str) -> None:
        """Add a message to in-memory ctx and persist it to DB."""
        msg_id = str(uuid.uuid4())
        self.ctx.append({"id": msg_id, "role": role, "content": content})
        self._persist_message(msg_id, role, content)



    # Persist messages in DB
    def _persist_message(self, msg_id: str, role: str, content: str) -> None:
        """ Persist messages in DB """

        token_count = tokenizer.count(content)
        try:
            try:
                conv_uuid = uuid.UUID(str(self.conversation_id))
            except ValueError:
                conv_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(self.conversation_id))

            try:
                m_uuid = uuid.UUID(str(msg_id))
            except ValueError:
                m_uuid = uuid.uuid4()

            with db_session() as db:
                db.add(Message(
                    id=m_uuid,
                    conversation_id=conv_uuid,
                    role=role,
                    content=content,
                    token_count=token_count,
                ))
        except Exception:
            pass  # Non-fatal: in-memory ctx is the source of truth during a session


    # Get the last user prompt
    def get_latest_user_prompt(self) -> str:
        """ Get the last user prompt """

        for msg in reversed(self.ctx):
            if msg.get("role") == "user" and msg.get("content"):
                return msg["content"]
        return ""



    # TODO: Write pytest for this
    async def build(self) -> List[Dict[str, str]]:
        """
        Build the ChatML message list to send to the LLM:
          1. Retrieve relevant tools and LTM memories (async, non-blocking).
          2. Compose system prompt (with summary + LTM if present).
          3. Apply token budget — trigger compaction if needed.
          4. Return messages list.
        """
        user_prompt = self.get_latest_user_prompt()

        # Step 1: retrieve tools and relevant LTM memories concurrently
        async def _empty(): return []
        tools_task = asyncio.create_task(self.tr.aretrieve(user_prompt) if user_prompt else _empty())
        ltm_task = asyncio.create_task(self._fetch_ltm(user_prompt))
        tools, ltm_facts = await asyncio.gather(tools_task, ltm_task)

        tools_str = json.dumps(tools, indent=2) if tools else "[]"

        # Step 2: compose system prompt
        system_content = SYSTEM_PROMPT
        if self.loaded_summary:
            system_content = (
                f"Previous conversation summary:\n{self.loaded_summary}\n\n"
                + system_content
            )
        if ltm_facts:
            facts_str = "\n".join(f"- {f}" for f in ltm_facts)
            system_content = f"Relevant long-term memory:\n{facts_str}\n\n" + system_content
        system_content += f"\n\nAvailable Tools:\n{tools_str}"

        # Step 3: compact if needed
        await self._maybe_compact()

        # Step 4: build final list
        messages = [{"role": "system", "content": system_content}]
        for msg in self.ctx:
            role = msg["role"]
            if role in ("output", "tool"):
                role = "user"
            messages.append({"role": role, "content": msg["content"]})

        # Hard budget enforcement
        messages = self._enforce_budget(messages)

        return messages

    async def _fetch_ltm(self, query: str, top_k: int = 5) -> List[str]:
        """Vector-search LTM for facts relevant to query. Returns list of content strings."""
        if not query:
            return []
        try:
            results = await asyncio.to_thread(
                self._ltm.search_memories,
                self.conversation_id,
                query,
                top_k,
            )
            return [m.content for m in results]
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Token budget
    # ------------------------------------------------------------------

    def _enforce_budget(self, messages: List[dict]) -> List[dict]:
        """Drop oldest non-system messages until total tokens fit in budget."""
        budget = tokenizer.max_tokens - TOKEN_HEADROOM
        while True:
            total = tokenizer.count_messages(messages)
            if total <= budget:
                break
            # Find the first non-system message and drop it
            for i, m in enumerate(messages):
                if m["role"] != "system":
                    messages.pop(i)
                    break
            else:
                break  # only system left, nothing to drop
        return messages

    # ------------------------------------------------------------------
    # Compaction
    # ------------------------------------------------------------------

    async def _maybe_compact(self) -> None:
        """
        If ctx has >= COMPACTION_TRIGGER messages, summarize the oldest
        MESSAGES_TO_COMPRESS messages with the LLM and replace them with
        the summary, keeping the MESSAGES_TO_KEEP most recent.
        """
        if len(self.ctx) < COMPACTION_TRIGGER:
            return
        if self.summarizer is None:
            return

        to_compress = self.ctx[:MESSAGES_TO_COMPRESS]
        to_keep = self.ctx[MESSAGES_TO_COMPRESS:]

        # Convert to plain role/content dicts for the summarizer
        messages_for_llm = [
            {"role": m["role"] if m["role"] not in ("output", "tool") else "user",
             "content": m["content"]}
            for m in to_compress
        ]

        last_message_id = to_compress[-1].get("id", "")

        summary_text = await self.summarizer.summarize(
            messages=messages_for_llm,
            conversation_id=self.conversation_id,
            last_message_id=last_message_id,
        )

        # Replace ctx: summary entry + remaining messages
        self.loaded_summary = (
            (self.loaded_summary + "\n\n" + summary_text).strip()
            if self.loaded_summary
            else summary_text
        )
        self.ctx = to_keep
