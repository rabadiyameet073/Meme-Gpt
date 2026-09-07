import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import ApiKey, User, get_db, utc_now
from app.core.auth import (
    AuthContext,
    generate_api_key,
    get_api_tier,
    require_admin,
    get_current_user,
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
    # If generating admin or internal keys, require admin permissions
    if body.tier in ("admin", "internal") and not auth.is_admin:
        raise HTTPException(status_code=403, detail="Admin permissions required to create admin keys")

    api_key, raw_token = generate_api_key(
        db=db,
        tier=body.tier,
        name=body.name,
        user_id=body.user_id or auth.user_id
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


# ── OAuth (Google & GitHub) Routes ─────────────────────────────────

@router.get("/google/login", summary="Get Google OAuth consent URL")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    return {"url": get_google_auth_url()}


@router.get("/google/callback", summary="Google OAuth callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    user_info = await exchange_google_code(code)
    if not user_info:
        raise HTTPException(status_code=400, detail="Google authentication failed")
    return await _oauth_login(user_info, db)


@router.get("/github/login", summary="Get GitHub OAuth consent URL")
async def github_login():
    """Redirect user to GitHub OAuth."""
    return {"url": get_github_auth_url()}


@router.get("/github/callback", summary="GitHub OAuth callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback."""
    user_info = await exchange_github_code(code)
    if not user_info:
        raise HTTPException(status_code=400, detail="GitHub authentication failed")
    return await _oauth_login(user_info, db)


async def _oauth_login(user_info: dict, db: Session) -> dict:
    """Create or find user from OAuth info, return JWT tokens."""
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
        if not user.oauth_provider:
            user.oauth_provider = user_info["provider"]
            user.oauth_id = user_info["oauth_id"]
        if user_info.get("avatar_url") and not user.avatar_url:
            user.avatar_url = user_info["avatar_url"]

    user.last_login = utc_now()
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }


@router.get("/me", summary="Get authenticated user profile")
async def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get current user from JWT token."""
    return {"user": user.to_dict()}


