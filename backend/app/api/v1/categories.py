"""
MemeGPT — Categories & Stats Endpoints.

Frontend api.ts calls:
  GET /api/categories  → list of all meme categories
  GET /api/stats       → platform statistics
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, Meme, SearchLog, Feedback

logger = logging.getLogger("memegpt.api.categories")

router = APIRouter(tags=["Categories & Stats"])

DEFAULT_CATEGORIES = {
    "coding", "work", "college", "gaming", "relationships",
    "money", "food", "general", "reaction", "wholesome", "tech", "burnout"
}


@router.get("/categories", summary="List all meme categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Returns all unique meme categories.
    Frontend uses this to populate category filter chips.
    """
    try:
        memes = db.query(Meme).all()

        categories = set(DEFAULT_CATEGORIES)
        for meme in memes:
            cats = meme.categories_list() if hasattr(meme, "categories_list") else None
            if isinstance(cats, list):
                for c in cats:
                    if c:
                        categories.add(c.strip().lower())
            elif isinstance(getattr(meme, "categories", None), list):
                for c in meme.categories:
                    if c:
                        categories.add(c.strip().lower())
            elif getattr(meme, "category", None):
                categories.add(meme.category.strip().lower())

        return sorted(categories)

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return sorted(DEFAULT_CATEGORIES)


@router.get("/stats", summary="Platform statistics")
def get_stats(db: Session = Depends(get_db)):
    """
    Returns platform-level statistics for admin dashboard / health check.
    Frontend calls GET /api/stats.
    """
    try:
        total_memes = db.query(func.count(Meme.id)).scalar() or 0
        total_searches = db.query(func.count(SearchLog.id)).scalar() or 0
        total_feedback = db.query(func.count(Feedback.id)).scalar() or 0

        memes_with_images = db.query(func.count(Meme.id)).filter(
            (Meme.image_url.isnot(None)) | (Meme.image_ref.isnot(None))
        ).scalar() or 0

        return {
            "total_memes": total_memes,
            "totalMemes": total_memes,
            "memes_with_images": memes_with_images,
            "total_searches": total_searches,
            "totalSearches": total_searches,
            "total_feedback": total_feedback,
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {"total_memes": 0, "totalMemes": 0, "total_searches": 0, "version": "1.0.0"}
