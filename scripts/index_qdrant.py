"""
MemeGPT — Qdrant Vector Indexing Script
Matches specifications from 05_AI_System/Vector_Database.md & AI_Pipeline.md
"""

import argparse
import json
import os
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff, PointStruct


def create_collection(client: QdrantClient, collection_name: str = "memes"):
    """Create Qdrant collection with 3 named vector spaces: text (384), image (512), combined (896)."""
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config={
            "text": VectorParams(
                size=384,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
            ),
            "image": VectorParams(
                size=512,
                distance=Distance.COSINE,
            ),
            "combined": VectorParams(
                size=896,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=32, ef_construct=200),
            ),
        },
    )
    print(f"✓ Created Qdrant collection '{collection_name}' with 3 vector spaces (text: 384, image: 512, combined: 896)")


def build_point(meme: dict) -> PointStruct:
    """Build a Qdrant PointStruct with 64-bit integer ID and 3 vector embeddings + 18 payload fields."""
    meme_id_str = str(meme.get("id", meme.get("meme_id", "")))
    int_id = abs(hash(meme_id_str)) % (10**18)

    text_vec = meme.get("text_embedding", meme.get("vector", [0.0] * 384))
    image_vec = meme.get("image_embedding", [0.0] * 512)
    combined_vec = meme.get("combined_embedding", [0.0] * 896)

    # Dimension normalization
    if len(text_vec) < 384:
        text_vec = list(text_vec) + [0.0] * (384 - len(text_vec))
    if len(image_vec) < 512:
        image_vec = list(image_vec) + [0.0] * (512 - len(image_vec))
    if len(combined_vec) < 896:
        combined_vec = list(combined_vec) + [0.0] * (896 - len(combined_vec))

    payload = {
        "meme_id": meme_id_str,
        "name": meme.get("name", "Unknown Meme"),
        "slug": meme.get("slug", meme.get("name", "").lower().replace(" ", "-")),
        "emotions": meme.get("emotions", []),
        "situations": meme.get("situations", []),
        "keywords": meme.get("keywords", []),
        "meme_type": meme.get("meme_type", "reaction"),
        "source": meme.get("source", ""),
        "image_url": meme.get("image_url", ""),
        "gif_url": meme.get("gif_url", ""),
        "mp4_url": meme.get("mp4_url", ""),
        "thumb_url": meme.get("thumb_url", ""),
        "has_gif": bool(meme.get("gif_url")),
        "has_video": bool(meme.get("mp4_url")),
        "nsfw": bool(meme.get("nsfw", False)),
        "popularity_score": float(meme.get("popularity_score", meme.get("score", 0.5))),
        "view_count": int(meme.get("view_count", 0)),
        "download_count": int(meme.get("download_count", 0)),
    }

    return PointStruct(
        id=int_id,
        vectors={
            "text": text_vec[:384],
            "image": image_vec[:512],
            "combined": combined_vec[:896],
        },
        payload=payload,
    )


def index_memes(client: QdrantClient, memes: list[dict], batch_size: int = 100, collection_name: str = "memes"):
    """Batch upsert memes into Qdrant."""
    for batch_start in range(0, len(memes), batch_size):
        batch = memes[batch_start:batch_start + batch_size]
        points = [build_point(m) for m in batch]
        client.upsert(collection_name=collection_name, points=points)
        print(f"  Indexed batch {batch_start}–{batch_start + len(batch)}")


def verify_index(client: QdrantClient, collection_name: str = "memes"):
    """Verify collection status and point count."""
    info = client.get_collection(collection_name)
    print(f"Collection: {collection_name}")
    print(f"Status: {info.status}")
    print(f"Vectors count: {getattr(info, 'vectors_count', getattr(info, 'points_count', 0))}")


def main():
    parser = argparse.ArgumentParser(description="Qdrant Indexing Tool")
    parser.add_argument("--verify", action="store_true", help="Verify existing collection index")
    parser.add_argument("--recreate", action="store_true", help="Recreate Qdrant collection")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for upserting")
    args = parser.parse_args()

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_key = os.getenv("QDRANT_API_KEY")

    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)

    if args.verify:
        verify_index(client)
    elif args.recreate:
        create_collection(client)
    else:
        create_collection(client)


if __name__ == "__main__":
    main()
