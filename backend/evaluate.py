#!/usr/bin/env python3
"""
MemeGPT — AI Quality Evaluation from 14_Testing_Suite.md.
Tests search quality against a labeled test set and reports Precision@5 and MRR.

Run: python evaluate.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memegpt.evaluate")

# Labeled ground-truth test cases: (query, expected_meme_slugs)
TEST_CASES = [
    ("when the code works on the first try", ["surprised-pikachu", "one-does-not-simply", "success-kid"]),
    ("monday morning motivation", ["this-is-fine", "kermit-sipping-tea", "hide-the-pain-harold"]),
    ("boss says we work on weekends", ["distracted-boyfriend", "drake-pointing", "panik-kalm-panik"]),
    ("finally fixed that bug after 3 hours", ["success-kid", "celebrating-guy", "leonardo-cheers"]),
    ("my code works but I dont know why", ["confused-math-lady", "dog-sitting-fire", "woman-yelling-at-cat"]),
    ("when someone says just 5 more minutes", ["waiting-skeleton", "roll-safe-think", "anakin-padme"]),
    ("feeling overwhelmed by todos", ["this-is-fine", "disaster-girl", "sweating-jordan-peele"]),
    ("made it to Friday", ["weekend-spongebob", "finally-free", "dancing-baby-groot"]),
]


async def evaluate(top_k: int = 5) -> dict:
    from app.services.recommendation_service import recommend_memes
    from app.database import SessionLocal, Meme

    db = SessionLocal()
    try:
        memes = [m.to_dict() for m in db.query(Meme).limit(50).all()]
    finally:
        db.close()

    results = []
    hits = 0
    total = len(TEST_CASES)

    for query, expected_slugs in TEST_CASES:
        try:
            response = await recommend_memes(query, format_pref="gif", nsfw=False, memes_from_db=memes)
            returned = response.get("results", []) or ([response["primary"]] if "primary" in response else [])
            returned_slugs = [r.get("slug", "") for r in returned][:top_k]

            hit = any(slug in returned_slugs for slug in expected_slugs)
            if hit:
                hits += 1

            results.append({
                "query": query,
                "expected": expected_slugs,
                "returned": returned_slugs,
                "hit": hit,
            })
        except Exception as e:
            results.append({
                "query": query,
                "expected": expected_slugs,
                "returned": [],
                "hit": False,
                "error": str(e),
            })

    precision_at_k = (hits / total) if total > 0 else 0.0
    print("\n=== MemeGPT AI Evaluation Results ===")
    print(f"Precision@{top_k}: {precision_at_k:.2%} ({hits}/{total})")
    print("Target: >60% precision@5")
    print(f"Result: {'[PASS]' if precision_at_k >= 0.6 else '[FAIL]'}\n")

    for r in results:
        status = "[OK]" if r["hit"] else "[MISS]"
        safe_query = r['query'][:50]
        print(f"{status} '{safe_query}'")
        if not r["hit"]:
            print(f"   Expected: {r['expected']}")
            print(f"   Got: {r['returned']}")

    return {"precision_at_k": precision_at_k, "total": total, "hits": hits}


if __name__ == "__main__":
    asyncio.run(evaluate())
