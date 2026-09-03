"""
MemeGPT — Reindex all memes from SQLite to Qdrant.
Run this whenever you add new memes to the DB.
Specification: 01_Qdrant_Setup_And_Indexing.md & 04_Meme_Data_Pipeline.md
"""
import os
import sys
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("reindex")

from app.database import SessionLocal, Meme
from app.services.embedding_service import embed_text, load_models
from app.services.search_service import get_qdrant_client, create_qdrant_collection, COLLECTION_NAME, _meme_id_to_int


def build_meme_text(meme) -> str:
    """Build the text representation of a meme for embedding."""
    parts = []
    if meme.name:
        parts.append(meme.name)
    if hasattr(meme, 'explanation') and meme.explanation:
        parts.append(meme.explanation)
    if hasattr(meme, 'dialogue') and meme.dialogue:
        parts.append(meme.dialogue)
    if meme.category:
        parts.append(f"category: {meme.category}")
    if meme.emotion:
        parts.append(f"emotion: {meme.emotion}")
    if hasattr(meme, 'keywords') and meme.keywords:
        kws = meme.keywords if isinstance(meme.keywords, list) else []
        parts.append(f"keywords: {', '.join(kws[:10])}")
    return " | ".join(parts) or meme.name or "meme"


def main():
    logger.info("Loading ML models...")
    load_models()

    logger.info("Connecting to Qdrant...")
    client = get_qdrant_client()
    if not client:
        logger.error("❌ Cannot connect to Qdrant. Check QDRANT_URL and QDRANT_API_KEY in .env")
        return

    logger.info("Creating collection (if not exists)...")
    create_qdrant_collection(recreate=False)

    logger.info("Loading memes from SQLite...")
    db = SessionLocal()
    memes = db.query(Meme).all()
    logger.info(f"Found {len(memes)} memes to index")
    db.close()

    if not memes:
        logger.warning("No memes found in DB. Run seed script first.")
        return

    from qdrant_client.models import PointStruct

    BATCH_SIZE = 50
    total = 0

    for i in range(0, len(memes), BATCH_SIZE):
        batch = memes[i:i + BATCH_SIZE]
        points = []

        for meme in batch:
            try:
                text = build_meme_text(meme)
                vector = embed_text(text)

                payload = {
                    "meme_id": str(meme.id),
                    "name": meme.name or "",
                    "slug": meme.slug or str(meme.id),
                    "category": meme.category or "",
                    "categories": [meme.category] if meme.category else ["general"],
                    "emotion": meme.emotion or "",
                    "emotions": [meme.emotion] if meme.emotion else [],
                    "format": meme.format or "image",
                    "image_url": meme.image_url or "",
                    "gif_url": getattr(meme, "gif_url", "") or "",
                    "thumb_url": getattr(meme, "thumb_url", "") or meme.image_url or "",
                    "usage_count": meme.usage_count or 0,
                    "is_nsfw": meme.is_nsfw if hasattr(meme, "is_nsfw") else False,
                }

                point_id = _meme_id_to_int(meme.id)
                points.append(PointStruct(
                    id=point_id,
                    vector={"text": vector},
                    payload=payload
                ))
            except Exception as e:
                logger.warning(f"Failed to index meme {meme.id}: {e}")

        if points:
            try:
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                total += len(points)
                logger.info(f"Indexed {total}/{len(memes)} memes...")
            except Exception as e:
                logger.error(f"Error upserting batch into Qdrant: {e}")

    logger.info(f"✅ Done! Indexed {total} memes into Qdrant.")

    # Verify
    try:
        info = client.get_collection(COLLECTION_NAME)
        logger.info(f"Qdrant collection now has {info.vectors_count} vectors")
    except Exception as e:
        logger.warning(f"Could not fetch collection stats: {e}")


if __name__ == "__main__":
    main()
