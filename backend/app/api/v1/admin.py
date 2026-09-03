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

from app.database import get_db, Meme
from app.core.auth import AuthContext, require_admin, get_api_tier

logger = logging.getLogger("memegpt.api.admin")

router = APIRouter(prefix="/admin", tags=["Admin — Meme Management"])


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
    auth: AuthContext = Depends(get_api_tier),
):
    """Returns paginated list of all memes for admin panel."""
    offset = max(page - 1, 0) * limit
    total = db.query(Meme).count()
    memes = db.query(Meme).order_by(Meme.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "memes": [m.to_dict() for m in memes],
    }


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
