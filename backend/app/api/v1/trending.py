import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.trending_service import get_trending_catalog

logger = logging.getLogger("memegpt.api.trending")
router = APIRouter(tags=["Trending"])


@router.get("/trending", summary="Get trending memes ranked by popularity")
def get_trending_memes(
    category: str = Query(default="all", description="Category filter (all, work, gaming, relationships, tech, sports, tv, wholesome)"),
    limit: int = Query(default=20, ge=1, le=50, description="Number of results (1-50)"),
    period: str = Query(default="24h", description="Lookback period (24h, 7d, 30d)"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """Returns memes ranked by real-time engagement and popularity, updated hourly."""
    try:
        return get_trending_catalog(
            db=db,
            category=category,
            period=period,
            limit=limit,
            offset=offset,
        )
    except ValueError as e:
        err_code = str(e)
        if err_code == "INVALID_CATEGORY":
            raise HTTPException(status_code=400, detail="Invalid category. Must be one of: all, work, gaming, relationships, tech, sports, tv, wholesome")
        elif err_code == "INVALID_PERIOD":
            raise HTTPException(status_code=400, detail="Invalid period. Must be one of: 24h, 7d, 30d")
        else:
            raise HTTPException(status_code=400, detail=str(e))
