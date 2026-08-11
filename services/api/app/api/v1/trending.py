"""GET /api/v1/trending — Trending memes, updated hourly. Cached 30 min."""
from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.meme import MemeResult, MemeFormats
from app.services.cdn_service import cdn_service
from app.core.cache import cache_service

router = APIRouter()

VALID_CATEGORIES = ["all", "work", "gaming", "relationship", "tech", "general", "coding", "exam"]


@router.get("/trending")
async def get_trending(
    category: str = Query(default="all", description="Filter by category"),
    limit: int = Query(default=20, ge=1, le=50),
):
    """
    Returns trending memes updated hourly.
    Categories: all | work | gaming | relationship | tech | general | coding | exam
    """
    cat = category.lower() if category.lower() in VALID_CATEGORIES else "all"
    cache_key = f"trending:{cat}:{limit}"

    cached = cache_service.get(cache_key)
    if cached:
        return cached

    # Load from local index or Qdrant
    results = _get_trending_from_index(cat, limit)

    # Cache for 30 minutes
    cache_service.set(cache_key, results, ttl=1800)
    return results


def _get_trending_from_index(category: str, limit: int) -> list:
    from app.services.search_service import search_service

    memes = search_service._local_index or []
    if category != "all":
        memes = [
            m for m in memes
            if category in (m.get("categories", [m.get("category", "")])) or
               category == m.get("category", "")
        ]

    # Sort by popularity then usage
    memes = sorted(
        memes,
        key=lambda m: (m.get("popularity_score", 0), m.get("usage_count", 0)),
        reverse=True,
    )[:limit]

    results = []
    for meme in memes:
        slug = meme.get("slug") or meme.get("name", "meme").lower().replace(" ", "-")
        formats_dict = cdn_service.resolve_formats(meme)
        results.append({
            "id": meme.get("id", slug),
            "name": meme.get("name", slug),
            "slug": slug,
            "categories": meme.get("categories", [meme.get("category", "general")]),
            "emotions": meme.get("emotions", []),
            "formats": formats_dict,
            "popularity_score": meme.get("popularity_score", 0.0),
            "usage_count": meme.get("usage_count", meme.get("usageCount", 0)),
        })
    return results
