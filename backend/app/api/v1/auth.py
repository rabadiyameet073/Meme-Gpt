import logging
import secrets
from typing import Optional, List
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import ApiKey, User, get_db, utc_now
from app.core.auth import (
    AuthContext,
    generate_api_key,
    get_api_tier,
    require_admin,
    get_jwt_cookie_settings,
)
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.services.oauth_service import (
    get_google_auth_url,
    exchange_google_code,
    get_github_auth_url,
    exchange_github_code,
)

logger = logging.getLogger("memegpt.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication & API Keys"])


class CreateApiKeyRequest(BaseModel):
    name: str = Field("Default API Key", min_length=1, max_length=100)
    tier: str = Field("free", pattern="^(free|pro|internal|admin)$")
    user_id: Optional[str] = None


class CreateApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    tier: str
    rate_limit: int
    raw_key: str = Field(..., description="Copy this now. It will NOT be shown again.")
    created_at: Optional[str] = None


@router.post("/api-keys", response_model=CreateApiKeyResponse, summary="Generate a new API key")
def create_new_api_key(
    body: CreateApiKeyRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier)
):
    """Issues a new API key (Free: 120 req/min, Pro: 300 req/min, Admin: 1000 req/min).
    The raw_key is returned ONLY on initial generation and never saved in plain text.
    """
    if body.tier in ("admin", "internal", "pro") and not auth.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required to create pro or admin keys")

    if not auth.is_admin and body.user_id and auth.user_id and body.user_id != auth.user_id:
        raise HTTPException(status_code=403, detail="Cannot create API keys for another user")

    api_key, raw_token = generate_api_key(
        db=db,
        tier=body.tier,
        name=body.name,
        user_id=auth.user_id if not auth.is_admin else (body.user_id or auth.user_id)
    )

    return {
        **api_key.to_dict(),
        "raw_key": raw_token
    }


@router.get("/api-keys", summary="List active API keys with masked prefixes")
def list_api_keys(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier)
):
    """Returns list of active API keys with secret token masked (e.g. pk_live_xxxx...1234)."""
    query = db.query(ApiKey).filter(ApiKey.revoked == False)
    if not auth.is_admin and auth.user_id:
        query = query.filter(ApiKey.user_id == auth.user_id)
    keys = query.order_by(ApiKey.created_at.desc()).all()
    return [k.to_dict() for k in keys]


@router.delete("/api-keys/{key_id}", summary="Revoke API key immediately")
def revoke_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_tier)
):
    """Revokes an API key. Revocation is instantaneous and permanently disables the key."""
    record = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="API key not found")

    if not auth.is_admin and record.user_id != auth.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to revoke this key")

    record.revoked = True
    db.commit()
    return {"success": True, "message": "API key revoked successfully", "id": key_id}


@router.get("/tier", summary="Check current caller tier and rate limit")
def check_tier(auth: AuthContext = Depends(get_api_tier)):
    """Returns authenticated access level, rate limit window, and admin status."""
    return auth.to_dict()


from app.core.jobs import recalculate_popularity_scores, warm_up_cache_task, aggregate_analytics_task


@router.post("/jobs/recalculate-popularity", summary="Trigger popularity decay recalculation")
def trigger_popularity_recalc(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin)
):
    """Admin maintenance endpoint: recalculates viral scores and interaction weights."""
    result = recalculate_popularity_scores(db)
    return result


@router.post("/jobs/warm-up", summary="Trigger cache warm-up for top queries")
def trigger_cache_warmup(auth: AuthContext = Depends(require_admin)):
    """Admin maintenance endpoint: pre-caches top search queries."""
    result = warm_up_cache_task()
    return result


@router.get("/jobs/analytics", summary="Trigger analytics aggregation")
def trigger_analytics_aggregation(auth: AuthContext = Depends(require_admin)):
    """Admin maintenance endpoint: aggregates platform search logs and latency stats."""
    return aggregate_analytics_task()


# ── Helper for setting auth cookies ────────────────────────────────

def _set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    try:
        cfg = get_jwt_cookie_settings()
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=15 * 60,
            httponly=cfg.get("httponly", True),
            secure=cfg.get("secure", False),
            samesite=cfg.get("samesite", "lax"),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=7 * 24 * 3600,
            httponly=cfg.get("httponly", True),
            secure=cfg.get("secure", False),
            samesite=cfg.get("samesite", "lax"),
        )
    except Exception as e:
        logger.debug(f"Cookie set notice: {e}")


# ── OAuth (Google & GitHub) Routes ─────────────────────────────────

@router.get("/google/login", summary="Get Google OAuth consent URL")
async def google_login(response: Response):
    """Redirect user to Google OAuth consent screen with CSRF state protection."""
    state = secrets.token_urlsafe(32)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        samesite="lax",
    )
    return {"url": get_google_auth_url(state=state), "state": state}


@router.get("/google/callback", summary="Google OAuth callback")
async def google_callback(
    code: str,
    response: Response,
    state: Optional[str] = None,
    oauth_state: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback with CSRF state validation."""
    if state and oauth_state:
        if not secrets.compare_digest(state, oauth_state):
            raise HTTPException(status_code=400, detail="OAuth state mismatch (CSRF protection)")
    elif state and not oauth_state:
        raise HTTPException(status_code=400, detail="OAuth state cookie missing (CSRF protection)")

    user_info = await exchange_google_code(code)
    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")
    return await _oauth_login(user_info, db, response)


@router.get("/github/login", summary="Get GitHub OAuth consent URL")
async def github_login(response: Response):
    """Redirect user to GitHub OAuth with CSRF state protection."""
    state = secrets.token_urlsafe(32)
    response.set_cookie(
        key="oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        samesite="lax",
    )
    return {"url": get_github_auth_url(state=state), "state": state}


@router.get("/github/callback", summary="GitHub OAuth callback")
async def github_callback(
    code: str,
    response: Response,
    state: Optional[str] = None,
    oauth_state: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback with CSRF state validation."""
    if state and oauth_state:
        if not secrets.compare_digest(state, oauth_state):
            raise HTTPException(status_code=400, detail="OAuth state mismatch (CSRF protection)")
    elif state and not oauth_state:
        raise HTTPException(status_code=400, detail="OAuth state cookie missing (CSRF protection)")

    user_info = await exchange_github_code(code)
    if not user_info:
        raise HTTPException(status_code=400, detail="GitHub authentication failed")
    return await _oauth_login(user_info, db, response)


async def _oauth_login(user_info: dict, db: Session, response: Optional[Response] = None) -> dict:
    """Create or find user from OAuth info, return JWT tokens."""
    if not user_info.get("email"):
        raise HTTPException(status_code=400, detail="OAuth provider did not supply an email address")
    if not user_info.get("email_verified", True):
        raise HTTPException(status_code=400, detail="Unverified email address from OAuth provider cannot be linked")

    user = db.query(User).filter(User.email == user_info["email"]).first()

    if not user:
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            avatar_url=user_info["avatar_url"],
            oauth_provider=user_info["provider"],
            oauth_id=user_info["oauth_id"],
            plan="free",
        )
        db.add(user)
    else:
        # Prevent silent takeover if existing user registered with password and a different OAuth provider
        if user.hashed_password and user.oauth_provider and user.oauth_provider != user_info["provider"]:
            raise HTTPException(
                status_code=400,
                detail="Account already registered with a different provider. Please sign in with your existing provider."
            )
        if not user.oauth_provider:
            user.oauth_provider = user_info["provider"]
            user.oauth_id = user_info["oauth_id"]
        if user_info.get("avatar_url") and not user.avatar_url:
            user.avatar_url = user_info["avatar_url"]
        if user_info.get("name") and not user.name:
            user.name = user_info["name"]

    user.last_login = utc_now()
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    if response:
        _set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


# ── Email/Password Authentication & Registration ───────────────────

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    name: Optional[str] = Field(None, max_length=200, description="Display name")


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferred_format: Optional[str] = Field(None, pattern="^(gif|image|mp4|webp)$")
    theme: Optional[str] = Field(None, pattern="^(dark|light)$")
    nsfw_enabled: Optional[bool] = None
    preferences: Optional[dict] = None


@router.post("/register", summary="Register a new user account")
async def register_user(body: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    """Register a new user with email and password (AUTH-09 password policy)."""
    import re
    email_clean = body.email.strip().lower()
    if "@" not in email_clean or "." not in email_clean:
        raise HTTPException(status_code=400, detail="Invalid email format")

    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r"[A-Za-z]", body.password) or not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", body.password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one letter and one number or special character"
        )

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email_clean,
        name=body.name.strip() if body.name else email_clean.split("@")[0],
        hashed_password=hash_password(body.password),
        plan="free",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    _set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.post("/login", summary="Login with email and password")
async def login_user(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate with email and password with brute-force protection (AUTH-09)."""
    from app.core.cache import cache_get, cache_set, cache_delete
    email_clean = body.email.strip().lower()

    # Brute-force lockout check (max 5 failed attempts in 15 mins)
    fail_key = f"login_failures:{email_clean}"
    fails = cache_get(fail_key) or 0
    if fails >= 5:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again in 15 minutes.",
            headers={"Retry-After": "900"}
        )

    user = db.query(User).filter(User.email == email_clean).first()

    if not user or not user.hashed_password:
        cache_set(fail_key, fails + 1, ttl=900)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(body.password, user.hashed_password):
        cache_set(fail_key, fails + 1, ttl=900)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Reset failure counter on success
    cache_delete(fail_key)

    user.last_login = utc_now()
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    _set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.post("/refresh", summary="Exchange refresh token for new access token")
async def refresh_tokens(request: Request, response: Response, body: Optional[RefreshRequest] = None, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token and rotated refresh token (AUTH-07)."""
    token = ""
    if body and body.refresh_token:
        token = body.refresh_token.strip()
    elif "refresh_token" in request.cookies:
        token = request.cookies.get("refresh_token", "").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Refresh token required")

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # AUTH-07: Invalidate the consumed refresh token family jti
    old_jti = payload.get("jti")
    if old_jti:
        from app.services.jwt_service import revoke_token_jti
        revoke_token_jti(old_jti)

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token({"sub": user.id, "email": user.email})
    new_refresh_token = create_refresh_token({"sub": user.id})

    _set_auth_cookies(response, new_access_token, new_refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.post("/logout", summary="Logout and clear session cookies")
async def logout_user(request: Request, response: Response):
    """Clear session cookies and revoke refresh token (AUTH-07)."""
    from app.services.jwt_service import decode_token, revoke_token_jti
    token = request.cookies.get("refresh_token")
    if token:
        payload = decode_token(token)
        if payload and payload.get("jti"):
            revoke_token_jti(payload["jti"])

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", summary="Get authenticated user profile")
async def get_current_user_profile(request: Request, db: Session = Depends(get_db)):
    """Get current user from JWT token."""
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token", "").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": user.to_dict()}


@router.put("/me", summary="Update user profile and preferences")
async def update_current_user_profile(
    body: UpdateProfileRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update profile fields for the authenticated user."""
    auth_header = request.headers.get("Authorization", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token", "").strip()

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.name is not None:
        user.name = body.name.strip()
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url.strip()
    if body.preferred_format is not None:
        user.preferred_format = body.preferred_format
    if body.theme is not None:
        user.theme = body.theme
    if body.nsfw_enabled is not None:
        user.nsfw_enabled = body.nsfw_enabled
    if body.preferences is not None:
        merged = dict(user.preferences or {})
        merged.update(body.preferences)
        user.preferences = merged

    db.commit()
    db.refresh(user)

    return {"user": user.to_dict()}


