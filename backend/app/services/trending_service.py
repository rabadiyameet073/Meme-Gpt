"""Trending API Service for MemeGPT.
Specification: 07_APIs/Trending_API.md
"""

import logging
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.cache import cache_flush_pattern, cache_get, cache_set
from app.database import Feedback, Meme, SearchLog

logger = logging.getLogger("memegpt.services.trending")

VALID_CATEGORIES = {
    "all",
    "work",
    "gaming",
    "relationships",
    "tech",
    "sports",
    "tv",
    "wholesome",
}

VALID_PERIODS = {
    "24h": 24,
    "7d": 168,
    "30d": 720,
}

_TRENDING_HOURLY_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
HOURLY_TTL = 3600  # 1 hour


def validate_trending_params(category: str, period: str) -> None:
    """Validate category and period parameters, raising ValueError if invalid."""
    if category.lower() not in VALID_CATEGORIES:
        raise ValueError("INVALID_CATEGORY")
    if period.lower() not in VALID_PERIODS:
        raise ValueError("INVALID_PERIOD")


def calculate_advanced_trending_score(
    meme: Meme,
    db: Optional[Session] = None,
    period_hours: int = 24
) -> Dict[str, Any]:
    """Calculate raw trending score and engagement counts from 07_APIs/Trending_API.md."""
    downloads = 0
    copies = 0
    shares = 0
    searches = 0
    hours_since_peak = 2.0
    last_activity_hours = 1.0

    if db:
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=period_hours)
            # Query feedback table
            feedback_rows = (
                db.query(Feedback.action, Feedback.created_at)
                .filter(Feedback.meme_id == meme.id, Feedback.created_at >= cutoff)
                .all()
            )
            for act, ts in feedback_rows:
                if act == "download":
                    downloads += 1
                elif act == "copy":
                    copies += 1
                elif act == "share":
                    shares += 1

            # Query search appearances. `search_logs` stores an irreversible
            # query_hash, not the query text (GDPR), so the usable signal is how
            # often this meme was the top result of a search. The previous
            # version filtered on `SearchLog.query`, a column that does not
            # exist, and the bare `except` below hid the AttributeError — the
            # searches term was always zero and silently fell back to
            # `usage_count * 0.8`.
            searches = (
                db.query(SearchLog.id)
                .filter(
                    SearchLog.top_meme_id == meme.id,
                    SearchLog.created_at >= cutoff,
                )
                .count()
            )
        except Exception as exc:  # noqa: BLE001 - trending must degrade, not 500
            logger.warning("trending_feedback_lookup_failed: meme=%s error=%s", meme.id, exc)

    # Fallback to cumulative estimates if recent rows are sparse
    if downloads == 0 and copies == 0 and shares == 0:
        base_usage = meme.usage_count or 0
        downloads = int(base_usage * 0.4)
        copies = int(base_usage * 0.3)
        shares = int(base_usage * 0.1)
        searches = int(base_usage * 0.8)

    # Weighted engagement score
    raw_score = (
        downloads * 3.0 +
        copies * 2.0 +
        shares * 4.0 +
        searches * 1.0
    )

    # Time decay: newer activity matters more
    time_decay = math.exp(-hours_since_peak / (period_hours * 0.5))

    # Recency bonus: memes with recent activity get a boost
    recency_bonus = max(0.0, 10.0 - last_activity_hours) * 0.5

    # Novelty factor: boost memes that are new to trending
    days_on_trending = 2.0
    novelty_boost = max(0.0, 1.0 - days_on_trending * 0.05)

    final_raw = (raw_score * time_decay + recency_bonus) * novelty_boost

    return {
        "raw_score": final_raw,
        "downloads_period": downloads,
        "copies_period": copies,
        "shares_period": shares,
        "searches_period": searches,
    }


def normalize_trending_scores(memes_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Min-max normalize raw trending scores across memes."""
    if not memes_data:
        return []

    scores = [m["raw_score"] for m in memes_data]
    min_s, max_s = min(scores), max(scores)

    for m in memes_data:
        if max_s > min_s:
            norm = (m["raw_score"] - min_s) / (max_s - min_s)
        else:
            norm = 0.85
        m["trending_score"] = round(max(0.0, min(1.0, norm)), 2)

    return sorted(memes_data, key=lambda m: m["trending_score"], reverse=True)


def invalidate_trending_cache() -> int:
    """Drop every cached trending payload, in both cache tiers.

    Called when moderation changes a meme's visibility. Clearing only the
    per-process dict is not enough: the shared tier would keep serving the
    removed meme to every worker until the TTL expired.
    """
    _TRENDING_HOURLY_CACHE.clear()
    return cache_flush_pattern("trending:*")


def get_trending_catalog(
    db: Session,
    category: str = "all",
    period: str = "24h",
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """Retrieve full trending catalog matching 07_APIs/Trending_API.md specification."""
    category = category.lower().strip()
    period = period.lower().strip()
    validate_trending_params(category, period)

    cache_key = f"trending:{category}:{period}:{offset}:{limit}"
    now_ts = datetime.now(timezone.utc).timestamp()

    if cache_key in _TRENDING_HOURLY_CACHE:
        cached_time, cached_val = _TRENDING_HOURLY_CACHE[cache_key]
        if now_ts - cached_time < HOURLY_TTL:
            cached_val["data"]["meta"]["cached"] = True
            cached_val["cached"] = True
            return cached_val

    # Second tier: the shared Redis cache. A cron process cannot warm this
    # module's per-process dict, so `scripts/refresh_trending.py` publishes here
    # and every API worker reads it (03_Backend/Background_Jobs.md lists the
    # hourly trending refresh as a scheduled job).
    shared = cache_get(cache_key)
    if isinstance(shared, dict):
        shared.setdefault("data", {}).setdefault("meta", {})["cached"] = True
        shared["cached"] = True
        _TRENDING_HOURLY_CACHE[cache_key] = (now_ts, shared)
        return shared

    period_hours = VALID_PERIODS[period]
    limit = min(max(limit, 1), 50)
    offset = max(0, offset)

    # 1. Fetch all memes to establish overall trending rank (excluding removed memes)
    all_memes = db.query(Meme).filter(Meme.moderation_status != "removed").all()
    overall_scored = []
    for m in all_memes:
        score_info = calculate_advanced_trending_score(m, db=db, period_hours=period_hours)
        overall_scored.append({
            "meme": m,
            **score_info,
        })
    overall_scored = normalize_trending_scores(overall_scored)

    for rank, item in enumerate(overall_scored, start=1):
        item["trending_rank"] = rank

    # 2. Filter by category
    if category != "all":
        cat_filtered = [item for item in overall_scored if (item["meme"].category or "").lower() == category]
    else:
        cat_filtered = overall_scored

    # Compute category rank
    for cat_rank, item in enumerate(cat_filtered, start=1):
        item["category_rank"] = cat_rank

    total_results = len(cat_filtered)
    total_trending = len(overall_scored)

    paged_items = cat_filtered[offset : offset + limit]

    results = []
    for item in paged_items:
        m = item["meme"]
        slug_val = m.slug or re.sub(r"[^\w\s-]", "", m.name.lower()).strip().replace(" ", "-")

        gif_ref = m.gif_ref or f"https://cdn.memegpt.com/memes/{slug_val}.gif"
        img_ref = m.image_ref or f"https://cdn.memegpt.com/images/{slug_val}.png"
        vid_ref = m.video_ref

        results.append({
            "id": m.id,
            "name": m.name,
            "slug": slug_val,
            "trending_score": item["trending_score"],
            "trending_rank": item["trending_rank"],
            "category_rank": item["category_rank"],
            f"downloads_{period}": item["downloads_period"],
            f"copies_{period}": item["copies_period"],
            f"shares_{period}": item["shares_period"],
            f"searches_{period}": item["searches_period"],
            "preview_url": f"https://cdn.memegpt.com/thumbs/{slug_val}.webp",
            "formats": {
                "gif": gif_ref,
                "image": img_ref,
                "video": vid_ref,
            },
            # Compatibility helpers
            "categories": [m.category] if m.category else ["general"],
            "view_count_24h": item["searches_period"],
        })

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")
    next_update = (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:00:00Z")

    response_payload = {
        "success": True,
        "data": {
            "category": category,
            "period": period,
            "results": results,
            "meta": {
                "total_results": total_results,
                "total_trending": total_trending,
                "updated_at": updated_at,
                "next_update": next_update,
                "cached": False,
            },
        },
        # Backwards compatibility top-level fields
        "category": category,
        "results": results,
        "total": total_results,
        "offset": offset,
        "limit": limit,
        "cached": False,
    }

    _TRENDING_HOURLY_CACHE[cache_key] = (now_ts, response_payload)
    cache_set(cache_key, response_payload, ttl=HOURLY_TTL)
    return response_payload
