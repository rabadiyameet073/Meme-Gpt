# 06 — Meme Indexing Pipeline
# Download Images → OCR → BLIP Caption → CLIP Embed → Index to Qdrant

> **Gap Source:** Section 9 of GAP_ANALYSIS_FULL.md  
> **Priority:** P1 (P0 if you want real image-based search)  
> **Files to create/edit:**  
> - `d:\Meme GPT\backend\generate_embeddings.py` (rewrite completely)  
> - `d:\Meme GPT\backend\scripts\download_memes.py` (new)  
> - `d:\Meme GPT\backend\scripts\index_to_qdrant.py` (new)

---

## WHAT IS BROKEN

Current `generate_embeddings.py`:
- Only generates TEXT embeddings (MiniLM) 
- Writes output to `embeddings.json` file — NOT to Qdrant
- No CLIP image embeddings
- No OCR (Tesseract)
- No BLIP captioning
- Does NOT call Qdrant at all

Required pipeline per documentation:
```
For each meme:
  1. Download image from URL (or use local file)
  2. Run Tesseract OCR → extract any text in image
  3. Run BLIP → generate image caption
  4. Build rich text: name + dialogue + OCR text + BLIP caption + keywords
  5. Embed rich text with MiniLM → 384-dim text vector
  6. Embed image with CLIP → 512-dim image vector
  7. Upsert both vectors + payload into Qdrant
```

---

## STEP 1 — Install Dependencies

```bash
cd "d:\Meme GPT\backend"
pip install Pillow requests transformers torch torchvision
pip install pytesseract  # For OCR (also needs Tesseract binary)
pip install qdrant-client sentence-transformers
```

Install Tesseract binary on Windows:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Add to PATH or set `TESSERACT_CMD` env var

Add to `requirements.txt`:
```
Pillow>=10.0.0
pytesseract>=0.3.10
transformers>=4.40.0
torch>=2.0.0
torchvision>=0.15.0
sentence-transformers>=2.2.0
qdrant-client>=1.7.0
requests>=2.31.0
```

---

## STEP 2 — Complete Indexing Script

**Overwrite** `d:\Meme GPT\backend\generate_embeddings.py` with:

```python
#!/usr/bin/env python3
"""
MemeGPT — Complete Meme Indexing Pipeline (FIXED).

Pipeline:
  DB memes → download images → OCR + BLIP caption → MiniLM text embed
  → CLIP image embed → upsert to Qdrant with full payload

Run: python generate_embeddings.py [--limit 100] [--recreate]
"""

import argparse
import logging
import os
import sys
import time
from io import BytesIO
from pathlib import Path

import requests

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("indexer")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def load_models():
    """Load all ML models needed for indexing."""
    models = {}

    # 1. MiniLM text embedding model
    logger.info("Loading MiniLM text embedding model...")
    try:
        from sentence_transformers import SentenceTransformer
        models["text"] = SentenceTransformer("all-MiniLM-L6-v2", cache_folder="./model_cache")
        logger.info("✅ MiniLM loaded")
    except Exception as e:
        logger.error(f"Failed to load MiniLM: {e}")
        models["text"] = None

    # 2. CLIP image embedding model
    logger.info("Loading CLIP image embedding model...")
    try:
        from transformers import CLIPProcessor, CLIPModel
        clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", cache_dir="./model_cache")
        clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", cache_dir="./model_cache")
        models["clip"] = clip_model
        models["clip_processor"] = clip_processor
        logger.info("✅ CLIP loaded")
    except Exception as e:
        logger.warning(f"CLIP not available: {e} — image vectors will be skipped")
        models["clip"] = None
        models["clip_processor"] = None

    # 3. BLIP image captioning model
    logger.info("Loading BLIP captioning model...")
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        blip_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            cache_dir="./model_cache"
        )
        blip_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            cache_dir="./model_cache"
        )
        models["blip"] = blip_model
        models["blip_processor"] = blip_processor
        logger.info("✅ BLIP loaded")
    except Exception as e:
        logger.warning(f"BLIP not available: {e} — captions will be skipped")
        models["blip"] = None
        models["blip_processor"] = None

    return models


def download_image(url: str, timeout: int = 10):
    """Download image from URL. Returns PIL Image or None."""
    if not url:
        return None
    try:
        from PIL import Image
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        return img
    except Exception as e:
        logger.debug(f"Image download failed for {url}: {e}")
        return None


def ocr_image(image) -> str:
    """Extract text from image using Tesseract OCR."""
    try:
        import pytesseract
        # Try to set tesseract path on Windows
        if os.name == "nt":
            tesseract_cmd = os.getenv(
                "TESSERACT_CMD",
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )
            if os.path.exists(tesseract_cmd):
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        text = pytesseract.image_to_string(image, config="--psm 11")
        return text.strip()[:300]  # Max 300 chars
    except Exception:
        return ""


def caption_image(image, models: dict) -> str:
    """Generate caption for image using BLIP."""
    if not models.get("blip") or not models.get("blip_processor"):
        return ""
    try:
        import torch
        inputs = models["blip_processor"](image, return_tensors="pt")
        with torch.no_grad():
            out = models["blip"].generate(**inputs, max_new_tokens=50)
        caption = models["blip_processor"].decode(out[0], skip_special_tokens=True)
        return caption.strip()
    except Exception as e:
        logger.debug(f"BLIP caption failed: {e}")
        return ""


def embed_image(image, models: dict) -> list[float] | None:
    """Generate 512-dim CLIP embedding for image."""
    if not models.get("clip") or not models.get("clip_processor"):
        return None
    try:
        import torch
        inputs = models["clip_processor"](images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = models["clip"].get_image_features(**inputs)
            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features[0].tolist()
    except Exception as e:
        logger.debug(f"CLIP embedding failed: {e}")
        return None


def embed_text(text: str, models: dict) -> list[float]:
    """Generate 384-dim MiniLM embedding for text."""
    if not models.get("text"):
        return [0.0] * 384
    try:
        vector = models["text"].encode(text[:512], normalize_embeddings=True)
        return vector.tolist()
    except Exception as e:
        logger.debug(f"Text embedding failed: {e}")
        return [0.0] * 384


def build_rich_text(meme: dict, ocr_text: str = "", caption: str = "") -> str:
    """Build rich text combining all meme attributes for better embedding."""
    parts = []

    if meme.get("name"):
        parts.append(f"Meme: {meme['name']}")

    categories = meme.get("categories", []) or [meme.get("category", "general")]
    if categories:
        parts.append(f"Category: {', '.join(categories)}")

    emotions = meme.get("emotions", [])
    if emotions:
        parts.append(f"Emotions: {', '.join(emotions)}")

    if meme.get("dialogue"):
        parts.append(f"Text on meme: {meme['dialogue']}")

    if meme.get("explanation"):
        parts.append(f"When to use: {meme['explanation']}")

    keywords = meme.get("keywords", [])
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords[:10])}")

    if ocr_text:
        parts.append(f"OCR extracted text: {ocr_text}")

    if caption:
        parts.append(f"Image shows: {caption}")

    return "\n".join(parts)


def index_memes(limit: int = None, recreate: bool = False, skip_images: bool = False):
    """
    Main indexing pipeline.
    Reads memes from SQLite DB, generates embeddings, indexes to Qdrant.
    """
    # Setup Django-like app context
    os.environ.setdefault("APP_ENV", "development")

    from app.database import SessionLocal, Meme as MemeModel
    from app.services.search_service import (
        get_qdrant_client, create_qdrant_collection, upsert_memes
    )

    # 1. Initialize Qdrant collection
    logger.info("Initializing Qdrant collection...")
    if not create_qdrant_collection(recreate=recreate):
        logger.error("Failed to create Qdrant collection — check QDRANT_URL in .env")
        return

    # 2. Load ML models
    logger.info("Loading ML models (this may take a few minutes on first run)...")
    models = load_models()

    # 3. Fetch memes from DB
    db = SessionLocal()
    try:
        query = db.query(MemeModel).order_by(MemeModel.created_at.desc())
        if limit:
            query = query.limit(limit)
        memes = [m.to_dict() for m in query.all()]
    finally:
        db.close()

    logger.info(f"Found {len(memes)} memes to index")

    # 4. Process each meme
    batch = []
    total_indexed = 0
    failed = 0

    for i, meme in enumerate(memes, 1):
        try:
            image = None
            ocr_text = ""
            caption = ""
            image_vector = None

            # Download image if we have a URL
            if not skip_images:
                image_url = meme.get("image_url") or meme.get("gif_url") or meme.get("imageRef")
                if image_url:
                    image = download_image(image_url)

                    if image:
                        ocr_text = ocr_image(image)
                        caption = caption_image(image, models)
                        image_vector = embed_image(image, models)

            # Build rich text + embed
            rich_text = build_rich_text(meme, ocr_text, caption)
            text_vector = embed_text(rich_text, models)

            batch.append({
                "meme": meme,
                "text_vector": text_vector,
                "image_vector": image_vector,
            })

            # Log progress
            if i % 10 == 0:
                logger.info(f"Processed {i}/{len(memes)} memes...")

            # Upsert in batches of 50
            if len(batch) >= 50:
                n = upsert_memes(batch)
                total_indexed += n
                batch = []
                logger.info(f"Indexed {total_indexed} memes so far...")

        except Exception as e:
            logger.error(f"Failed to process meme {meme.get('id')}: {e}")
            failed += 1

    # Upsert remaining
    if batch:
        n = upsert_memes(batch)
        total_indexed += n

    logger.info(f"\n{'='*50}")
    logger.info(f"✅ Indexing complete!")
    logger.info(f"   Indexed: {total_indexed}")
    logger.info(f"   Failed:  {failed}")
    logger.info(f"   Total:   {len(memes)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MemeGPT meme indexing pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of memes to index")
    parser.add_argument("--recreate", action="store_true", help="Recreate Qdrant collection")
    parser.add_argument("--skip-images", action="store_true", help="Skip image download/CLIP/BLIP")
    args = parser.parse_args()

    index_memes(
        limit=args.limit,
        recreate=args.recreate,
        skip_images=args.skip_images,
    )
```

---

## STEP 3 — Run the Pipeline

### Quick test (first 10 memes, text-only, fast):
```bash
cd "d:\Meme GPT\backend"
python generate_embeddings.py --limit 10 --skip-images
```

### Full run with images (takes ~1-2 hours for 5000 memes):
```bash
python generate_embeddings.py --recreate
```

### Text-only indexing (faster, no CLIP/BLIP needed):
```bash
python generate_embeddings.py --skip-images
```

---

## STEP 4 — Verify Indexing

```python
# Run from d:\Meme GPT\backend
python -c "
from app.services.search_service import get_collection_info
info = get_collection_info()
print(f'Qdrant collection stats: {info}')
# Should show count > 0 if indexing worked
"
```

---

## STEP 5 — Schedule Re-indexing

Add to `cron` or Windows Task Scheduler to re-index weekly:
```bash
# Weekly re-index (update embeddings for new memes)
python generate_embeddings.py --limit 500  # Index newest 500 memes
```
