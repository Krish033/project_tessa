import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, Index, UUID, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    summaries = relationship(
        "ContextSummary",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ContextSummary.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user / assistant / tool
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    conversation = relationship("Conversation", back_populates="messages")


class ContextSummary(Base):
    __tablename__ = "context_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    last_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    token_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    conversation = relationship("Conversation", back_populates="summaries")
    last_message = relationship("Message")


class LongTermMemory(Base):
    __tablename__ = "long_term_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(String(100), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    importance = Column(Float, nullable=False, default=0.5)
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        Index("idx_ltm_owner_key", "owner_id", "key", unique=True),
    )


class ToolModel(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=True)  # pgvector vector type
    parameters = Column(JSON, nullable=False)
    permissions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self) -> dict:
        return {
            "name": self.tool_name,
            "description": self.description,
            "parameters": self.parameters,
            "permissions": self.permissions,
        }

    def __repr__(self) -> str:
        return f"<ToolModel name={self.tool_name!r}>"
