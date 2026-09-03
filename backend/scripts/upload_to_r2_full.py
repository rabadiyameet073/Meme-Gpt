"""
MemeGPT — Upload all meme media to Cloudflare R2 CDN.
Downloads from source URLs, uploads to R2, updates DB with CDN URLs.
Specification: 03_Cloudflare_R2_CDN_Setup.md & 04_Meme_Data_Pipeline.md
"""
import os
import sys
import time
import logging
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

import httpx
import boto3
from botocore.exceptions import ClientError
from app.database import SessionLocal, Meme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("upload_r2")

# R2 Config
R2_ENDPOINT = os.getenv("R2_ENDPOINT", "")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY", "")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY", "")
R2_BUCKET = os.getenv("R2_BUCKET", "memegpt-memes")
CDN_BASE = os.getenv("CDN_BASE_URL", "https://cdn.memegpt.com").rstrip("/")

TEMP_DIR = Path("./tmp_downloads")
TEMP_DIR.mkdir(exist_ok=True)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
    )


def download_file(url: str, dest: Path) -> bool:
    """Download a file from URL. Returns True on success."""
    try:
        with httpx.stream("GET", url, timeout=30, follow_redirects=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        return dest.stat().st_size > 1000  # At least 1KB
    except Exception as e:
        logger.warning(f"Download failed {url}: {e}")
        return False


def upload_to_r2(s3, local_path: Path, r2_key: str, content_type: str) -> bool:
    """Upload a file to R2."""
    try:
        with open(local_path, "rb") as f:
            s3.put_object(
                Bucket=R2_BUCKET,
                Key=r2_key,
                Body=f.read(),
                ContentType=content_type,
            )
        return True
    except ClientError as e:
        logger.warning(f"R2 upload failed {r2_key}: {e}")
        return False


def get_content_type(url_or_path: str) -> str:
    ext = url_or_path.lower().split("?")[0].split(".")[-1]
    types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "mp4": "video/mp4",
    }
    return types.get(ext, "image/jpeg")


def get_folder(url: str) -> str:
    ext = url.lower().split("?")[0].split(".")[-1]
    if ext == "gif":
        return "gifs"
    elif ext == "mp4":
        return "videos"
    elif ext == "webp":
        return "webp"
    else:
        return "images"


def main():
    if not all([R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY]):
        logger.error("❌ R2 credentials not set in .env (R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY)")
        return

    try:
        s3 = get_s3_client()
        logger.info(f"✅ R2 client created. Bucket: {R2_BUCKET}")
    except Exception as e:
        logger.error(f"Failed to create S3/R2 client: {e}")
        return

    db = SessionLocal()
    memes = db.query(Meme).all()
    logger.info(f"Found {len(memes)} memes to process")

    success = 0
    failed = 0

    for meme in memes:
        source_url = meme.image_url or ""
        if not source_url or source_url.startswith(CDN_BASE):
            logger.debug(f"Skipping {meme.slug} — already on CDN or no URL")
            continue

        slug = meme.slug or hashlib.md5(source_url.encode()).hexdigest()[:12]
        folder = get_folder(source_url)
        ext = source_url.lower().split("?")[0].split(".")[-1] or "jpg"
        r2_key = f"{folder}/{slug}.{ext}"
        cdn_url = f"{CDN_BASE}/{r2_key}"

        # Download
        local = TEMP_DIR / f"{slug}.{ext}"
        if not download_file(source_url, local):
            failed += 1
            continue

        # Upload
        content_type = get_content_type(source_url)
        if upload_to_r2(s3, local, r2_key, content_type):
            # Update DB
            meme.image_url = cdn_url
            db.add(meme)
            success += 1
            logger.info(f"[{success}] Uploaded {slug} → {cdn_url}")
        else:
            failed += 1

        # Cleanup
        local.unlink(missing_ok=True)

        # Rate limit — be respectful to source servers
        time.sleep(0.1)

    db.commit()
    db.close()

    logger.info(f"\n✅ Done! Uploaded: {success} | Failed: {failed}")
    logger.info(f"Check your R2 bucket at: https://dash.cloudflare.com → R2 → {R2_BUCKET}")


if __name__ == "__main__":
    main()
