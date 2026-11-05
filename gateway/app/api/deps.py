"""Gateway authentication dependencies and session verification."""

import time
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.config.config import settings
from shared.config.logging import get_logger
from shared.database.models.models import User, UserSession
from shared.config.database import AsyncSessionLocal, get_db

logger = get_logger(__name__)

# Lightweight in-memory session cache: token -> (user_id, email, cache_expiry_ts)
_session_cache: dict[str, tuple[str, str, float]] = {}
SESSION_CACHE_TTL = 30.0  # seconds


def invalidate_session_cache(token: str) -> None:
    """Invalidate cached session token immediately (e.g., on logout)."""
    _session_cache.pop(token, None)


async def verify_session_token(token: str | None) -> tuple[str, str] | None:
    """Validate a session token against PostgreSQL (with short TTL cache) and return (user_id, email)."""
    if not token:
        return None

    now_ts = time.time()
    cached = _session_cache.get(token)
    if cached and cached[2] > now_ts:
        return (cached[0], cached[1])

    try:
        now_dt = datetime.now(UTC)
        async with AsyncSessionLocal() as db:
            stmt = (
                select(UserSession)
                .options(selectinload(UserSession.user))
                .where(
                    UserSession.session_token == token,
                    UserSession.expires_at > now_dt,
                )
            )
            result = await db.execute(stmt)
            session_record = result.scalar_one_or_none()

            if not session_record or not session_record.user or not session_record.user.is_active:
                _session_cache.pop(token, None)
                return None

            user_id = str(session_record.user.id)
            email = session_record.user.email
            _session_cache[token] = (user_id, email, now_ts + SESSION_CACHE_TTL)
            return (user_id, email)
    except Exception as exc:
        logger.error("verify_session_token_error", error=str(exc))
        return None


def is_cookie_secure(request: Request) -> bool:
    """Determine whether cookies should have the Secure flag enabled."""
    if settings.environment != "production":
        return False
    host = request.headers.get("host", "")
    if "localhost" in host or "127.0.0.1" in host:
        return False
    return request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"


def get_session_token(request: Request) -> str | None:
    """Extract session token from HTTP-only cookie or Authorization header."""
    # 1. Primary: Session cookie
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        return token.strip()

    # 2. Fallback: Bearer Authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    return None


async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Retrieve the authenticated User from the current session token, if valid."""
    token = get_session_token(request)
    if not token:
        return None

    try:
        now = datetime.now(UTC)
        stmt = (
            select(UserSession)
            .options(selectinload(UserSession.user))
            .where(
                UserSession.session_token == token,
                UserSession.expires_at > now,
            )
        )
        result = await db.execute(stmt)
        session_record = result.scalar_one_or_none()

        if not session_record or not session_record.user:
            return None

        if not session_record.user.is_active:
            logger.warning("inactive_user_access_attempt", user_id=str(session_record.user.id))
            return None

        # Update last_active_at if more than 5 minutes have elapsed since last update
        if (now - session_record.last_active_at).total_seconds() > 300:
            session_record.last_active_at = now
            try:
                await db.commit()
            except Exception:
                await db.rollback()

        return session_record.user
    except Exception as exc:
        logger.error("session_lookup_failed", error=str(exc))
        return None


async def require_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    """Dependency enforcing that the request has an active, valid user session."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with Google.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
