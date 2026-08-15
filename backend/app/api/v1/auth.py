import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import ApiKey, get_db
from app.core.auth import (
    AuthContext,
    generate_api_key,
    get_api_tier,
    require_admin,
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

