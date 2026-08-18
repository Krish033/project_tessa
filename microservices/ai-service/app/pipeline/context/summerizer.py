import uuid
import asyncio
from typing import List

from app.core.database import db_session
from app.models.models import ContextSummary
from app.pipeline.context.tokenizor import tokenizer


class Summarizer:
    """
    Summarizes a batch of messages using an LLM call and persists
    the result to the context_summaries table.
    """

    def __init__(self, llm):
        self.llm = llm

    async def summarize(
        self,
        messages: List[dict],
        conversation_id: str,
        last_message_id: str,
    ) -> str:
        """
        Call LLM to summarize messages, save to DB, return summary text.

        Args:
            messages: list of {"role": ..., "content": ...} dicts to summarize
            conversation_id: UUID string of the conversation
            last_message_id: UUID string of the last message being compressed
        """
        # Build a plain transcript for the LLM to summarize
        transcript = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )

        llm_messages = [
            {
                "role": "system",
                "content": (
                    "You are a concise summarizer. "
                    "Summarize the following conversation into a short paragraph "
                    "capturing all key facts, decisions, and context. "
                    "Output only the summary, no preamble."
                ),
            },
            {
                "role": "user",
                "content": f"Conversation to summarize:\n\n{transcript}",
            },
        ]

        # Use run_stream if available, else run (sync wrapped in thread)
        if hasattr(self.llm, "run_stream"):
            _, summary_text = await self.llm.run_stream(llm_messages)
        else:
            summary_text = await asyncio.to_thread(self.llm.run, llm_messages)

        summary_text = summary_text.strip()
        token_count = tokenizer.count(summary_text)

        # Persist to DB
        await asyncio.to_thread(
            self._save,
            conversation_id,
            summary_text,
            last_message_id,
            token_count,
        )

        return summary_text

    def _save(
        self,
        conversation_id: str,
        summary: str,
        last_message_id: str,
        token_count: int,
    ) -> None:
        with db_session() as db:
            db.add(ContextSummary(
                id=uuid.uuid4(),
                conversation_id=uuid.UUID(conversation_id),
                summary=summary,
                last_message_id=uuid.UUID(last_message_id),
                token_count=token_count,
            ))