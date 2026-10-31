"""
MemeGPT — Vector Index Verification Script
Matches specifications from 06_Database/Backup.md & 05_AI_System/Vector_Database.md
"""

import json
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.search_service import (
    get_qdrant_client,
    verify_vector_index,
    search,
)


def main() -> int:
    client = get_qdrant_client()
    print("=== MemeGPT Vector Index Verification ===")

    diag = verify_vector_index(client=client, collection_name="memes")
    print(f"Collection: {diag.get('collection_name', 'memes')}")
    print(f"Connection Status: {diag.get('status', 'unknown')}")
    points = diag.get("points_count", diag.get("vectors_count", 0)) or 0
    print(f"Points / Vectors Count: {points}")

    # This script is the post-reindex gate in .github/workflows/weekly_reindex.yml.
    # It used to print "completed successfully" and exit 0 no matter what, so a
    # run that indexed nothing still reported green.
    if not diag.get("is_connected") or diag.get("status") in {"error", "unavailable"}:
        print("\n[FAIL] Qdrant is unreachable — the index cannot be verified.", file=sys.stderr)
        return 1
    if points == 0:
        print("\n[FAIL] The collection is empty — nothing was indexed.", file=sys.stderr)
        return 1

    # Run a test search query
    test_query = "when the code finally works"
    print(f"\nRunning benchmark test query: '{test_query}'...")

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_vector = model.encode(test_query, normalize_embeddings=True).tolist()
    except Exception:
        # Fallback test vector
        test_vector = [0.05] * 384

    results = search(
        query_vector=test_vector,
        vector_name="text",
        top_k=3,
        score_threshold=0.30,
    )

    print(f"Retrieved {len(results)} top candidate matches:")
    for idx, r in enumerate(results, 1):
        meme = r.get("meme", {})
        score = r.get("score", 0.0)
        name = meme.get("name", "Unknown")
        print(f"  {idx}. Score: {score:.3f} | {name}")

    if not results:
        print("\n[FAIL] A benchmark query returned no candidates.", file=sys.stderr)
        return 1

    print(f"\n[OK] Index verified: {points} points, {len(results)} candidates returned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
