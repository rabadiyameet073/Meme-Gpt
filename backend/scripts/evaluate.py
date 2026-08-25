#!/usr/bin/env python3
"""
MemeGPT — Offline Search Quality & Latency Evaluation.
Measures MRR (Mean Reciprocal Rank), nDCG@5, and p95 latency.

Run: python scripts/evaluate.py
"""

import asyncio
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Test dataset with gold standard meme IDs
BENCHMARK_DATASET = [
    {
        "query": "when the code compiles on first try and tests pass",
        "expected_slugs": ["success-kid", "roll-safe-think-about-it"],
    },
    {
        "query": "everything is burning down in production at 3am",
        "expected_slugs": ["this-is-fine", "thak-gaya-hu-bhai", "bhai-tu-toh-gaya"],
    },
    {
        "query": "when someone is shocked by an obvious consequence of their actions",
        "expected_slugs": ["surprised-pikachu"],
    },
    {
        "query": "comparing two frameworks and clearly preferring the new one",
        "expected_slugs": ["drake-pointing", "distracted-boyfriend"],
    },
    {
        "query": "big brain smart moves escalating to galaxy level",
        "expected_slugs": ["expanding-brain", "roll-safe-think-about-it"],
    },
]


def dcg_at_k(relevance_scores: list[int], k: int = 5) -> float:
    """Calculate Discounted Cumulative Gain at rank k."""
    dcg = 0.0
    for i, rel in enumerate(relevance_scores[:k], 1):
        dcg += (2**rel - 1) / math.log2(i + 1)
    return dcg


def ndcg_at_k(relevance_scores: list[int], k: int = 5) -> float:
    """Calculate Normalized Discounted Cumulative Gain at rank k."""
    dcg = dcg_at_k(relevance_scores, k)
    ideal_scores = sorted(relevance_scores, reverse=True)
    idcg = dcg_at_k(ideal_scores, k)
    return (dcg / idcg) if idcg > 0 else 0.0


async def evaluate_pipeline():
    from app.services.recommendation_service import recommend
    from app.database import SessionLocal, Meme

    db = SessionLocal()
    try:
        memes = [m.to_dict() for m in db.query(Meme).all()]
    finally:
        db.close()

    print(f"Loaded {len(memes)} memes for evaluation.")
    print("-" * 60)

    reciprocal_ranks = []
    ndcg_scores = []
    latencies = []

    for item in BENCHMARK_DATASET:
        query = item["query"]
        expected = set(item["expected_slugs"])

        start = time.perf_counter()
        result = await recommend(user_text=query, memes_from_db=memes)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        results = result.get("results") or result.get("topFive") or []
        retrieved_slugs = [r.get("slug") or r.get("id") for r in results]

        # Calculate Reciprocal Rank
        rr = 0.0
        for rank, slug in enumerate(retrieved_slugs, 1):
            if slug in expected:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        # Calculate nDCG@5
        rel_scores = [1 if slug in expected else 0 for slug in retrieved_slugs[:5]]
        score_ndcg = ndcg_at_k(rel_scores, k=5)
        ndcg_scores.append(score_ndcg)

        print(f"Query: '{query[:45]}...'")
        print(f"  Latency: {elapsed_ms:.1f}ms | RR: {rr:.2f} | nDCG@5: {score_ndcg:.2f}")

    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0
    avg_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0

    print("=" * 60)
    print("SEARCH QUALITY BENCHMARK RESULTS:")
    print(f"  Mean Reciprocal Rank (MRR):  {mrr:.3f}")
    print(f"  nDCG@5:                       {avg_ndcg:.3f}")
    print(f"  p50 Latency:                  {p50:.1f}ms")
    print(f"  p95 Latency:                  {p95:.1f}ms")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(evaluate_pipeline())
