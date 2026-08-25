#!/usr/bin/env python3
"""
Upload meme images from Imgflip/internet to Cloudflare R2.
Run: python scripts/upload_to_r2.py [--limit 100]
"""

import argparse
import logging
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uploader")


def upload_all_memes(limit=None):
    from app.database import SessionLocal, Meme
    from app.services.cdn_service import upload_meme_image, upload_thumbnail, get_r2_client

    client = get_r2_client()
    if not client:
        logger.warning("R2 client not configured. Set R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY in .env.")
        return

    db = SessionLocal()
    try:
        query = db.query(Meme).filter(Meme.image_url.is_(None))
        if limit:
            query = query.limit(limit)
        memes = query.all()
        logger.info(f"Found {len(memes)} memes without CDN images")

        for i, meme in enumerate(memes, 1):
            src_url = meme.image_ref or meme.gif_ref

            if not src_url:
                src_url = f"https://i.imgflip.com/{meme.id}.jpg"

            try:
                resp = requests.get(src_url, timeout=10)
                if resp.status_code != 200:
                    logger.warning(f"Could not fetch image for {meme.slug}: {resp.status_code}")
                    continue

                image_data = resp.content
                fmt = "gif" if src_url.endswith(".gif") else "jpg"

                cdn_url = upload_meme_image(meme.slug, image_data, fmt)
                if cdn_url:
                    if fmt == "gif":
                        meme.gif_url = cdn_url
                    else:
                        meme.image_url = cdn_url

                thumb_url = upload_thumbnail(meme.slug, image_data)
                if thumb_url:
                    meme.thumb_url = thumb_url

                db.commit()
                logger.info(f"[{i}/{len(memes)}] Uploaded: {meme.slug}")

            except Exception as e:
                logger.error(f"Failed {meme.slug}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    upload_all_memes(args.limit)
