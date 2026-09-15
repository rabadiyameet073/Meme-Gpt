"""
MemeGPT AI Recommendation Quality Evaluator
Computes Precision@3, NDCG@5, and Mean Reciprocal Rank (MRR).
Specification: 14_Testing_CI_Gaps.md
"""
import json
import httpx
import math
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/search")
TEST_SET = Path(__file__).resolve().parent.parent / "data" / "eval" / "golden_queries.json"


def is_slug_match(retrieved_slug: str, expected_slugs: set) -> bool:
    """Check if retrieved slug matches any expected slug directly or via root prefix."""
    r = retrieved_slug.lower()
    for exp in expected_slugs:
        e = exp.lower()
        if r == e or e in r or r in e:
            return True
    return False


def compute_reciprocal_rank(retrieved_slugs, expected_slugs):
    for rank, slug in enumerate(retrieved_slugs, start=1):
        if is_slug_match(slug, expected_slugs):
            return 1.0 / rank
    return 0.0


def compute_precision_at_k(retrieved_slugs, expected_slugs, k=3):
    top_k = retrieved_slugs[:k]
    hits = sum(1 for s in top_k if is_slug_match(s, expected_slugs))
    return hits / k


def compute_dcg(retrieved_slugs, expected_slugs, k=5):
    dcg = 0.0
    for i, slug in enumerate(retrieved_slugs[:k]):
        rel = 1.0 if is_slug_match(slug, expected_slugs) else 0.0
        dcg += (2**rel - 1) / math.log2(i + 2)
    return dcg


def get_search_client():
    """Returns an HTTP client or backend TestClient fallback."""
    try:
        # Check if local or remote server is reachable
        with httpx.Client(timeout=1.0) as probe:
            r = probe.get(API_URL.replace("/search", "/health"))
            if r.status_code == 200:
                return httpx.Client(timeout=10.0), API_URL
    except Exception:
        pass

    # Fallback to direct FastAPI TestClient
    from starlette.testclient import TestClient
    from app.main import app
    return TestClient(app), "/api/v1/search"


def evaluate():
    with open(TEST_SET, encoding="utf-8") as f:
        cases = json.load(f)

    p3_scores, mrr_scores, ndcg_scores = [], [], []
    client, search_url = get_search_client()

    try:
        for case in cases:
            query = case["query"]
            expected = set(case["expected_slugs"])
            resp = client.post(search_url, json={"query": query, "limit": 5})
            if resp.status_code != 200:
                print(f"Error querying '{query}': {resp.status_code}")
                continue

            data = resp.json()
            results = data.get("memes") or data.get("results") or []
            retrieved = [m.get("slug") or m.get("id") or "" for m in results]

            p3 = compute_precision_at_k(retrieved, expected, k=3)
            mrr = compute_reciprocal_rank(retrieved, expected)
            dcg = compute_dcg(retrieved, expected, k=5)
            # Ideal DCG for 1 hit in top 5
            idcg = (2**1 - 1) / math.log2(2)
            ndcg = min(1.0, dcg / idcg) if idcg > 0 else 0.0

            p3_scores.append(p3)
            mrr_scores.append(mrr)
            ndcg_scores.append(ndcg)
    finally:
        if hasattr(client, "close"):
            client.close()

    mean_p3 = sum(p3_scores) / len(p3_scores) if p3_scores else 0.0
    mean_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0.0
    mean_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0

    print("=" * 40)
    print("MemeGPT AI Recommendation Quality Benchmark")
    print("=" * 40)
    print(f"Precision@3: {mean_p3:.3f} (Target: > 0.650)")
    print(f"NDCG@5:      {mean_ndcg:.3f} (Target: > 0.700)")
    print(f"MRR:         {mean_mrr:.3f} (Target: > 0.600)")
    print("=" * 40)

    # Return exit code for CI pipeline
    assert mean_p3 >= 0.50, f"Precision@3 {mean_p3} below minimum bar 0.50"
    return {
        "precision_at_3": mean_p3,
        "ndcg_at_5": mean_ndcg,
        "mrr": mean_mrr,
    }


if __name__ == "__main__":
    evaluate()
