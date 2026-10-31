#!/usr/bin/env python3
"""
MemeGPT — Qdrant Indexer Script.

CLI script for indexing database memes into Qdrant cloud vector database.
Can be scheduled via Windows Task Scheduler or cron.

Usage:
    python scripts/index_to_qdrant.py [--limit 500] [--recreate] [--skip-images]
    python scripts/index_to_qdrant.py --verify

``--verify`` is the reconciliation check: it compares the three places the corpus
size is tracked (the database, ``data/embeddings.json`` and the live Qdrant
collection) and exits non-zero on drift. Before it existed the repository could
hold 195 DB rows, 142 cached embeddings and 179 vector points simultaneously
without any tool noticing.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add backend root to path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from generate_embeddings import index_memes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("index_to_qdrant")

EMBEDDINGS_CACHE = backend_root / "data" / "embeddings.json"


def _db_counts() -> dict:
    from app.database import SessionLocal, Meme as MemeModel
    from app.services.search_service import HIDDEN_MODERATION_STATUSES

    session = SessionLocal()
    try:
        total = session.query(MemeModel).count()
        hidden = (
            session.query(MemeModel)
            .filter(MemeModel.moderation_status.in_(sorted(HIDDEN_MODERATION_STATUSES)))
            .count()
        )
        indexed = session.query(MemeModel).filter(MemeModel.indexed_at.isnot(None)).count()
        return {"total": total, "hidden": hidden, "indexed_at": indexed}
    finally:
        session.close()


def _cache_count() -> int | None:
    if not EMBEDDINGS_CACHE.exists():
        return None
    try:
        payload = json.loads(EMBEDDINGS_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return -1
    return len(payload) if isinstance(payload, list) else -1


def _qdrant_count() -> int | None:
    from app.services.search_service import get_qdrant_client, COLLECTION_NAME

    client = get_qdrant_client()
    if client is None:
        return None
    try:
        info = client.get_collection(COLLECTION_NAME)
    except Exception as exc:
        logger.warning("Could not read Qdrant collection stats: %s", exc)
        return None
    return int(getattr(info, "points_count", 0) or 0)


def verify() -> int:
    """Reconcile corpus counts across DB, embeddings cache and Qdrant."""
    counts = _db_counts()
    cache = _cache_count()
    vectors = _qdrant_count()
    expected = counts["total"] - counts["hidden"]

    logger.info("Database rows:        %d (hidden: %d, expected indexable: %d)",
                counts["total"], counts["hidden"], expected)
    logger.info("indexed_at stamped:   %d", counts["indexed_at"])
    logger.info("embeddings.json:      %s", "missing" if cache is None else cache)
    logger.info("Qdrant points:        %s", "no backend" if vectors is None else vectors)

    problems: list[str] = []
    if vectors is None:
        problems.append("no Qdrant backend reachable (set QDRANT_URL or unset hermetic APP_ENV)")
    elif vectors != expected:
        problems.append(f"Qdrant has {vectors} points but the database expects {expected}")

    if counts["indexed_at"] != expected:
        problems.append(
            f"indexed_at is stamped on {counts['indexed_at']} rows but {expected} are indexable"
        )

    if cache is not None and cache != expected:
        problems.append(
            f"data/embeddings.json holds {cache} vectors but the database expects {expected}"
        )

    if problems:
        for problem in problems:
            logger.error("DRIFT: %s", problem)
        return 1

    logger.info("Corpus counts agree across database, embeddings cache and Qdrant.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Index memes from SQLite database into Qdrant Vector DB")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of newest memes to index")
    parser.add_argument("--recreate", action="store_true", help="Recreate Qdrant collection from scratch")
    parser.add_argument("--skip-images", action="store_true", help="Skip image download, CLIP, and BLIP processing")
    parser.add_argument("--verify", action="store_true", help="Only reconcile corpus counts, do not index")
    args = parser.parse_args()

    if args.verify:
        try:
            return verify()
        finally:
            from app.services.search_service import reset_qdrant_client
            reset_qdrant_client()

    logger.info("Starting Qdrant indexing task...")
    try:
        summary = index_memes(
            limit=args.limit,
            recreate=args.recreate,
            skip_images=args.skip_images,
        )
    finally:
        # Close the embedded client before the interpreter tears down; otherwise
        # QdrantClient.__del__ imports modules during shutdown and crashes.
        from app.services.search_service import reset_qdrant_client
        reset_qdrant_client()

    if not summary.get("vector_backend"):
        logger.error(
            "No Qdrant backend was reachable, so nothing was persisted. "
            "Set QDRANT_URL (remote) or unset a hermetic APP_ENV (test/ci) to use the local index."
        )
        return 1
    if summary.get("vector_upserts", 0) == 0:
        logger.error("Qdrant upsert wrote 0 points — the vector index is still empty.")
        return 1

    logger.info("Qdrant indexing task finished (%s points).", summary["vector_upserts"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
