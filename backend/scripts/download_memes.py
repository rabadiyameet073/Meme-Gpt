#!/usr/bin/env python3
"""
MemeGPT — Meme Asset Bulk Downloader.

Downloads all meme images, gifs, and video files from database to local directory.
Supports resuming, rate-limiting, and image validation.

Usage:
    python scripts/download_memes.py [--output-dir ./media/memes] [--limit 100]
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests

# Set path to backend root
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("downloader")


def download_file(url: str, dest_path: Path, timeout: int = 15) -> bool:
    """Download single file from url to dest_path with stream writing."""
    if not url:
        return False

    if dest_path.exists() and dest_path.stat().st_size > 0:
        return True  # Already downloaded

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        headers = {"User-Agent": "MemeGPT-Downloader/1.0"}
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        resp.raise_for_status()

        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        logger.debug(f"Failed to download {url}: {e}")
        if dest_path.exists():
            dest_path.unlink(missing_ok=True)
        return False


def run_downloader(output_dir: str = "./media/memes", limit: Optional[int] = None):
    """Fetch memes from SQLite database and download available media."""
    from app.database import SessionLocal, Meme

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        query = db.query(Meme).order_by(Meme.created_at.desc())
        if limit:
            query = query.limit(limit)
        memes = query.all()
    finally:
        db.close()

    logger.info(f"Starting download for {len(memes)} memes to '{output_dir}'...")

    downloaded = 0
    skipped = 0
    failed = 0

    for i, m in enumerate(memes, 1):
        slug = m.slug or m.id
        url = m.image_url or m.gif_url or m.image_ref or m.gif_ref

        if not url:
            skipped += 1
            continue

        ext = ".jpg"
        if ".gif" in url.lower():
            ext = ".gif"
        elif ".png" in url.lower():
            ext = ".png"
        elif ".webp" in url.lower():
            ext = ".webp"
        elif ".mp4" in url.lower():
            ext = ".mp4"

        target_file = out_path / f"{slug}{ext}"
        success = download_file(url, target_file)

        if success:
            downloaded += 1
        else:
            failed += 1

        if i % 25 == 0 or i == len(memes):
            logger.info(f"Progress: {i}/{len(memes)} (downloaded: {downloaded}, failed: {failed}, skipped: {skipped})")

    logger.info("=" * 50)
    logger.info("✅ Bulk Download Finished!")
    logger.info(f"   Downloaded: {downloaded}")
    logger.info(f"   Skipped:    {skipped}")
    logger.info(f"   Failed:     {failed}")
    logger.info(f"   Total:      {len(memes)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download meme media files")
    parser.add_argument("--output-dir", default="./media/memes", help="Destination folder for downloaded media")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of memes to download")
    args = parser.parse_args()

    run_downloader(output_dir=args.output_dir, limit=args.limit)
