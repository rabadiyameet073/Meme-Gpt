import json
import logging
import re
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import Meme, SessionLocal, get_db, sanitize_input
from app.models.meme import CreateMemeRequest

logger = logging.getLogger("memegpt.api.memes")
router = APIRouter(tags=["Memes"])


def _record_feedback_background(meme_id: str, signal: str, fmt: str = "image"):
    """Background task for recording feedback signals."""
    db = SessionLocal()
    try:
        meme = db.query(Meme).filter(Meme.id == meme_id).first()
        if meme:
            if signal == "upvote":
                meme.upvotes += 1
            elif signal == "downvote":
                meme.downvotes += 1
            elif signal == "copy":
                meme.viral_score += 0.5
                meme.usage_count += 1
            elif signal == "download":
                meme.viral_score += 1.0
                meme.usage_count += 1
            db.commit()
    except Exception as e:
        logger.error(f"Error in background feedback task: {e}")
        db.rollback()
    finally:
        db.close()


@router.get("/memes", summary="List and filter memes with pagination")
def list_memes(
    q: str = "",
    category: str = "",
    limit: int = 50,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """List memes ordered by popularity and filtered by keyword or category."""
    limit = min(max(limit, 1), 100)
    query = db.query(Meme)
    if category:
        query = query.filter(Meme.category == category)
    memes = query.order_by(Meme.usage_count.desc()).all()

    if q:
        search = sanitize_input(q).lower().strip()
        if search:
            filtered = []
            for m in memes:
                kws = m.keywords_list()
                if (
                    search in m.name.lower()
                    or search in m.dialogue.lower()
                    or search in m.category.lower()
                    or any(search in k.lower() for k in kws)
                ):
                    filtered.append(m)
            memes = filtered

    offset = (page - 1) * limit
    paged = memes[offset : offset + limit]

    return {
        "items": [m.to_dict() for m in paged],
        "total": len(memes),
        "page": page,
        "pageSize": limit
    }


from fastapi import Query


@router.get("/memes/{slug_or_id}", summary="Get specific meme details")
def get_meme_detail(
    slug_or_id: str,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Retrieve meme metadata by UUID, slug, or parameterized name with view tracking."""
    meme = db.query(Meme).filter(Meme.id == slug_or_id).first()

    if not meme:
        meme = db.query(Meme).filter(Meme.slug == slug_or_id).first()

    if not meme:
        memes = db.query(Meme).all()
        for m in memes:
            slug_val = re.sub(r"[^\w\s-]", "", m.name.lower()).strip().replace(" ", "-")
            if slug_val == slug_or_id:
                meme = m
                break

    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    # Asynchronously track view count without blocking response
    if background_tasks:
        background_tasks.add_task(_record_feedback_background, meme.id, "view", "image")

    return meme.to_dict()


@router.get("/memes/{slug_or_id}/download", summary="Download meme in specific format")
def download_meme(
    slug_or_id: str,
    format: str = Query(default="gif", pattern="^(gif|image|video|webp|png|mp4)$"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Direct CDN file redirect for download in GIF, PNG, MP4, or WebP format."""
    meme = db.query(Meme).filter(Meme.id == slug_or_id).first()
    if not meme:
        meme = db.query(Meme).filter(Meme.slug == slug_or_id).first()
    if not meme:
        memes = db.query(Meme).all()
        for m in memes:
            slug_val = re.sub(r"[^\w\s-]", "", m.name.lower()).strip().replace(" ", "-")
            if slug_val == slug_or_id:
                meme = m
                break
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")

    fmt = format.lower()
    target_url = None
    if fmt == "gif":
        target_url = meme.gif_ref
    elif fmt in ("video", "mp4"):
        target_url = meme.video_ref
    elif fmt in ("image", "png", "webp"):
        target_url = meme.image_ref

    if not target_url:
        target_url = meme.image_ref or meme.gif_ref or meme.video_ref or f"https://cdn.memegpt.com/images/{meme.id}.png"

    if background_tasks:
        background_tasks.add_task(_record_feedback_background, meme.id, "download", fmt)

    return RedirectResponse(url=target_url, status_code=301)



from app.core.auth import require_admin, AuthContext


@router.post("/admin/memes", summary="Create new meme entry")
def create_meme(
    body: CreateMemeRequest,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin)
):
    """Admin endpoint to create a new meme in database (requires Admin tier)."""
    meme = Meme(
        name=sanitize_input(body.name),
        category=body.category,
        dialogue=sanitize_input(body.dialogue),
        explanation=sanitize_input(body.explanation),
        keywords=json.dumps([sanitize_input(k) for k in body.keywords]),
        video_ref=body.videoRef,
        gif_ref=body.gifRef,
    )
    db.add(meme)
    db.commit()
    db.refresh(meme)
    return meme.to_dict()


@router.delete("/admin/memes/{meme_id}", summary="Delete meme entry")
def delete_meme(
    meme_id: str,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_admin)
):
    """Admin endpoint to delete a meme by ID (requires Admin tier)."""
    meme = db.query(Meme).filter(Meme.id == meme_id).first()
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    db.delete(meme)
    db.commit()
    return {"success": True}

