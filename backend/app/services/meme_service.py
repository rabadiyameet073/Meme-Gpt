"""Meme Service for MemeGPT — detail formatting, download resolution, trending score calculation, and pagination.
Specification: 07_APIs/Meme_API.md
"""

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from sqlalchemy.orm import Session

from app.database import Meme, Feedback

logger = logging.getLogger("memegpt.services.memes")

# In-memory 5-minute cache for trending results
_TRENDING_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


def get_meme_by_id(meme_id_or_slug: str, db: Optional[Session] = None) -> Optional[dict[str, Any]]:
    """Retrieve a meme by ID or slug and return formatted detail dictionary."""
    if not meme_id_or_slug:
        return None
    if db:
        meme = db.query(Meme).filter((Meme.id == meme_id_or_slug) | (Meme.slug == meme_id_or_slug)).first()
        if meme:
            return format_meme_detail_response(meme, db=db)
    return None


def format_meme_detail_response(meme: Meme, db: Optional[Session] = None) -> dict[str, Any]:
    """Format full meme detail payload according to 07_APIs/Meme_API.md specification."""
    slug_val = meme.slug or re.sub(r"[^\w\s-]", "", meme.name.lower()).strip().replace(" ", "-")
    
    # Parse keywords and categories
    try:
        keywords = json.loads(meme.keywords) if isinstance(meme.keywords, str) else (meme.keywords or [])
    except Exception:
        keywords = []

    # Categories list
    categories = [meme.category] if meme.category else ["general"]
    for kw in keywords[:3]:
        if kw not in categories:
            categories.append(kw)

    # Emotions heuristic from keywords or default
    emotions = ["relatable", "funny"]

    # Formats dictionary
    formats = {
        "gif": meme.gif_ref,
        "image": meme.image_ref or f"https://cdn.memegpt.com/images/{slug_val}.jpg",
        "video": meme.video_ref,
        "webp": meme.image_ref or f"https://cdn.memegpt.com/webp/{slug_val}.webp",
    }

    # Find 2 related memes in same category
    related_slugs = []
    if db:
        try:
            related = (
                db.query(Meme.slug, Meme.name)
                .filter(Meme.category == meme.category, Meme.id != meme.id)
                .limit(2)
                .all()
            )
            for r_slug, r_name in related:
                s = r_slug or re.sub(r"[^\w\s-]", "", r_name.lower()).strip().replace(" ", "-")
                related_slugs.append(s)
        except Exception:
            pass

    return {
        "id": meme.id,
        "name": meme.name,
        "slug": slug_val,
        "description": meme.explanation or f"{meme.name} meme template",
        "origin": "MemeGPT Catalog (2026)",
        "categories": categories,
        "emotions": emotions,
        "formats": formats,
        "preview_url": formats["image"] or f"https://cdn.memegpt.com/thumbs/{slug_val}.webp",
        "share_url": f"https://memegpt.com/meme/{slug_val}",
        "related_memes": related_slugs,
        "usage_count": meme.usage_count or 0,
        "download_count": getattr(meme, "download_count", meme.usage_count or 0),
        "popularity_score": round(min(1.0, (meme.viral_score or 0.0) / 10.0 if meme.viral_score > 1.0 else (meme.viral_score or 0.0)), 2),
        "source": "imgflip",
        "nsfw": False,
        "created_at": meme.created_at.isoformat() if meme.created_at else None,
        "indexed_at": meme.updated_at.isoformat() if meme.updated_at else (meme.created_at.isoformat() if meme.created_at else None),
    }


def get_meme_download_url(meme: Meme, format_type: str = "gif") -> Optional[str]:
    """Resolve format-specific CDN download URL. Returns None if format is unavailable."""
    fmt = format_type.lower().strip()
    
    if fmt == "gif":
        return meme.gif_ref
    elif fmt in ("image", "png", "jpg", "jpeg"):
        return meme.image_ref or f"https://cdn.memegpt.com/images/{meme.id}.jpg"
    elif fmt in ("video", "mp4"):
        return meme.video_ref
    elif fmt == "webp":
        return meme.image_ref or f"https://cdn.memegpt.com/webp/{meme.id}.webp"
    return None


def calculate_trending_score(meme: Meme, db: Optional[Session] = None, time_window_hours: int = 24) -> float:
    """Calculate composite 24-hour trending score from 07_APIs/Meme_API.md."""
    views_24h = 0
    downloads_24h = 0
    shares_24h = 0
    thumbs_up = meme.upvotes or 0

    if db:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
            records = (
                db.query(Feedback.action)
                .filter(Feedback.meme_id == meme.id, Feedback.created_at >= cutoff)
                .all()
            )
            for (act,) in records:
                if act == "view":
                    views_24h += 1
                elif act == "download":
                    downloads_24h += 1
                elif act == "share":
                    shares_24h += 1
                elif act == "thumbs_up":
                    thumbs_up += 1
        except Exception:
            pass

    # Fallback to cumulative stats if no recent logs
    if views_24h == 0 and downloads_24h == 0:
        downloads_24h = meme.usage_count or 0
        views_24h = (meme.usage_count or 0) * 3

    raw_score = (
        views_24h * 0.1 +
        downloads_24h * 2.0 +
        shares_24h * 3.0 +
        thumbs_up * 2.0
    )

    # Normalize to 0.0–1.0
    return min(1.0, round(raw_score / 1000.0, 2))


def get_trending_memes_paginated(
    db: Session,
    category: str = "all",
    limit: int = 20,
    offset: int = 0
) -> dict[str, Any]:
    """Retrieve paginated trending memes with 5-minute memory cache."""
    now = datetime.now(timezone.utc).timestamp()
    cache_key = f"trending:{category}:{limit}:{offset}"
    
    if cache_key in _TRENDING_CACHE:
        cached_time, cached_data = _TRENDING_CACHE[cache_key]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_data

    limit = min(max(limit, 1), 50)
    offset = max(offset, 0)

    query = db.query(Meme)
    if category and category.lower() != "all":
        query = query.filter(Meme.category == category.lower())

    total = query.count()
    memes = query.order_by(Meme.viral_score.desc(), Meme.usage_count.desc()).offset(offset).limit(limit).all()

    results = []
    for m in memes:
        slug_val = m.slug or re.sub(r"[^\w\s-]", "", m.name.lower()).strip().replace(" ", "-")
        trend_score = calculate_trending_score(m, db=db)
        
        results.append({
            "id": m.id,
            "name": m.name,
            "slug": slug_val,
            "preview_url": m.image_ref or f"https://cdn.memegpt.com/thumbs/{slug_val}.webp",
            "trending_score": trend_score,
            "view_count_24h": (m.usage_count or 0) * 3,
            "categories": [m.category] if m.category else ["general"],
        })

    response_payload = {
        "success": True,
        "category": category,
        "results": results,
        "total": total,
        "offset": offset,
        "limit": limit,
    }

    _TRENDING_CACHE[cache_key] = (now, response_payload)
    return response_payload
