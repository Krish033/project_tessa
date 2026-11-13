import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user_optional, require_current_user
from shared.config.database import AsyncSessionLocal
from shared.config.logging import get_logger
from shared.database.models import Project, Conversation, User

router = APIRouter()
logger = get_logger(__name__)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None


@router.post("/", summary="Create a new Project", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new project. Associates with current user if logged in."""
    user_id = user.id if user else None
    new_project = Project(
        name=project_in.name,
        description=project_in.description,
        instructions=project_in.instructions,
        user_id=user_id,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return {
        "status": "success",
        "project": {
            "id": str(new_project.id),
            "name": new_project.name,
            "description": new_project.description,
            "instructions": new_project.instructions,
            "user_id": str(new_project.user_id) if new_project.user_id else None,
            "created_at": new_project.created_at.isoformat() if new_project.created_at else None,
            "updated_at": new_project.updated_at.isoformat() if new_project.updated_at else None,
            "chats": [],
        },
    }


@router.get("/", summary="Get All Projects")
async def get_all_projects(
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve all projects (filtered by user if authenticated, otherwise all or unassigned)."""
    stmt = select(Project).options(selectinload(Project.conversations)).order_by(Project.updated_at.desc())
    if user:
        stmt = stmt.where((Project.user_id == user.id) | (Project.user_id.is_(None)))

    result = await db.execute(stmt)
    projects = result.scalars().all()

    return {
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "instructions": p.instructions,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                "chats": [
                    {
                        "id": str(c.id),
                        "title": c.title,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                    }
                    for c in p.conversations
                ],
            }
            for p in projects
        ]
    }


@router.get("/{project_id}", summary="Get Project by ID")
async def get_project_by_id(
    project_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve a project and its chats by ID."""
    try:
        p_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format.")

    stmt = select(Project).options(selectinload(Project.conversations)).where(Project.id == p_uuid)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    return {
        "project": {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "instructions": project.instructions,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "chats": [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in project.conversations
            ],
        }
    }


@router.patch("/{project_id}", summary="Update Project")
@router.put("/{project_id}", summary="Update Project")
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update project details (name, description, instructions)."""
    try:
        p_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format.")

    stmt = select(Project).where(Project.id == p_uuid)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description
    if project_in.instructions is not None:
        project.instructions = project_in.instructions

    await db.commit()
    await db.refresh(project)

    return {
        "status": "success",
        "project": {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "instructions": project.instructions,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        },
    }


@router.delete("/{project_id}", summary="Delete Project")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a project."""
    try:
        p_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID format.")

    stmt = select(Project).where(Project.id == p_uuid)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    await db.delete(project)
    await db.commit()

    return {"status": "success", "message": f"Project {project_id} deleted successfully."}
