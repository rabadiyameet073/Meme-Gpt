# 03 — Cloudflare R2 CDN Setup + Media Upload
> **Priority:** 🔴 Critical — Meme images need to load from a fast, stable CDN
> **Time Needed:** ~2 hours
> **Result:** All meme images, GIFs, and thumbnails served from Cloudflare's global CDN

---

## 🌐 What is Cloudflare R2 and Why We Need It

**Cloudflare R2** is object storage (like Amazon S3 but free for 10GB). Every meme's image, GIF, WebP, and thumbnail gets uploaded here.

**Without R2:**
- `image_url` in your database points to Reddit or Giphy URLs
- Reddit URLs expire or get rate-limited
- Giphy URLs work but add third-party dependency
- No thumbnails exist → frontend shows nothing or slow full images

**With R2:**
- All media served from `cdn.memegpt.com` (Cloudflare edge)
- URLs never expire — they're YOUR content
- Thumbnail generation gives fast-loading previews (200×200 WebP)
- Global CDN means fast load everywhere

**R2 Folder Structure:**
```
memegpt-memes/ (bucket)
├── images/   {slug}.jpg   ← Original image
├── gifs/     {slug}.gif   ← GIF version
├── videos/   {slug}.mp4   ← Video version
├── webp/     {slug}.webp  ← WebP compressed
└── thumbs/   {slug}.webp  ← Thumbnail (200×200)
```

---

## 📋 Step 1 — Create Cloudflare Account + R2 Bucket

```
1. Go to: https://dash.cloudflare.com
2. Sign up (free)
3. In sidebar, click "R2 Object Storage"
4. Click "Create Bucket"
   - Name: memegpt-memes
   - Region: Automatic (Cloudflare chooses nearest)
5. Click "Create Bucket"

6. Enable Public Access:
   - Go to bucket → Settings tab
   - Under "Public Access" → click "Allow Access"
   - Copy the public bucket URL (looks like: https://pub-abc123.r2.dev)
   
7. (Optional but recommended) Set Custom Domain:
   - Under "Custom Domains" → "Connect Domain"
   - Domain: cdn.memegpt.com
   - This requires you own the domain and have Cloudflare as DNS
```

---

## 📋 Step 2 — Create R2 API Token

```
1. Cloudflare Dashboard → R2 → "Manage R2 API Tokens"
2. Click "Create API Token"
3. Settings:
   - Token Name: memegpt-backend
   - Permissions: Object Read & Write
   - Specify Bucket: memegpt-memes (select specific bucket)
4. Click "Create API Token"
5. COPY:
   - Access Key ID
   - Secret Access Key
   - (Account ID — visible in R2 dashboard URL)
```

---

## 📋 Step 3 — Add to Your .env File

```env
# ── CLOUDFLARE R2 (Media CDN) ────────────────────
R2_ENDPOINT=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key_id_here
R2_SECRET_KEY=your_secret_access_key_here
R2_BUCKET=memegpt-memes

# If you set up a custom domain:
CDN_BASE_URL=https://cdn.memegpt.com
# If using the free public URL (no custom domain):
# CDN_BASE_URL=https://pub-YOUR_ID.r2.dev
```

**Your Account ID** is in the Cloudflare Dashboard URL:
`https://dash.cloudflare.com/ACCOUNT_ID/r2/`

---

## 📋 Step 4 — Test R2 Connection

```powershell
cd "d:\Meme GPT\backend"
python -c "
import os
import boto3
from dotenv import load_dotenv
load_dotenv('../.env')

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('R2_SECRET_KEY'),
)

# List objects in bucket
result = s3.list_objects_v2(Bucket=os.getenv('R2_BUCKET', 'memegpt-memes'), MaxKeys=5)
print('✅ R2 connected!')
print(f'Objects in bucket: {result.get(\"KeyCount\", 0)}')
"
```

---

## 📋 Step 5 — Upload Meme Media to R2

The upload script already exists at `backend/scripts/upload_to_r2.py`. Here's how to run it and what it does:

**What `upload_to_r2.py` does:**
1. Reads all memes from SQLite
2. Downloads each image from its source URL (Reddit/Giphy/Imgflip)
3. Uploads to R2 in the correct folder (`images/`, `gifs/`, etc.)
4. Updates the `image_url` in your SQLite database to the CDN URL
5. Logs any failures

```powershell
cd "d:\Meme GPT\backend"
python scripts/upload_to_r2.py
```

**If the script is missing or broken, use this complete replacement:**

Create `d:\Meme GPT\backend\scripts\upload_to_r2_full.py`:

```python
"""
MemeGPT — Upload all meme media to Cloudflare R2 CDN.
Downloads from source URLs, uploads to R2, updates DB with CDN URLs.
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
    types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
             "gif": "image/gif", "webp": "image/webp", "mp4": "video/mp4"}
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

    s3 = get_s3_client()
    logger.info(f"✅ R2 client created. Bucket: {R2_BUCKET}")

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
```

```powershell
cd "d:\Meme GPT\backend"
python scripts/upload_to_r2_full.py
```

---

## 📋 Step 6 — Generate Thumbnails

The `generate_thumbnails.py` script creates 200×200 WebP thumbnails for every meme.

```powershell
cd "d:\Meme GPT\backend"
python scripts/generate_thumbnails.py
```

**If missing, create `d:\Meme GPT\backend\scripts\generate_thumbnails_full.py`:**

```python
"""
Generate WebP thumbnails (200x200) for all memes and upload to R2.
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("thumbnails")

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET = os.getenv("R2_BUCKET", "memegpt-memes")
CDN_BASE = os.getenv("CDN_BASE_URL", "https://cdn.memegpt.com").rstrip("/")
THUMB_SIZE = (200, 200)


def main():
    s3 = boto3.client("s3", endpoint_url=R2_ENDPOINT,
                       aws_access_key_id=R2_ACCESS_KEY,
                       aws_secret_access_key=R2_SECRET_KEY)

    db = SessionLocal()
    memes = db.query(Meme).all()
    success = 0

    for meme in memes:
        url = meme.image_url or ""
        if not url or "cdn.memegpt.com/thumbs" in url:
            continue

        slug = meme.slug or str(meme.id)

        try:
            r = httpx.get(url, timeout=15, follow_redirects=True)
            img = Image.open(BytesIO(r.content)).convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)

            # Save as WebP
            buf = BytesIO()
            img.save(buf, "WEBP", quality=80)
            buf.seek(0)

            r2_key = f"thumbs/{slug}.webp"
            s3.put_object(Bucket=R2_BUCKET, Key=r2_key, Body=buf.read(), ContentType="image/webp")

            # Update DB with thumb URL
            meme.thumb_url = f"{CDN_BASE}/{r2_key}"
            db.add(meme)
            success += 1

            if success % 10 == 0:
                db.commit()
                logger.info(f"Processed {success} thumbnails...")

        except Exception as e:
            logger.warning(f"Failed thumbnail for {slug}: {e}")

    db.commit()
    db.close()
    logger.info(f"✅ Generated {success} thumbnails")


if __name__ == "__main__":
    main()
```

```powershell
pip install pillow
python scripts/generate_thumbnails_full.py
```

---

## 📋 Step 7 — Set CDN CORS Headers (Prevent Browser Errors)

In Cloudflare R2 dashboard:
```
R2 → memegpt-memes → Settings → CORS Policy → Add Rule:
  Allowed Origins: * (or your specific domain)
  Allowed Methods: GET, HEAD
  Allowed Headers: *
  Max Age: 86400
```

---

## ✅ Done When

- [ ] R2 bucket `memegpt-memes` exists and is publicly accessible
- [ ] Test URL returns an image: `https://pub-YOUR-ID.r2.dev/images/test.jpg`
- [ ] `upload_to_r2_full.py` ran successfully
- [ ] Meme `image_url` values in DB now point to `cdn.memegpt.com` or R2 URL
- [ ] Thumbnails exist in `thumbs/` folder in R2 bucket

**Next step → `04_Meme_Data_Pipeline.md`**
