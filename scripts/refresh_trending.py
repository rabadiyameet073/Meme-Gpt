"""Hourly Trending Refresh Cron Script for MemeGPT.
Specification: 08_Features/Trending_System.md
"""

import sys
import logging
from typing import List, Dict, Any

from app.services.trending_system_service import (
    SUPPORTED_TRENDING_CATEGORIES,
    refresh_category_trending_cache,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.cron.trending")


def run_hourly_trending_refresh() -> int:
    """Execute hourly refresh across all categories and cache top 50."""
    logger.info("Starting hourly trending memes calculation...")
    
    # Mock/Seed database meme sample for standalone cron executions
    sample_memes: List[Dict[str, Any]] = [
        {
            "id": "meme_001",
            "name": "This Is Fine",
            "category": "work",
            "feedback": {"views": 1200, "clicks": 300, "downloads": 150, "shares": 90, "thumbs_up": 80},
        },
        {
            "id": "meme_002",
            "name": "Drake Hotline Bling",
            "category": "all",
            "feedback": {"views": 2000, "clicks": 500, "downloads": 200, "shares": 120, "thumbs_up": 100},
        },
        {
            "id": "meme_003",
            "name": "Distracted Boyfriend",
            "category": "relationships",
            "feedback": {"views": 800, "clicks": 200, "downloads": 80, "shares": 60, "thumbs_up": 50},
        },
        {
            "id": "meme_004",
            "name": "Gamer Rage Quit",
            "category": "gaming",
            "feedback": {"views": 1500, "clicks": 400, "downloads": 180, "shares": 110, "thumbs_up": 90},
        },
        {
            "id": "meme_005",
            "name": "Programmer 3AM Bug",
            "category": "tech",
            "feedback": {"views": 1100, "clicks": 350, "downloads": 140, "shares": 85, "thumbs_up": 75},
        },
    ]

    result = refresh_category_trending_cache(memes_list=sample_memes, categories=SUPPORTED_TRENDING_CATEGORIES, limit=50)
    logger.info(f"Trending refreshed for {len(result)} categories: {result}")
    print(f"Trending refreshed for {len(result)} categories")
    return 0


if __name__ == "__main__":
    sys.exit(run_hourly_trending_refresh())
