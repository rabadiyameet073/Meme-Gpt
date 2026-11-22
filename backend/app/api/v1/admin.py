"""
MemeGPT — Admin Meme Management Endpoints.

Frontend api.ts calls:
  POST   /api/admin/memes       → create meme
  DELETE /api/admin/memes/{id}  → delete meme
  GET    /api/admin/memes        → list all memes (admin view)
  PATCH  /api/admin/memes/{id}  → update meme
"""

import logging
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db, Meme, User, AdminAuditLog, SearchLog, Feedback, MemeFlag
from app.core.auth import AuthContext, require_admin

logger = logging.getLogger("memegpt.api.admin")

router = APIRouter(prefix="/admin", tags=["Admin — Meme Management"])


def _record_audit_log(db: Session, actor_id: Optional[str], action: str, target_type: str, target_id: Optional[str], details: dict):
    """Persists admin actions to the AdminAuditLog table (ADM-03)."""
    try:
        log_entry = AdminAuditLog(
            actor_id=actor_id or "admin",
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to record admin audit log: {e}")


class CreateMemeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: Optional[str] = None
    category: str = "general"
    categories: list[str] = []
    emotions: list[str] = []
    dialogue: str = ""
    explanation: str = ""
    keywords: list[str] = []
    image_url: Optional[str] = None
    gif_url: Optional[str] = None
    mp4_url: Optional[str] = None
    thumb_url: Optional[str] = None
    source: str = "manual"
    nsfw: bool = False


class UpdateMemeRequest(BaseModel):
    name: Optional[str] = None
    categories: Optional[list[str]] = None
    emotions: Optional[list[str]] = None
    dialogue: Optional[str] = None
    explanation: Optional[str] = None
    keywords: Optional[list[str]] = None
    image_url: Optional[str] = None
    gif_url: Optional[str] = None
    mp4_url: Optional[str] = None
    thumb_url: Optional[str] = None
    nsfw: Optional[bool] = None
    popularity_score: Optional[float] = None


@router.get("/memes", summary="List all memes (admin)")
def list_all_memes(
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Returns paginated list of all memes for admin panel. Admin only."""
    offset = max(page - 1, 0) * limit
    total = db.query(Meme).count()
    memes = db.query(Meme).order_by(Meme.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "memes": [m.to_dict() for m in memes],
    }


def _reindex_meme_to_qdrant(meme_dict: dict):
    """Embeds text and upserts meme point into Qdrant index (ADM-04, AI-08)."""
    try:
        from app.services.embedding_service import embed_text
        from app.services.search_service import upsert_memes
        text_to_embed = " ".join(filter(None, [
            meme_dict.get("name"),
            meme_dict.get("dialogue"),
            meme_dict.get("explanation"),
            " ".join(meme_dict.get("keywords") or []),
            " ".join(meme_dict.get("categories") or []),
        ]))
        vec = embed_text(text_to_embed)
        upsert_memes(memes_with_vectors=[{"meme": meme_dict, "text_vector": vec}])
    except Exception as e:
        logger.warning(f"Failed to re-index meme to Qdrant: {e}")


@router.post("/memes", summary="Create a new meme")
def create_meme(
    body: CreateMemeRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """
    Create a new meme record.
    Frontend calls POST /api/admin/memes.
    """
    meme_id = str(uuid.uuid4())[:8]
    slug = body.slug or body.name.lower().strip().replace(" ", "-")

    # Check slug uniqueness
    existing = db.query(Meme).filter((Meme.slug == slug) | (Meme.id == meme_id)).first()
    if existing:
        slug = f"{slug}-{meme_id}"

    categories = body.categories or ([body.category] if body.category else ["general"])

    new_meme = Meme(
        id=meme_id,
        name=body.name,
        slug=slug,
        categories=categories,
        emotions=body.emotions,
        dialogue=body.dialogue,
        explanation=body.explanation,
        keywords=body.keywords,
        image_url=body.image_url,
        image_ref=body.image_url,
        gif_url=body.gif_url,
        gif_ref=body.gif_url,
        mp4_url=body.mp4_url,
        video_ref=body.mp4_url,
        thumb_url=body.thumb_url,
        source=body.source,
        nsfw=body.nsfw,
    )

    db.add(new_meme)
    db.commit()
    db.refresh(new_meme)

    from app.core.cache import cache_flush_pattern
    cache_flush_pattern("search:*")
    cache_flush_pattern("trending:*")
    _reindex_meme_to_qdrant(new_meme.to_dict())

    # Record audit log (ADM-03)
    _record_audit_log(
        db=db,
        actor_id=auth.user_id,
        action="create_meme",
        target_type="meme",
        target_id=new_meme.id,
        details={"name": new_meme.name, "slug": new_meme.slug},
    )

    logger.info(f"Created meme: {meme_id} ({body.name})")
    return {"success": True, "meme": new_meme.to_dict()}


@router.patch("/memes/{meme_id}", summary="Update meme fields")
def update_meme(
    meme_id: str,
    body: UpdateMemeRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Update specific fields of a meme."""
    meme = db.query(Meme).filter((Meme.id == meme_id) | (Meme.slug == meme_id)).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    update_data = body.model_dump(exclude_none=True) if hasattr(body, "model_dump") else body.dict(exclude_none=True)
    for field, value in update_data.items():
        setattr(meme, field, value)

    db.commit()
    db.refresh(meme)

    from app.core.cache import cache_flush_pattern
    cache_flush_pattern("search:*")
    cache_flush_pattern("trending:*")
    _reindex_meme_to_qdrant(meme.to_dict())

    # Record audit log (ADM-03)
    _record_audit_log(
        db=db,
        actor_id=auth.user_id,
        action="update_meme",
        target_type="meme",
        target_id=meme.id,
        details={"updated_fields": list(update_data.keys())},
    )

    return {"success": True, "meme": meme.to_dict()}


@router.delete("/memes/{meme_id}", summary="Delete a meme")
def delete_meme(
    meme_id: str,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """
    Delete a meme by ID.
    Frontend calls DELETE /api/admin/memes/{id}.
    Also removes from Qdrant if connected.
    """
    meme = db.query(Meme).filter((Meme.id == meme_id) | (Meme.slug == meme_id)).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    meme_name = meme.name
    target_id = meme.id
    db.delete(meme)
    db.commit()

    from app.core.cache import cache_flush_pattern
    cache_flush_pattern("search:*")
    cache_flush_pattern("trending:*")

    # Record audit log (ADM-03)
    _record_audit_log(
        db=db,
        actor_id=auth.user_id,
        action="delete_meme",
        target_type="meme",
        target_id=target_id,
        details={"name": meme_name},
    )

    # Also remove from Qdrant if available
    try:
        from app.services.search_service import get_qdrant_client, COLLECTION_NAME, _meme_id_to_int
        client = get_qdrant_client()
        if client:
            client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=[_meme_id_to_int(target_id)],
            )
    except Exception as e:
        logger.warning(f"Failed to remove meme {target_id} from Qdrant: {e}")

    logger.info(f"Deleted meme: {target_id} ({meme_name})")
    return {"success": True, "deleted_id": target_id}


# ── ADM-03: Audit Logs ─────────────────────────────────────────────

@router.get("/audit-logs", summary="List admin audit trail logs (ADM-03)")
def get_audit_logs(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Retrieve immutable audit logs of administrative actions."""
    logs = (
        db.query(AdminAuditLog)
        .order_by(AdminAuditLog.created_at.desc())
        .offset(offset)
        .limit(min(limit, 100))
        .all()
    )
    total = db.query(AdminAuditLog).count()
    return {"total": total, "logs": [l.to_dict() for l in logs]}


# ── ADM-07: User Management ────────────────────────────────────────

class UpdateUserRoleRequest(BaseModel):
    plan: Optional[str] = Field(None, pattern="^(free|pro|enterprise|admin)$")
    is_admin: Optional[bool] = None


class UpdateUserStatusRequest(BaseModel):
    is_active: bool


@router.get("/users", summary="List users for administration (ADM-07)")
def list_admin_users(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Returns paginated user list for admin management."""
    total = db.query(User).count()
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(min(limit, 100)).all()
    return {"total": total, "users": [u.to_dict() for u in users]}


@router.patch("/users/{user_id}/role", summary="Update user role/plan (ADM-07)")
def update_user_role(
    user_id: str,
    body: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Grant or revoke admin privileges and subscription tiers."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.plan is not None:
        user.plan = body.plan
    if body.is_admin is not None:
        user.is_admin = body.is_admin

    db.commit()
    db.refresh(user)

    _record_audit_log(
        db=db,
        actor_id=auth.user_id,
        action="update_user_role",
        target_type="user",
        target_id=user.id,
        details={"plan": user.plan, "is_admin": user.is_admin},
    )

    return {"success": True, "user": user.to_dict()}


@router.patch("/users/{user_id}/status", summary="Activate or ban user (ADM-07)")
def update_user_status(
    user_id: str,
    body: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Deactivate (ban) or reactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = body.is_active
    db.commit()
    db.refresh(user)

    _record_audit_log(
        db=db,
        actor_id=auth.user_id,
        action="update_user_status",
        target_type="user",
        target_id=user.id,
        details={"is_active": user.is_active},
    )

    return {"success": True, "user": user.to_dict()}


# ── ADM-05 / RPT-02: KPI & Metrics Dashboard ───────────────────────

@router.get("/metrics", summary="Admin KPI and platform metrics overview (ADM-05)")
def get_admin_metrics(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin),
):
    """Summary metrics of catalog, engagement, flags, and system state."""
    total_memes = db.query(Meme).count()
    active_memes = db.query(Meme).filter(Meme.moderation_status == "approved").count()
    pending_review = db.query(Meme).filter(Meme.moderation_status == "pending_review").count()
    total_users = db.query(User).count()
    total_searches = db.query(SearchLog).count()
    total_feedback = db.query(Feedback).count()
    pending_flags = db.query(MemeFlag).filter(MemeFlag.status == "pending").count()

    return {
        "memes": {
            "total": total_memes,
            "active": active_memes,
            "pending_review": pending_review,
        },
        "users": {
            "total": total_users,
        },
        "analytics": {
            "total_searches": total_searches,
            "total_feedback_events": total_feedback,
            "pending_flags": pending_flags,
        },
    }
