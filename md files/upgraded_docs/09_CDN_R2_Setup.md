# 09 — CDN & Cloudflare R2 Setup
# Bucket Creation, Image Upload Script, Thumbnail Pipeline

> **Gap Source:** Section 5 of GAP_ANALYSIS_FULL.md  
> **Priority:** P1 (Without this, all meme images show as broken)  
> **Files to create:**  
> - `d:\Meme GPT\backend\scripts\upload_to_r2.py` (NEW)  
> - `d:\Meme GPT\backend\scripts\generate_thumbnails.py` (NEW)  
> - `d:\Meme GPT\backend\app\services\cdn_service.py` (fix)

---

## WHAT IS BROKEN

- All `image_url`, `gif_url`, `mp4_url` fields in DB are NULL
- No Cloudflare R2 bucket exists or is configured
- `CDN_BASE_URL` defaults to `cdn.memegpt.com` which doesn't exist yet
- No thumbnail generation pipeline

---

## STEP 1 — Create Cloudflare R2 Bucket

1. Go to https://dash.cloudflare.com → R2 → Create Bucket
2. Name: `memegpt-memes`
3. Location: Auto
4. Go to **Manage R2 API Tokens** → Create Token
   - Permissions: Object Read & Write
   - Bucket: Restrict to `memegpt-memes`
5. Copy: **Account ID**, **Access Key ID**, **Secret Access Key**
6. Add to `.env`:
```env
R2_ENDPOINT=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY=YOUR_ACCESS_KEY_ID
R2_SECRET_KEY=YOUR_SECRET_ACCESS_KEY
R2_BUCKET=memegpt-memes
CDN_BASE_URL=https://pub-XXXXXXXX.r2.dev  # R2 public URL until custom domain
```

### Optional: Custom Domain for CDN
1. R2 Bucket → Settings → Custom Domains → Add Domain
2. Point `cdn.memegpt.com` → R2 bucket
3. Update: `CDN_BASE_URL=https://cdn.memegpt.com`

---

## STEP 2 — Fixed `cdn_service.py`

**Replace** `d:\Meme GPT\backend\app\services\cdn_service.py` with:

```python
"""
MemeGPT — CDN Service (Cloudflare R2) — FIXED.

Handles URL building, file upload, and thumbnail generation.
All meme media stored in Cloudflare R2 with structure:
  memegpt-memes/
  ├── images/   {slug}.jpg
  ├── gifs/     {slug}.gif
  ├── videos/   {slug}.mp4
  ├── webp/     {slug}.webp
  └── thumbs/   {slug}.webp  (200×200)
"""

import logging
import os
from io import BytesIO
from typing import Optional

from app.config import settings

logger = logging.getLogger("memegpt.cdn")

CDN_BASE = getattr(settings, "CDN_BASE_URL", "https://cdn.memegpt.com")
R2_BUCKET = getattr(settings, "R2_BUCKET", "memegpt-memes")


def build_meme_urls(slug: str) -> dict:
    """Build all CDN URLs for a meme by its slug."""
    base = CDN_BASE.rstrip("/")
    return {
        "image_url": f"{base}/images/{slug}.jpg",
        "gif_url": f"{base}/gifs/{slug}.gif",
        "mp4_url": f"{base}/videos/{slug}.mp4",
        "webp_url": f"{base}/webp/{slug}.webp",
        "thumb_url": f"{base}/thumbs/{slug}.webp",
    }


def get_r2_client():
    """Returns boto3 S3 client configured for Cloudflare R2."""
    endpoint = getattr(settings, "R2_ENDPOINT", "")
    access_key = getattr(settings, "R2_ACCESS_KEY", "")
    secret_key = getattr(settings, "R2_SECRET_KEY", "")

    if not all([endpoint, access_key, secret_key]):
        logger.warning("R2 credentials not configured — media upload disabled")
        return None

    try:
        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
        )
        return client
    except ImportError:
        logger.error("boto3 not installed. Run: pip install boto3")
        return None
    except Exception as e:
        logger.error(f"Failed to create R2 client: {e}")
        return None


def upload_file(
    file_data: bytes,
    key: str,
    content_type: str = "image/jpeg",
    public: bool = True,
) -> Optional[str]:
    """
    Upload file bytes to R2.
    Returns CDN URL on success, None on failure.

    Args:
        file_data: Raw file bytes
        key: R2 object key, e.g. "images/drake-pointing.jpg"
        content_type: MIME type
        public: Whether to make publicly accessible
    """
    client = get_r2_client()
    if not client:
        return None

    extra_args = {"ContentType": content_type}
    if public:
        extra_args["ACL"] = "public-read"

    try:
        client.put_object(
            Bucket=R2_BUCKET,
            Key=key,
            Body=file_data,
            **extra_args,
        )
        cdn_url = f"{CDN_BASE.rstrip('/')}/{key}"
        logger.debug(f"Uploaded {key} → {cdn_url}")
        return cdn_url

    except Exception as e:
        logger.error(f"R2 upload failed for {key}: {e}")
        return None


def upload_meme_image(slug: str, image_data: bytes, fmt: str = "jpg") -> Optional[str]:
    """Upload meme original image. Returns CDN URL."""
    content_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "mp4": "video/mp4",
        "webp": "image/webp",
    }
    folder_map = {
        "jpg": "images", "jpeg": "images", "png": "images",
        "gif": "gifs",
        "mp4": "videos",
        "webp": "webp",
    }
    folder = folder_map.get(fmt.lower(), "images")
    key = f"{folder}/{slug}.{fmt.lower()}"
    ct = content_types.get(fmt.lower(), "image/jpeg")
    return upload_file(image_data, key, ct)


def generate_thumbnail(image_data: bytes, size: tuple = (200, 200)) -> Optional[bytes]:
    """
    Generate a 200×200 WebP thumbnail from image bytes.
    Returns thumbnail bytes or None on failure.
    """
    try:
        from PIL import Image

        img = Image.open(BytesIO(image_data)).convert("RGB")
        img.thumbnail(size, Image.LANCZOS)

        # Center-crop to exact size
        if img.size != size:
            left = (img.width - size[0]) // 2
            top = (img.height - size[1]) // 2
            img = img.crop((left, top, left + size[0], top + size[1]))

        output = BytesIO()
        img.save(output, format="WEBP", quality=85)
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Thumbnail generation failed: {e}")
        return None


def upload_thumbnail(slug: str, image_data: bytes) -> Optional[str]:
    """Generate 200×200 thumbnail and upload to R2/thumbs/. Returns CDN URL."""
    thumb_data = generate_thumbnail(image_data)
    if not thumb_data:
        return None
    key = f"thumbs/{slug}.webp"
    return upload_file(thumb_data, key, "image/webp")


def resolve_formats(meme: dict) -> dict:
    """
    Build format URLs for a meme dict.
    Tries CDN URLs, falls back to imageRef/gifRef/videoRef.
    """
    slug = meme.get("slug", "")
    cdn_urls = build_meme_urls(slug) if slug else {}

    return {
        "image": meme.get("image_url") or meme.get("imageRef") or cdn_urls.get("image_url"),
        "gif": meme.get("gif_url") or meme.get("gifRef") or cdn_urls.get("gif_url"),
        "mp4": meme.get("mp4_url") or meme.get("videoRef") or cdn_urls.get("mp4_url"),
        "webp": meme.get("webp_url") or cdn_urls.get("webp_url"),
        "thumb": meme.get("thumb_url") or cdn_urls.get("thumb_url"),
    }
```

---

## STEP 3 — Image Upload Script

**Create** `d:\Meme GPT\backend\scripts\upload_to_r2.py`:

```python
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
    from app.services.cdn_service import upload_meme_image, upload_thumbnail

    db = SessionLocal()
    try:
        query = db.query(Meme).filter(Meme.image_url.is_(None))
        if limit:
            query = query.limit(limit)
        memes = query.all()
        logger.info(f"Found {len(memes)} memes without CDN images")

        for i, meme in enumerate(memes, 1):
            # Try to get image from imgflip or original source
            src_url = meme.image_ref or meme.gif_ref

            if not src_url:
                # Try Imgflip API as fallback
                src_url = f"https://i.imgflip.com/{meme.id}.jpg"

            try:
                resp = requests.get(src_url, timeout=10)
                if resp.status_code != 200:
                    logger.warning(f"Could not fetch image for {meme.slug}: {resp.status_code}")
                    continue

                image_data = resp.content
                fmt = "gif" if src_url.endswith(".gif") else "jpg"

                # Upload original
                cdn_url = upload_meme_image(meme.slug, image_data, fmt)
                if cdn_url:
                    if fmt == "gif":
                        meme.gif_url = cdn_url
                    else:
                        meme.image_url = cdn_url

                # Upload thumbnail
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
```

---

## STEP 4 — Install boto3

```bash
pip install boto3
```

Add to `requirements.txt`:
```
boto3>=1.28.0
```

---

## STEP 5 — Run Upload

```bash
# Test with 10 memes first
cd "d:\Meme GPT\backend"
python scripts/upload_to_r2.py --limit 10

# Full upload
python scripts/upload_to_r2.py
```

---

## STEP 6 — Verify CDN Works

```bash
# Check a meme URL
curl -I https://pub-XXXX.r2.dev/images/drake-pointing.jpg
# Should return: HTTP/2 200
```
