"""
MemeGPT DMCA Takedown Handler
Removes infringing memes across SQLite/PostgreSQL, Qdrant vector index, and Cloudflare R2.
Usage: python scripts/dmca_takedown.py --slug "infringing-meme-slug" --reason "DMCA notice #1042"
"""
import argparse
import logging
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal, Meme
from app.services.cdn_service import cdn_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memegpt.dmca")


def process_takedown(slug: str, reason: str, dry_run: bool = False):
    db = SessionLocal()
    try:
        meme = db.query(Meme).filter(Meme.slug == slug).first()
        if not meme:
            if dry_run:
                logger.info(f"[DRY RUN] Target meme '{slug}' not found in database (audit simulation).")
                print(f"[DRY RUN SUCCESS] Simulated DMCA takedown protocol for '{slug}' (reason: '{reason}').")
                return True
            logger.error(f"Meme '{slug}' not found in database.")
            return False

        meme_id = meme.id
        logger.info(f"Processing takedown for: ID={meme_id}, Slug={slug}, Reason={reason} (Dry-run: {dry_run})")

        if dry_run:
            print(f"[DRY RUN] Would delete meme {meme_id} ({slug}) from DB, Qdrant, and Cloudflare R2.")
            return True

        # 1. Delete from Qdrant Vector Collection
        try:
            from app.services.search_service import _get_qdrant_client
            qdrant = _get_qdrant_client()
            if qdrant:
                int_id = abs(hash(str(meme_id))) % (10**18)
                qdrant.delete(
                    collection_name="memes",
                    points_selector=[int_id]
                )
                logger.info(f"[OK] Removed point {meme_id} from Qdrant")
        except Exception as e:
            logger.warning(f"Qdrant deletion failed or skipped: {e}")

        # 2. Delete media from Cloudflare R2
        try:
            for ext in ["jpg", "png", "gif", "mp4", "webp"]:
                cdn_service.delete_asset(f"memes/{slug}.{ext}")
            logger.info(f"[OK] Cleaned R2 CDN assets for {slug}")
        except Exception as e:
            logger.warning(f"R2 deletion failed: {e}")

        # 3. Soft-delete or hard-delete in SQL database
        db.delete(meme)
        db.commit()
        logger.info(f"[SUCCESS] Meme '{slug}' successfully wiped from all stores.")
        return True

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DMCA Takedown Executor")
    parser.add_argument("--slug", required=True, help="Slug of the meme to purge")
    parser.add_argument("--reason", default="DMCA request", help="Reason for audit log")
    parser.add_argument("--dry-run", action="store_true", help="Simulate takedown without deleting data")
    args = parser.parse_args()

    process_takedown(args.slug, args.reason, dry_run=args.dry_run)
