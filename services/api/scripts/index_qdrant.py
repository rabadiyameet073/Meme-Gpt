"""
Step 4 of ML Pipeline — Create Qdrant collection and upsert meme embeddings.
Collection: 'memes' with 3 named vector spaces: text (384), image (512), combined (896).

Usage:
  python scripts/index_qdrant.py
  python scripts/index_qdrant.py --new-only
"""
import argparse
import json
import os
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

COLLECTION_NAME = "memes"


def get_client():
    from qdrant_client import QdrantClient
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_key = os.getenv("QDRANT_API_KEY") or None
    client = QdrantClient(url=url, api_key=api_key)
    print(f"Connected to Qdrant: {url}")
    return client


def create_collection(client) -> None:
    """Create meme collection with 3 named vector spaces."""
    from qdrant_client.models import VectorParams, Distance, HnswConfigDiff
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "text": VectorParams(
                size=384,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
            ),
            "image": VectorParams(size=512, distance=Distance.COSINE),
            "combined": VectorParams(
                size=896,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=32, ef_construct=200),
            ),
        },
    )
    print(f"✓ Created collection '{COLLECTION_NAME}'")


def index_memes(client, memes: list, batch_size: int = 100) -> None:
    from qdrant_client.models import PointStruct

    for start in range(0, len(memes), batch_size):
        batch = memes[start:start + batch_size]
        points = []
        for meme in batch:
            point_id = abs(hash(meme["id"])) % (10 ** 18)
            text_emb = meme.get("text_embedding", [0.0] * 384)
            image_emb = meme.get("image_embedding", [0.0] * 512)
            combined_emb = meme.get("combined_embedding", [0.0] * 896)

            slug = meme.get("slug") or meme.get("name", "meme").lower().replace(" ", "-")

            point = PointStruct(
                id=point_id,
                vectors={"text": text_emb, "image": image_emb, "combined": combined_emb},
                payload={
                    "meme_id": meme["id"],
                    "name": meme["name"],
                    "slug": slug,
                    "emotions": meme.get("emotions", []),
                    "situations": meme.get("situations", []),
                    "keywords": meme.get("keywords", []),
                    "meme_type": meme.get("meme_type", "reaction"),
                    "source": meme.get("source", "unknown"),
                    "image_url": meme.get("image_url", ""),
                    "gif_url": meme.get("gif_url", ""),
                    "mp4_url": meme.get("mp4_url", ""),
                    "thumb_url": meme.get("thumb_url", ""),
                    "has_gif": bool(meme.get("gif_url")),
                    "has_video": bool(meme.get("mp4_url")),
                    "nsfw": meme.get("nsfw", False),
                    "popularity_score": min(1.0, meme.get("score", 0) / 10000),
                    "view_count": 0,
                    "download_count": 0,
                },
            )
            points.append(point)

        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"  Indexed {start} – {start + len(batch)}")


def verify(client) -> None:
    from sentence_transformers import SentenceTransformer
    info = client.get_collection(COLLECTION_NAME)
    print(f"\nCollection '{COLLECTION_NAME}'")
    print(f"  Vectors: {info.vectors_count}")
    print(f"  Status:  {info.status}")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    q = "when the code finally works"
    vec = model.encode(q, normalize_embeddings=True).tolist()
    results = client.search(collection_name=COLLECTION_NAME, query_vector=("text", vec), limit=3)
    print(f"\nTest search: '{q}'")
    for r in results:
        print(f"  Score: {r.score:.3f} | {r.payload.get('name')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new-only", action="store_true", help="Only upsert new memes")
    args = parser.parse_args()

    emb_file = EMBEDDINGS_DIR / "memes_with_embeddings.json"
    if not emb_file.exists():
        print(f"✗ No embeddings at {emb_file}")
        print("  Run: python scripts/generate_embeddings.py first")
        sys.exit(1)

    with open(emb_file, "r") as f:
        memes = json.load(f)

    client = get_client()

    if not args.new_only:
        create_collection(client)

    print(f"Indexing {len(memes)} memes...")
    index_memes(client, memes)
    verify(client)
    print("\n✅ Qdrant indexing complete.")


if __name__ == "__main__":
    main()
