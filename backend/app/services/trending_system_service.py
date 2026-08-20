"""Trending System Service for MemeGPT.
Specification: 08_Features/Trending_System.md
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("memegpt.services.trending_system")

SUPPORTED_TRENDING_CATEGORIES = [
    "all",
    "work",
    "gaming",
    "relationships",
    "tech",
    "sports",
]

_CATEGORY_TRENDING_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
CATEGORY_CACHE_TTL_SECONDS = 300  # 5 minutes in-memory TTL


def calculate_trending_velocity_score(feedback_counts: Dict[str, int]) -> float:
    """Calculate 24-hour engagement velocity score from 08_Features/Trending_System.md.
    
    Formula:
        raw = (
            views * 0.1 +
            clicks * 0.5 +
            downloads * 2.0 +
            shares * 3.0 +
            thumbs_up * 2.0
        )
        return min(1.0, raw / 1000)
    """
    views = max(0, int(feedback_counts.get("views", 0)))
    clicks = max(0, int(feedback_counts.get("clicks", 0)))
    downloads = max(0, int(feedback_counts.get("downloads", 0)))
    shares = max(0, int(feedback_counts.get("shares", 0)))
    thumbs_up = max(0, int(feedback_counts.get("thumbs_up", 0)))

    raw = (
        views * 0.1
        + clicks * 0.5
        + downloads * 2.0
        + shares * 3.0
        + thumbs_up * 2.0
    )
    return round(min(1.0, raw / 1000.0), 4)


def get_trending_tier_info(score: float) -> Dict[str, Any]:
    """Classify trending score into visual display tiers.
    
    Tiers:
        - 0.80–1.00: 🔥 Hot (Top of trending)
        - 0.50–0.79: 📈 Rising (Mid-trending)
        - 0.20–0.49: ➡️ Steady (Lower trending)
        - <0.20: Below threshold
    """
    clamped = max(0.0, min(1.0, float(score)))
    if clamped >= 0.80:
        return {
            "tier": "hot",
            "label": "🔥 Hot",
            "display": "Top of trending",
            "is_visible": True,
            "score": clamped,
        }
    elif clamped >= 0.50:
        return {
            "tier": "rising",
            "label": "📈 Rising",
            "display": "Mid-trending",
            "is_visible": True,
            "score": clamped,
        }
    elif clamped >= 0.20:
        return {
            "tier": "steady",
            "label": "➡️ Steady",
            "display": "Lower trending",
            "is_visible": True,
            "score": clamped,
        }
    else:
        return {
            "tier": "below_threshold",
            "label": "Below Threshold",
            "display": "Not shown",
            "is_visible": False,
            "score": clamped,
        }


def refresh_category_trending_cache(
    memes_list: Optional[List[Dict[str, Any]]] = None,
    categories: Optional[List[str]] = None,
    limit: int = 50,
) -> Dict[str, int]:
    """Refresh top 50 memes per category into trending memory cache."""
    cats = categories or SUPPORTED_TRENDING_CATEGORIES
    memes = memes_list or []
    now = datetime.now(timezone.utc).timestamp()
    counts = {}

    for cat in cats:
        cat_lower = cat.lower()
        if cat_lower == "all":
            cat_memes = list(memes)
        else:
            cat_memes = [m for m in memes if m.get("category", "").lower() == cat_lower]

        scored_items = []
        for m in cat_memes:
            f_counts = m.get("feedback", {})
            score = calculate_trending_velocity_score(f_counts)
            tier_info = get_trending_tier_info(score)
            scored_items.append({
                "id": m.get("id"),
                "name": m.get("name"),
                "slug": m.get("slug") or m.get("id"),
                "category": m.get("category", "general"),
                "preview_url": m.get("preview_url") or f"https://cdn.memegpt.com/thumbs/{m.get('id')}.webp",
                "trending_score": score,
                "tier": tier_info["tier"],
                "tier_label": tier_info["label"],
            })

        scored_items.sort(key=lambda x: x["trending_score"], reverse=True)
        top_n = scored_items[:limit]
        _CATEGORY_TRENDING_CACHE[cat_lower] = (now, top_n)
        counts[cat_lower] = len(top_n)

    return counts


def get_cached_category_trending(
    category: str = "all",
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Retrieve cached trending memes for a given category."""
    cat_lower = category.lower()
    now = datetime.now(timezone.utc).timestamp()

    if cat_lower in _CATEGORY_TRENDING_CACHE:
        cached_time, cached_items = _CATEGORY_TRENDING_CACHE[cat_lower]
        if now - cached_time < CATEGORY_CACHE_TTL_SECONDS:
            return cached_items[:limit]

    return []
