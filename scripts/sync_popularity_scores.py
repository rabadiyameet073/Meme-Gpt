#!/usr/bin/env python3
"""
MemeGPT — Recalculate & Sync Popularity Scores

Specification: 05_AI_System/Scoring_Logic.md, 03_Backend/Background_Jobs.md,
06_Database/Recovery.md (recovery step 4 re-syncs the scores from this script).

This is the "Popularity update" scheduled job (daily 4:00 UTC). For every meme
it aggregates the trailing feedback window through
`rerank_service.calculate_popularity_score` and persists the normalised result
to `memes.popularity_score`, which is the column the composite scorer's
popularity term and the fallback catalog ordering read.

Usage:
    python scripts/sync_popularity_scores.py [--window-days 30]
"""

import argparse
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.jobs import recalculate_popularity_scores  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("memegpt.cron.popularity")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Recalculate persisted popularity scores")
    parser.add_argument(
        "--window-days",
        type=int,
        default=30,
        help="Trailing feedback window in days (default: 30)",
    )
    args = parser.parse_args(argv)

    result = recalculate_popularity_scores(window_days=args.window_days)

    if result.get("status") != "success":
        logger.error("Popularity recalculation failed: %s", result)
        return 1

    print(
        "[OK] popularity synced: "
        f"{result['updated_memes']}/{result['total_memes']} memes updated, "
        f"{result['with_recent_feedback']} had feedback inside "
        f"{result['window_days']}d window"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
