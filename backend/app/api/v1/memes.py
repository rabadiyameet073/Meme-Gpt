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


CATEGORY_SYNONYMS = {
    "work": ["work", "office", "corporate", "job", "career", "meeting", "boss", "monday"],
    "office": ["office", "work", "corporate", "job", "career", "meeting"],
    "tech": ["tech", "coding", "programming", "developer", "software", "computer", "linux", "git", "bug"],
    "coding": ["coding", "tech", "programming", "developer", "software", "bug"],
    "gaming": ["gaming", "games", "game", "gamer", "play", "nintendo", "playstation", "xbox"],
    "relationships": ["relationships", "relationship", "dating", "love", "romance", "crush", "couple", "boyfriend", "girlfriend"],
    "relationship": ["relationships", "relationship", "dating", "love", "romance", "crush", "couple", "boyfriend", "girlfriend"],
    "wholesome": ["wholesome", "heartwarming", "cute", "animals", "kindness", "sweet", "dog", "puppy", "cat"],
    "tv": ["tv", "cinema", "movie", "movies", "show", "series", "popculture", "film", "hollywood", "actor"],
    "sports": ["sports", "sport", "fitness", "football", "soccer", "cricket", "basketball", "gym", "athlete", "workout"],
    "funny": ["funny", "humor", "comedy", "laugh", "hilarious", "meme"],
    "money": ["money", "crypto", "finance", "stonks", "rich", "cash", "bank"],
    "failure": ["failure", "fail", "sad", "defeat", "loss", "stress"],
    "success": ["success", "win", "pride", "champion", "winner"],
}


@router.get("/memes", summary="List and filter memes with pagination")
def list_memes(
    q: str = "",
    category: str = "",
    limit: int = 50,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """List memes ordered by popularity and filtered by keyword or category."""
    from sqlalchemy import or_, func
    limit = min(max(limit, 1), 100)
    query = db.query(Meme).filter(Meme.moderation_status != "removed")

    if category:
        cat_clean = sanitize_input(category).lower().strip()
        synonyms = CATEGORY_SYNONYMS.get(cat_clean, [cat_clean])
        conds = []
        for syn in synonyms:
            conds.append(func.lower(Meme.categories).like(f'%"{syn}"%'))
            conds.append(func.lower(Meme.categories).like(f'%{syn}%'))
            conds.append(func.lower(Meme.keywords).like(f'%"{syn}"%'))
        
        filtered_query = query.filter(or_(*conds))
        if filtered_query.count() > 0:
            query = filtered_query

    memes = query.order_by(Meme.popularity_score.desc(), Meme.usage_count.desc()).all()

    if q:
        search = sanitize_input(q).lower().strip()
        if search:
            terms = [t for t in search.split() if len(t) > 1]
            scored_memes = []
            for m in memes:
                m_name = m.name.lower()
                m_dial = (m.dialogue or "").lower()
                m_exp = (m.explanation or "").lower()
                kws = [k.lower() for k in m.keywords_list()]
                cats = [c.lower() for c in m.categories_list()]

                score = 0
                if search in m_name:
                    score += 10
                if search in m_dial or search in m_exp:
                    score += 6
                if any(search in k for k in kws):
                    score += 5
                if any(search in c for c in cats):
                    score += 4
                for term in terms:
                    if term in m_name:
                        score += 3
                    if any(term in k for k in kws):
                        score += 2
                    if any(term in c for c in cats):
                        score += 1

                if score > 0:
                    scored_memes.append((score, m))

            if scored_memes:
                scored_memes.sort(key=lambda x: x[0], reverse=True)
                memes = [m for _, m in scored_memes]
            elif not category:
                # If no exact match and no category filter, provide diverse top memes
                memes = memes[:limit]

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

