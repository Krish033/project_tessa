import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user_optional
from shared.config.database import AsyncSessionLocal
from shared.config.logging import get_logger
from shared.database.models import Conversation, Message, Project, User
from shared.rabbitmq import get_rabbitmq

router = APIRouter()
logger = get_logger(__name__)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"
    project_id: Optional[str] = None
    initial_message: Optional[str] = None


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    project_id: Optional[str] = None


class MessageCreate(BaseModel):
    role: str = "user"  # "user" | "assistant" | "tool"
    content: str


@router.post("/", summary="Create New Chat", status_code=status.HTTP_201_CREATED)
@router.post("/new", summary="Create New Chat", status_code=status.HTTP_201_CREATED)
async def create_new_chat(
    chat_in: Optional[ChatCreate] = None,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new chat conversation, optionally associated with a project."""
    title = chat_in.title if chat_in and chat_in.title else "New Chat"
    project_id = None
    if chat_in and chat_in.project_id:
        try:
            project_id = uuid.UUID(chat_in.project_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format.")

    user_id = user.id if user else None

    conversation = Conversation(
        title=title,
        project_id=project_id,
        user_id=user_id,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    messages_list = []
    # If an initial_message was provided, immediately persist it and execute harness via RabbitMQ
    if chat_in and chat_in.initial_message and chat_in.initial_message.strip():
        user_text = chat_in.initial_message.strip()
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=user_text,
        )
        db.add(user_msg)
        await db.commit()
        await db.refresh(user_msg)
        messages_list.append({
            "id": str(user_msg.id),
            "role": user_msg.role,
            "content": user_msg.content,
            "created_at": user_msg.created_at.isoformat() if user_msg.created_at else None,
        })

        rabbit = get_rabbitmq()
        try:
            rpc_payload = {
                "prompt": user_text,
                "conversation_id": str(conversation.id),
                "history": [],
            }
            logger.info("gateway_dispatching_initial_message_to_harness", conversation_id=str(conversation.id))
            harness_result = await rabbit.rpc_call("harness.agent_run", rpc_payload, timeout=30.0)
            reply_text = harness_result.get("answer", "Agent finished without reply.")

            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=reply_text,
            )
            db.add(assistant_msg)
            await db.commit()
            await db.refresh(assistant_msg)
            messages_list.append({
                "id": str(assistant_msg.id),
                "role": assistant_msg.role,
                "content": assistant_msg.content,
                "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None,
            })
        except Exception as rpc_err:
            logger.error("harness_initial_message_rpc_failed", error=str(rpc_err))
            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=f"An error occurred executing agent over RabbitMQ: {rpc_err}",
            )
            db.add(assistant_msg)
            await db.commit()
            await db.refresh(assistant_msg)
            messages_list.append({
                "id": str(assistant_msg.id),
                "role": assistant_msg.role,
                "content": assistant_msg.content,
                "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None,
            })

    return {
        "status": "success",
        "chat": {
            "id": str(conversation.id),
            "title": conversation.title,
            "project_id": str(conversation.project_id) if conversation.project_id else None,
            "user_id": str(conversation.user_id) if conversation.user_id else None,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "messages": messages_list,
        },
    }


@router.get("/", summary="Get All Chats")
async def get_all_chats(
    project_id: Optional[str] = None,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve all chats, optionally filtered by project_id or user."""
    stmt = select(Conversation).order_by(Conversation.updated_at.desc())

    if project_id:
        try:
            p_uuid = uuid.UUID(project_id)
            stmt = stmt.where(Conversation.project_id == p_uuid)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format.")

    if user:
        stmt = stmt.where((Conversation.user_id == user.id) | (Conversation.user_id.is_(None)))

    result = await db.execute(stmt)
    conversations = result.scalars().all()

    return {
        "chats": [
            {
                "id": str(c.id),
                "title": c.title,
                "project_id": str(c.project_id) if c.project_id else None,
                "user_id": str(c.user_id) if c.user_id else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in conversations
        ]
    }


@router.get("/{chat_id}", summary="Get Chat by ID")
async def get_chat_by_id(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve a specific chat by ID, including its messages."""
    try:
        c_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat ID format.")

    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == c_uuid)
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

    return {
        "chat": {
            "id": str(conversation.id),
            "title": conversation.title,
            "project_id": str(conversation.project_id) if conversation.project_id else None,
            "user_id": str(conversation.user_id) if conversation.user_id else None,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in conversation.messages
            ],
        }
    }


@router.patch("/{chat_id}", summary="Update Chat")
@router.put("/{chat_id}", summary="Update Chat")
async def update_chat(
    chat_id: str,
    chat_in: ChatUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update chat title or link/unlink to a project."""
    try:
        c_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat ID format.")

    stmt = select(Conversation).where(Conversation.id == c_uuid)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

    if chat_in.title is not None:
        conversation.title = chat_in.title

    if chat_in.project_id is not None:
        if chat_in.project_id == "" or chat_in.project_id.lower() == "null":
            conversation.project_id = None
        else:
            try:
                conversation.project_id = uuid.UUID(chat_in.project_id)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format.")

    await db.commit()
    await db.refresh(conversation)

    return {
        "status": "success",
        "chat": {
            "id": str(conversation.id),
            "title": conversation.title,
            "project_id": str(conversation.project_id) if conversation.project_id else None,
            "user_id": str(conversation.user_id) if conversation.user_id else None,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
        },
    }


@router.delete("/{chat_id}", summary="Delete Chat")
async def delete_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a chat conversation."""
    try:
        c_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat ID format.")

    stmt = select(Conversation).where(Conversation.id == c_uuid)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

    await db.delete(conversation)
    await db.commit()

    return {"status": "success", "message": f"Chat {chat_id} deleted successfully."}


@router.post("/{chat_id}/messages", summary="Add Message and Execute Agent via RabbitMQ", status_code=status.HTTP_201_CREATED)
async def add_message(
    chat_id: str,
    msg_in: MessageCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Add a message to a conversation. If the message is from a user, Gateway executes
    the agent loop on the harness microservice exclusively via RabbitMQ RPC.
    """
    try:
        c_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid chat ID format.")

    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == c_uuid)
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

    # 1. Persist the incoming user message
    user_msg = Message(
        conversation_id=conversation.id,
        role=msg_in.role,
        content=msg_in.content,
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # 2. If user message, delegate harness execution to RabbitMQ
    assistant_msg = None
    if msg_in.role == "user":
        # Build prior history payload from DB
        history = [
            {"role": m.role, "content": m.content}
            for m in conversation.messages
        ]

        rabbit = get_rabbitmq()
        try:
            rpc_payload = {
                "prompt": msg_in.content,
                "conversation_id": str(conversation.id),
                "history": history,
            }
            logger.info("gateway_dispatching_to_harness_via_rabbitmq", conversation_id=str(conversation.id))
            harness_result = await rabbit.rpc_call("harness.agent_run", rpc_payload, timeout=30.0)

            reply_text = harness_result.get("answer", "Agent finished without reply.")

            # 3. Gateway stores the assistant response in database
            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=reply_text,
            )
            db.add(assistant_msg)
            await db.commit()
            await db.refresh(assistant_msg)

        except Exception as rpc_err:
            logger.error("harness_rabbitmq_rpc_failed", error=str(rpc_err))
            # Fallback message
            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=f"An error occurred executing agent over RabbitMQ: {rpc_err}",
            )
            db.add(assistant_msg)
            await db.commit()
            await db.refresh(assistant_msg)

    return {
        "status": "success",
        "message": {
            "id": str(user_msg.id),
            "conversation_id": str(user_msg.conversation_id),
            "role": user_msg.role,
            "content": user_msg.content,
            "created_at": user_msg.created_at.isoformat() if user_msg.created_at else None,
        },
        "response": {
            "id": str(assistant_msg.id),
            "conversation_id": str(assistant_msg.conversation_id),
            "role": assistant_msg.role,
            "content": assistant_msg.content,
            "created_at": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None,
        } if assistant_msg else None,
    }




