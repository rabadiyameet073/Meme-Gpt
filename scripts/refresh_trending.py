"""Hourly Trending Refresh Cron Script for MemeGPT.

Specification: 08_Features/Trending_System.md and 03_Backend/Background_Jobs.md.

`GET /api/v1/trending` is served by `trending_service.get_trending_catalog`,
which computes the ranking from the `memes` and `feedback` tables and memoises
the response in the shared cache layer. This job runs that same function on a
schedule so the first real visitor of every hour gets a cache hit instead of a
full recomputation.

The previous version replayed five hardcoded `sample_memes` with invented
engagement counts into a module-level dict inside this process. Nothing else
read that dict, so the cron reported success while the API kept recomputing
from scratch and the "hourly refreshed" trending claim was not backed by
anything.
"""

import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.database import Meme, SessionLocal  # noqa: E402
from app.services.trending_service import (  # noqa: E402
    VALID_CATEGORIES,
    VALID_PERIODS,
    get_trending_catalog,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.cron.trending")

# First-page window the API hands out by default.
WARM_LIMIT = 20
WARM_PERIODS = ("24h", "7d")


def run_trending_refresh() -> int:
    """Warm the shared trending cache for every category and period."""
    db = SessionLocal()
    try:
        total_memes = db.query(Meme).count()
        if total_memes == 0:
            logger.warning("trending_refresh_skipped: no memes in the database")
            print("[SKIP] trending refresh skipped: no memes in the database")
            return 0

        warmed = 0
        for period in WARM_PERIODS:
            if period not in VALID_PERIODS:
                continue
            for category in sorted(VALID_CATEGORIES):
                payload = get_trending_catalog(
                    db, category=category, period=period, limit=WARM_LIMIT, offset=0
                )
                counts = payload["data"]["meta"]["total_results"]
                warmed += 1
                logger.info(
                    "trending_warmed: category=%s period=%s results=%s",
                    category,
                    period,
                    counts,
                )

        logger.info("trending_refresh_completed: warmed_keys=%s", warmed)
        print(
            f"[OK] trending cache warmed: {warmed} category/period keys "
            f"across {total_memes} memes"
        )
        return 0
    except Exception as exc:  # noqa: BLE001 - a cron must exit non-zero to alert
        logger.error("trending_refresh_failed: %s", exc)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(run_trending_refresh())
