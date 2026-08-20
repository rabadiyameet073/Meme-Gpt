#!/usr/bin/env python3
"""
MemeGPT — Sync Popularity Scores Script
Specification: 06_Database/Recovery.md & 05_AI_System/Scoring_Logic.md
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database import get_db
from app.services.rerank_service import recalculate_all_popularity_scores


def main():
    print("\n=== Recalculating and Syncing Popularity Scores ===")
    with next(get_db()) as db:
        res = recalculate_all_popularity_scores(db)
        print(f"Status: {res.get('status')}")
        print(f"Updated Memes Count: {res.get('updated_count')}")
        print("✓ Popularity scores synced.")


if __name__ == "__main__":
    main()
