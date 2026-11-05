"""Google OAuth 2.0 User Authentication Routes.

Handles:
- /api/v1/auth/google/login: initiates OAuth consent flow with CSRF state protection
- /api/v1/auth/google/callback: validates OAuth state, token exchange, user identity, and establishes session
- /api/v1/auth/me: retrieves current authenticated user profile
- /api/v1/auth/status: checks authentication state without throwing 401
- /api/v1/auth/logout: terminates server-side session and clears HTTP-only cookie
"""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import quote_plus, urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.app.api.deps import (
    get_current_user_optional,
    get_session_token,
    invalidate_session_cache,
    is_cookie_secure,
    require_current_user,
)
from shared.config.config import settings
from shared.config.logging import get_logger
from shared.database.models.models import User, UserSession
from shared.config.database import get_db

logger = get_logger(__name__)

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class UserProfileResponse(BaseModel):
    """Authenticated user profile schema."""
    id: str
    email: str
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
    is_active: bool
    created_at: str


class AuthStatusResponse(BaseModel):
    """User authentication status schema."""
    authenticated: bool
    user: UserProfileResponse | None = None
    google_login_configured: bool


def _generate_oauth_state() -> tuple[str, str]:
    """Generate cryptographically secure state with HMAC-SHA256 signature."""
    nonce = secrets.token_urlsafe(32)
    sig = hmac.new(settings.secret_key.encode("utf-8"), nonce.encode("utf-8"), hashlib.sha256).hexdigest()
    combined_state = f"{nonce}.{sig}"
    return nonce, combined_state


def _verify_oauth_state(received_state: str, cookie_nonce: str | None) -> bool:
    """Verify HMAC signature and matching cookie nonce."""
    if not received_state or not cookie_nonce:
        return False
    parts = received_state.split(".", 1)
    if len(parts) != 2:
        return False
    nonce, sig = parts
    # Check HMAC signature
    expected_sig = hmac.new(settings.secret_key.encode("utf-8"), nonce.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        return False
    # Check matching cookie nonce
    return hmac.compare_digest(cookie_nonce, nonce)


@router.get("/google/login", summary="Initiate Google OAuth 2.0 login")
async def google_login(
    request: Request,
    return_url: str | None = None,
    format: str | None = Query(None, description="Set to 'json' to receive auth_url JSON payload instead of 302 redirect"),
):
    """Initiates Google OAuth 2.0 user login flow with CSRF protection."""
    if not settings.google_login_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Login is not configured on this server (GOOGLE_LOGIN_CLIENT_ID missing).",
        )

    nonce, state = _generate_oauth_state()

    params = {
        "client_id": settings.google_login_client_id,
        "redirect_uri": settings.google_login_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    cookie_secure = is_cookie_secure(request)

    if format == "json":
        json_resp = JSONResponse(content={"auth_url": auth_url})
        json_resp.set_cookie(
            key="oauth_state",
            value=nonce,
            max_age=300,
            httponly=True,
            samesite="lax",
            secure=cookie_secure,
            path="/",
        )
        return json_resp

    redirect_resp = RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)
    redirect_resp.set_cookie(
        key="oauth_state",
        value=nonce,
        max_age=300,
        httponly=True,
        samesite="lax",
        secure=cookie_secure,
        path="/",
    )
    return redirect_resp


@router.get("/google/callback", summary="Google OAuth 2.0 callback endpoint")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    """Handle the OAuth 2.0 redirect from Google, validate tokens, and issue session."""
    frontend_login = f"{settings.frontend_url}/login"

    # Handle provider errors (e.g. user denied consent)
    if error:
        logger.warning("google_oauth_error_from_provider", error=error)
        return RedirectResponse(
            url=f"{frontend_login}?error={quote_plus(error)}",
            status_code=status.HTTP_302_FOUND,
        )

    if not code or not state:
        logger.warning("google_oauth_missing_code_or_state")
        return RedirectResponse(
            url=f"{frontend_login}?error=missing_credentials",
            status_code=status.HTTP_302_FOUND,
        )

    cookie_nonce = request.cookies.get("oauth_state")
    if not _verify_oauth_state(state, cookie_nonce):
        logger.warning("google_oauth_state_validation_failed")
        return RedirectResponse(
            url=f"{frontend_login}?error=invalid_state",
            status_code=status.HTTP_302_FOUND,
        )

    # Exchange authorization code for tokens
    token_payload = {
        "code": code,
        "client_id": settings.google_login_client_id,
        "client_secret": settings.google_login_client_secret,
        "redirect_uri": settings.google_login_redirect_uri,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            token_resp = await http_client.post(GOOGLE_TOKEN_URL, data=token_payload)

            if token_resp.status_code != 200:
                logger.error(
                    "google_token_exchange_failed",
                    status_code=token_resp.status_code,
                    body=token_resp.text,
                )
                return RedirectResponse(
                    url=f"{frontend_login}?error=token_exchange_failed",
                    status_code=status.HTTP_302_FOUND,
                )

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            id_token = token_data.get("id_token")

            if not access_token:
                logger.error("google_missing_access_token")
                return RedirectResponse(
                    url=f"{frontend_login}?error=missing_access_token",
                    status_code=status.HTTP_302_FOUND,
                )

            # Retrieve userinfo from Google
            userinfo_resp = await http_client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_resp.status_code != 200:
                logger.error(
                    "google_userinfo_fetch_failed",
                    status_code=userinfo_resp.status_code,
                )
                return RedirectResponse(
                    url=f"{frontend_login}?error=userinfo_fetch_failed",
                    status_code=status.HTTP_302_FOUND,
                )

            userinfo = userinfo_resp.json()

            # Optional extra security: validate ID token audience via tokeninfo if present
            if id_token and settings.google_login_client_id:
                try:
                    tokeninfo_resp = await http_client.get(
                        f"{GOOGLE_TOKENINFO_URL}?id_token={id_token}"
                    )
                    if tokeninfo_resp.status_code == 200:
                        tokeninfo = tokeninfo_resp.json()
                        aud = tokeninfo.get("aud")
                        if aud and aud != settings.google_login_client_id:
                            logger.error("google_id_token_audience_mismatch", aud=aud)
                            return RedirectResponse(
                                url=f"{frontend_login}?error=invalid_token_audience",
                                status_code=status.HTTP_302_FOUND,
                            )
                except Exception as t_err:
                    logger.warning("google_tokeninfo_verification_warning", error=str(t_err))

    except Exception as exc:
        logger.error("google_oauth_network_exception", error=str(exc))
        return RedirectResponse(
            url=f"{frontend_login}?error=oauth_network_error",
            status_code=status.HTTP_302_FOUND,
        )

    google_id = userinfo.get("sub")
    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified", True)

    if not email:
        logger.error("google_userinfo_missing_email")
        return RedirectResponse(
            url=f"{frontend_login}?error=missing_email",
            status_code=status.HTTP_302_FOUND,
        )

    if str(email_verified).lower() not in ("true", "1"):
        logger.warning("google_email_not_verified", email=email)
        return RedirectResponse(
            url=f"{frontend_login}?error=email_not_verified",
            status_code=status.HTTP_302_FOUND,
        )

    email_clean = email.strip().lower()
    name = userinfo.get("name")
    given_name = userinfo.get("given_name")
    family_name = userinfo.get("family_name")
    picture = userinfo.get("picture")

    # Upsert user in PostgreSQL
    now = datetime.now(UTC)
    stmt = select(User).where((User.google_id == google_id) | (User.email == email_clean))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Update user attributes
        user.google_id = google_id
        if name:
            user.name = name
        if given_name:
            user.given_name = given_name
        if family_name:
            user.family_name = family_name
        if picture:
            user.picture = picture
        user.updated_at = now
    else:
        # Create new user
        user = User(
            email=email_clean,
            google_id=google_id,
            name=name,
            given_name=given_name,
            family_name=family_name,
            picture=picture,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    # Issue server-side session
    session_token = secrets.token_urlsafe(48)
    expires_at = now + timedelta(days=settings.session_expiry_days)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    session_record = UserSession(
        session_token=session_token,
        user_id=user.id,
        ip_address=client_ip,
        user_agent=user_agent,
        expires_at=expires_at,
        created_at=now,
        last_active_at=now,
    )
    db.add(session_record)
    await db.commit()

    # Create redirect response to frontend home with HTTP-only cookie
    redirect_target = f"{settings.frontend_url}/"
    response = RedirectResponse(url=redirect_target, status_code=status.HTTP_302_FOUND)

    cookie_secure = is_cookie_secure(request)
    max_age_seconds = settings.session_expiry_days * 86400

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        max_age=max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=cookie_secure,
        path="/",
    )
    # Clear the temporary oauth_state cookie
    response.delete_cookie(key="oauth_state", path="/")

    logger.info("user_authenticated_successfully", user_id=str(user.id), email=user.email)
    return response


@router.get("/me", response_model=UserProfileResponse, summary="Get current authenticated user")
async def get_current_user_profile(user: User = Depends(require_current_user)):
    """Retrieve the profile of the currently authenticated user."""
    return UserProfileResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        given_name=user.given_name,
        family_name=user.family_name,
        picture=user.picture,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.get("/status", response_model=AuthStatusResponse, summary="Get authentication status")
async def get_auth_status(user: User | None = Depends(get_current_user_optional)):
    """Check current authentication status without requiring 401 exceptions."""
    is_configured = bool(settings.google_login_client_id and settings.google_login_client_secret)
    if not user:
        return AuthStatusResponse(
            authenticated=False,
            user=None,
            google_login_configured=is_configured,
        )

    return AuthStatusResponse(
        authenticated=True,
        user=UserProfileResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            given_name=user.given_name,
            family_name=user.family_name,
            picture=user.picture,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        ),
        google_login_configured=is_configured,
    )


@router.post("/logout", summary="Logout and invalidate session")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Log out the user, invalidate the database session, and clear the HTTP-only cookie."""
    token = get_session_token(request)
    if token:
        invalidate_session_cache(token)
        try:
            stmt = delete(UserSession).where(UserSession.session_token == token)
            await db.execute(stmt)
            await db.commit()
        except Exception as exc:
            logger.error("logout_session_deletion_failed", error=str(exc))
            await db.rollback()

    # Clear session cookie
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
    )
    return {"status": "ok", "message": "Logged out successfully"}
