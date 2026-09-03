#!/usr/bin/env python3
"""
MemeGPT — Batch Thumbnail Generator.
Generates 200x200 WebP thumbnails for all memes in database and uploads to CDN/local.

Usage:
    python scripts/generate_thumbnails.py [--limit 100] [--output-dir ./media/thumbs]
"""

import argparse
import logging
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.cdn_service import generate_thumbnail, upload_thumbnail, get_r2_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("thumbnails")


def generate_all_thumbnails(limit: Optional[int] = None, output_dir: Optional[str] = None):
    from app.database import SessionLocal, Meme

    out_path = Path(output_dir) if output_dir else None
    if out_path:
        out_path.mkdir(parents=True, exist_ok=True)

    r2_client = get_r2_client()

    db = SessionLocal()
    try:
        query = db.query(Meme).order_by(Meme.created_at.desc())
        if limit:
            query = query.limit(limit)
        memes = query.all()
        logger.info(f"Processing thumbnails for {len(memes)} memes...")

        success_count = 0
        for i, meme in enumerate(memes, 1):
            url = meme.image_url or meme.image_ref or meme.gif_url or meme.gif_ref
            if not url:
                continue

            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    continue

                thumb_bytes = generate_thumbnail(resp.content, size=(200, 200))
                if not thumb_bytes:
                    continue

                slug = meme.slug or meme.id

                # 1. Save locally if requested
                if out_path:
                    thumb_file = out_path / f"{slug}.webp"
                    thumb_file.write_bytes(thumb_bytes)

                # 2. Upload to R2 if client is configured
                if r2_client:
                    cdn_thumb_url = upload_thumbnail(slug, resp.content)
                    if cdn_thumb_url:
                        meme.thumb_url = cdn_thumb_url
                        db.commit()

                success_count += 1
                if i % 25 == 0 or i == len(memes):
                    logger.info(f"Progress: {i}/{len(memes)} (generated: {success_count})")

            except Exception as e:
                logger.debug(f"Failed thumbnail for {meme.id}: {e}")

        logger.info(f"✅ Finished generating {success_count} thumbnails.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate WebP thumbnails for memes")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of memes to process")
    parser.add_argument("--output-dir", default=None, help="Local directory to save thumbnails")
    args = parser.parse_args()

    generate_all_thumbnails(limit=args.limit, output_dir=args.output_dir)
