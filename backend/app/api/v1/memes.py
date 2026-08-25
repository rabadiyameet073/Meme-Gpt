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
from app.services.meme_service import format_meme_detail_response, get_meme_download_url


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
        raise HTTPException(status_code=404, detail=f"No meme found with slug '{slug_or_id}'")

    # Asynchronously track view count without blocking response
    if background_tasks:
        background_tasks.add_task(_record_feedback_background, meme.id, "view", "image")

    return format_meme_detail_response(meme, db=db)


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
    target_url = get_meme_download_url(meme, fmt)
    if not target_url:
        raise HTTPException(status_code=400, detail=f"Format '{format}' not available for this meme")

    if background_tasks:
        background_tasks.add_task(_record_feedback_background, meme.id, "download", fmt)

    return RedirectResponse(url=target_url, status_code=301)

