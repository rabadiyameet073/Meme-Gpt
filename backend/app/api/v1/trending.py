import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import Meme, get_db

logger = logging.getLogger("memegpt.api.trending")
router = APIRouter(tags=["Trending"])


@router.get("/trending", summary="Fetch trending memes")
def get_trending_memes(category: str = "", limit: int = 12, db: Session = Depends(get_db)):
    """Returns top trending memes ordered by usage and upvotes."""
    limit = min(max(limit, 1), 50)
    query = db.query(Meme)
    if category and category.lower() != "all":
        query = query.filter(Meme.category == category.lower())

    memes = query.order_by(Meme.usage_count.desc(), Meme.upvotes.desc()).limit(limit).all()
    return [m.to_dict() for m in memes]
