"""
Step 5 of ML Pipeline — Verify the Qdrant index is working correctly.
Run after index_qdrant.py to confirm search is functional.

Usage:
  python scripts/verify_index.py
"""
import os
import sys

TEST_QUERIES = [
    ("when code works on first try and you don't know why", ["success", "surprise", "programming"]),
    ("Monday morning feeling", ["monday", "tired", "relatable"]),
    ("my boss emailed at 11pm on a Friday", ["work", "frustration", "office"]),
    ("I fixed a bug that took me 3 days in 5 minutes", ["programming", "joy", "success"]),
]


def main():
    try:
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Run: pip install qdrant-client sentence-transformers")
        sys.exit(1)

    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_key = os.getenv("QDRANT_API_KEY") or None

    try:
        client = QdrantClient(url=url, api_key=api_key, timeout=5)
        info = client.get_collection("memes")
        print(f"✓ Qdrant connected: {url}")
        print(f"  Vectors: {info.vectors_count}")
    except Exception as e:
        print(f"✗ Qdrant unavailable: {e}")
        print("  Start with: docker run -p 6333:6333 qdrant/qdrant")
        sys.exit(1)

    print("\nLoading MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("\nRunning test queries:")
    all_pass = True
    for query, expected_tags in TEST_QUERIES:
        vec = model.encode(query, normalize_embeddings=True).tolist()
        results = client.search(collection_name="memes", query_vector=("text", vec), limit=3)

        if results:
            top = results[0]
            name = top.payload.get("name", "Unknown")
            score = top.score
            status = "✓" if score > 0.5 else "⚠"
            if score < 0.5:
                all_pass = False
            print(f"  {status} '{query[:50]}...'")
            print(f"     → {name} (score: {score:.3f})")
        else:
            all_pass = False
            print(f"  ✗ No results for: '{query}'")

    print()
    if all_pass:
        print("✅ All test queries returned results with acceptable scores.")
    else:
        print("⚠  Some queries returned low scores — consider re-running the pipeline.")
        print("   Step 1: python scripts/download_datasets.py")
        print("   Step 2: python scripts/preprocess_memes.py")
        print("   Step 3: python scripts/generate_embeddings.py")
        print("   Step 4: python scripts/index_qdrant.py")


if __name__ == "__main__":
    main()
