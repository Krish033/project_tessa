import uuid
import asyncio
from typing import List, Optional, Tuple

from app.core.database import db_session
from app.models.models import Message, ContextSummary
from app.pipeline.context.tokenizor import tokenizer


class DataPipeline:
    """
    Handles database persistence, message fetching, and conversation state loading.
    """

    def persist_message(self, conversation_id: str, msg_id: str, role: str, content: str) -> None:
        """Persist a message to the database with calculated token count."""
        token_count = tokenizer.count(content)
        try:
            try:
                conv_uuid = uuid.UUID(str(conversation_id))
            except ValueError:
                conv_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(conversation_id))

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
            pass  # Non-fatal: in-memory context is the session source of truth

    def fetch_latest_summary(self, conversation_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Return (summary_text, last_message_id) from the most recent summary row."""
        try:
            with db_session() as db:
                row = (
                    db.query(ContextSummary)
                    .filter_by(conversation_id=conversation_id)
                    .order_by(ContextSummary.created_at.desc())
                    .first()
                )
                if row:
                    return row.summary, str(row.last_message_id) if row.last_message_id else None
        except Exception:
            pass
        return None, None

    def fetch_messages_after(self, conversation_id: str, after_message_id: Optional[str]) -> List[dict]:
        """Return messages created after the given message id (or all messages if None)."""
        try:
            with db_session() as db:
                if after_message_id:
                    boundary = db.query(Message).filter_by(id=after_message_id).first()
                    if boundary:
                        rows = (
                            db.query(Message)
                            .filter(
                                Message.conversation_id == conversation_id,
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
                        .filter_by(conversation_id=conversation_id)
                        .order_by(Message.created_at)
                        .all()
                    )
                return [
                    {"id": str(m.id), "role": m.role, "content": m.content}
                    for m in rows
                ]
        except Exception:
            return []

    async def load(self, conversation_id: str) -> Tuple[List[dict], str]:
        """
        Load conversation state:
          1. Retrieve latest summary and cutoff message ID.
          2. Retrieve remaining messages after cutoff ID.
        """
        latest_summary, after_id = await asyncio.to_thread(self.fetch_latest_summary, conversation_id)
        messages = await asyncio.to_thread(self.fetch_messages_after, conversation_id, after_id)
        return messages, latest_summary or ""
