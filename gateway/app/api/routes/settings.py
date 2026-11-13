import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_optional
from shared.config.database import AsyncSessionLocal
from shared.config.logging import get_logger
from shared.database.models import Setting, User

router = APIRouter()
logger = get_logger(__name__)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


class LLMConfig(BaseModel):
    name: str = Field(..., description="Display name, e.g. 'Ollama Qwen 2.5' or 'OpenAI GPT-4o'")
    provider: str = Field(default="ollama", description="'ollama', 'openai', 'anthropic', 'custom', 'openrouter', 'vllm'")
    model_name: str = Field(..., description="Model identifier, e.g. 'qwen2.5:7b', 'gpt-4o', 'claude-3-5-sonnet-20241022'")
    url: str = Field(default="http://localhost:11434", description="Base URL endpoint for API or local inference")
    port: Optional[int] = Field(None, description="Optional port number override")
    auth_key: Optional[str] = Field(None, description="Optional API key or Bearer token")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096)
    is_default: Optional[bool] = Field(default=False)
    extra_headers: Optional[Dict[str, str]] = Field(default_factory=dict)


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = None
    auth_key: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_default: Optional[bool] = None
    extra_headers: Optional[Dict[str, str]] = None


# ── LLMs Endpoints ────────────────────────────────────────────

@router.get("/llms", summary="Get all configured LLMs")
async def get_all_llms(
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve all LLM configurations from the settings table."""
    stmt = (
        select(Setting)
        .where(Setting.category == "llm")
        .order_by(Setting.created_at.asc())
    )
    if user:
        stmt = stmt.where((Setting.user_id == user.id) | (Setting.user_id.is_(None)))

    result = await db.execute(stmt)
    records = result.scalars().all()

    llms = []
    for r in records:
        val = r.value or {}
        llms.append({
            "id": str(r.id),
            "key": r.key,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            **val,
        })

    return {"llms": llms}


@router.post("/llms", summary="Add new LLM configuration", status_code=status.HTTP_201_CREATED)
async def add_llm(
    config: LLMConfig,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
):
    """Store a new LLM configuration in the settings table."""
    user_id = user.id if user else None
    setting_id = uuid.uuid4()
    key_name = f"llm_{config.name.lower().replace(' ', '_')}_{setting_id.hex[:6]}"

    # Mask auth key for security in representation if needed, but store safely
    setting_record = Setting(
        id=setting_id,
        key=key_name,
        category="llm",
        value=config.model_dump(),
        user_id=user_id,
    )
    db.add(setting_record)
    await db.commit()
    await db.refresh(setting_record)

    return {
        "status": "success",
        "llm": {
            "id": str(setting_record.id),
            "key": setting_record.key,
            "created_at": setting_record.created_at.isoformat() if setting_record.created_at else None,
            "updated_at": setting_record.updated_at.isoformat() if setting_record.updated_at else None,
            **setting_record.value,
        },
    }


@router.patch("/llms/{llm_id}", summary="Update LLM configuration")
@router.put("/llms/{llm_id}", summary="Update LLM configuration")
async def update_llm(
    llm_id: str,
    update_data: LLMConfigUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update an existing LLM configuration in the settings table."""
    try:
        s_uuid = uuid.UUID(llm_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid LLM ID format.")

    stmt = select(Setting).where(Setting.id == s_uuid, Setting.category == "llm")
    result = await db.execute(stmt)
    setting_record = result.scalar_one_or_none()

    if not setting_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM configuration not found.")

    current_val = dict(setting_record.value or {})
    updates = update_data.model_dump(exclude_unset=True)

    current_val.update(updates)
    setting_record.value = current_val

    await db.commit()
    await db.refresh(setting_record)

    return {
        "status": "success",
        "llm": {
            "id": str(setting_record.id),
            "key": setting_record.key,
            "created_at": setting_record.created_at.isoformat() if setting_record.created_at else None,
            "updated_at": setting_record.updated_at.isoformat() if setting_record.updated_at else None,
            **setting_record.value,
        },
    }


@router.delete("/llms/{llm_id}", summary="Delete LLM configuration")
async def delete_llm(
    llm_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete an LLM configuration from the settings table."""
    try:
        s_uuid = uuid.UUID(llm_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid LLM ID format.")

    stmt = select(Setting).where(Setting.id == s_uuid, Setting.category == "llm")
    result = await db.execute(stmt)
    setting_record = result.scalar_one_or_none()

    if not setting_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM configuration not found.")

    await db.delete(setting_record)
    await db.commit()

    return {"status": "success", "message": f"LLM configuration {llm_id} deleted successfully."}
