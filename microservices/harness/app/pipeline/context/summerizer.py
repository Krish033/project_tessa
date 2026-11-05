import uuid
import asyncio
from typing import List, Tuple

from app.core.database import db_session
from app.models.models import ContextSummary
from app.pipeline.context.tokenizor import tokenizer

COMPACTION_TRIGGER = 10   # Compress when ctx hits this many messages
MESSAGES_TO_COMPRESS = 7  # How many oldest messages to summarize
MESSAGES_TO_KEEP = 3      # How many most-recent messages to retain after summary


class Summarizer:
    """
    Summarizes a batch of messages using an LLM call and persists
    the result to the context_summaries table.
    """

    def __init__(self, llm=None):
        self.llm = llm

    async def maybe_compact(
        self,
        ctx: List[dict],
        conversation_id: str,
        loaded_summary: str = "",
    ) -> Tuple[List[dict], str]:
        """
        If ctx has >= COMPACTION_TRIGGER messages, summarize the oldest
        MESSAGES_TO_COMPRESS messages with the LLM and return (retained_messages, updated_summary).
        """
        if len(ctx) < COMPACTION_TRIGGER or self.llm is None:
            return ctx, loaded_summary

        to_compress = ctx[:MESSAGES_TO_COMPRESS]
        to_keep = ctx[MESSAGES_TO_COMPRESS:]

        messages_for_llm = [
            {
                "role": m["role"] if m.get("role") not in ("output", "tool") else "user",
                "content": m.get("content", ""),
            }
            for m in to_compress
        ]

        last_message_id = to_compress[-1].get("id", "")

        summary_text = await self.summarize(
            messages=messages_for_llm,
            conversation_id=conversation_id,
            last_message_id=last_message_id,
        )

        updated_summary = (
            (loaded_summary + "\n\n" + summary_text).strip()
            if loaded_summary
            else summary_text
        )
        return to_keep, updated_summary

    async def summarize(
        self,
        messages: List[dict],
        conversation_id: str,
        last_message_id: str,
    ) -> str:
        """Call LLM to summarize messages, save to DB, return summary text."""
        transcript = "\n".join(
            f"{m.get('role', '').upper()}: {m.get('content', '')}" for m in messages
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

        if hasattr(self.llm, "run_stream"):
            _, summary_text = await self.llm.run_stream(llm_messages)
        else:
            summary_text = await asyncio.to_thread(self.llm.run, llm_messages)

        summary_text = summary_text.strip()
        token_count = tokenizer.count(summary_text)

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
        try:
            try:
                conv_uuid = uuid.UUID(str(conversation_id))
            except ValueError:
                conv_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(conversation_id))

            try:
                msg_uuid = uuid.UUID(str(last_message_id))
            except ValueError:
                msg_uuid = uuid.uuid4()

            with db_session() as db:
                db.add(ContextSummary(
                    id=uuid.uuid4(),
                    conversation_id=conv_uuid,
                    summary=summary,
                    last_message_id=msg_uuid,
                    token_count=token_count,
                ))
        except Exception:
            pass