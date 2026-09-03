"""
MemeGPT — Generate WebP thumbnails (200x200) for all memes and upload to R2.
Specification: 03_Cloudflare_R2_CDN_Setup.md & 04_Meme_Data_Pipeline.md
"""
import os
import sys
import logging
from pathlib import Path
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

import httpx
import boto3
from PIL import Image
from app.database import SessionLocal, Meme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("thumbnails")

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = os.getenv("R2_BUCKET", "memegpt-memes")
CDN_BASE = os.getenv("CDN_BASE_URL", "https://cdn.memegpt.com").rstrip("/")
THUMB_SIZE = (200, 200)


def main():
    if not all([R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY]):
        logger.error("❌ R2 credentials not set in .env")
        return

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=R2_ACCESS_KEY,
            aws_secret_access_key=R2_SECRET_KEY,
        )
    except Exception as e:
        logger.error(f"Failed to create S3 client: {e}")
        return

    db = SessionLocal()
    memes = db.query(Meme).all()
    success = 0
    failed = 0

    for meme in memes:
        url = meme.image_url or ""
        if not url or "cdn.memegpt.com/thumbs" in url:
            continue

        slug = meme.slug or str(meme.id)

        try:
            r = httpx.get(url, timeout=15, follow_redirects=True)
            r.raise_for_status()
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)

            # Save as WebP
            buf = BytesIO()
            img.save(buf, "WEBP", quality=80)
            buf.seek(0)

            r2_key = f"thumbs/{slug}.webp"
            s3.put_object(
                Bucket=R2_BUCKET,
                Key=r2_key,
                Body=buf.read(),
                ContentType="image/webp",
            )

            # Update DB with thumb URL
            meme.thumb_url = f"{CDN_BASE}/{r2_key}"
            db.add(meme)
            success += 1

            if success % 10 == 0:
                db.commit()
                logger.info(f"Processed {success} thumbnails...")

        except Exception as e:
            failed += 1
            logger.warning(f"Failed thumbnail for {slug}: {e}")

    db.commit()
    db.close()
    logger.info(f"✅ Generated {success} thumbnails (Failed: {failed})")


if __name__ == "__main__":
    main()
