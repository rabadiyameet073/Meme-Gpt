# 03 — BLIP + CLIP Image AI Pipeline Guide
> Add BLIP caption generation, CLIP image embeddings, and OCR text extraction to the meme indexing pipeline.

---

## Problem Statement

The spec requires three image-processing AI models for meme indexing:

| Model | Purpose | Status | Gap |
|-------|---------|--------|-----|
| BLIP (Salesforce/blip-image-captioning-base) | Generate captions for meme images | ❌ Missing | No code exists |
| CLIP (openai/clip-vit-base-patch32) | Generate 512-dim image embeddings | 🟡 Partial | Collection supports it, but no processing script |
| Tesseract OCR | Extract text from meme images | 🟡 Partial | Installed in Docker, but not used in indexing |

These models run **during indexing only** (not real-time), so they don't affect latency.

---

## Prerequisites

```powershell
cd "d:\Meme GPT\backend"
pip install transformers Pillow torch pytesseract sentence-transformers
```

For Tesseract on Windows:
1. Download from https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH or set in Python:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## Step 1: Create the Image Processing Service

**File (create new):** `backend/app/services/image_processing_service.py`

```python
"""
MemeGPT — Image Processing Service for Meme Indexing.

Runs OFFLINE (during indexing, not real-time).
Models:
  - BLIP: Auto-generate captions for meme images (446MB)
  - CLIP: Generate 512-dim image embeddings (400MB)
  - Tesseract: OCR text extraction from meme images (20MB)

Specification: 03_ML_PIPELINE_AND_TRAINING.md
"""

import logging
import os
import sys
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger("memegpt.image_processing")

# ─── Model Singletons ────────────────────────────────────────────────
_blip_model = None
_blip_processor = None
_clip_model = None
_clip_processor = None

MODELS_CACHE_DIR = os.getenv("MODELS_CACHE_DIR", "./model_cache")


def load_blip():
    """Load BLIP captioning model (446MB). Call once at start of indexing."""
    global _blip_model, _blip_processor
    if _blip_model is not None:
        return

    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        logger.info("Loading BLIP captioning model...")
        _blip_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            cache_dir=MODELS_CACHE_DIR,
        )
        _blip_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base",
            cache_dir=MODELS_CACHE_DIR,
        )
        logger.info("✅ BLIP model loaded")
    except Exception as e:
        logger.error(f"Failed to load BLIP: {e}")


def load_clip():
    """Load CLIP image embedding model (400MB). Call once at start of indexing."""
    global _clip_model, _clip_processor
    if _clip_model is not None:
        return

    try:
        from transformers import CLIPModel, CLIPProcessor
        logger.info("Loading CLIP image embedding model...")
        _clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32",
            cache_dir=MODELS_CACHE_DIR,
        )
        _clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32",
            cache_dir=MODELS_CACHE_DIR,
        )
        logger.info("✅ CLIP model loaded")
    except Exception as e:
        logger.error(f"Failed to load CLIP: {e}")


def generate_caption(image_path: str) -> str:
    """
    Generate a natural language caption for a meme image using BLIP.
    Example output: "a man in a suit pointing at a television"

    Args:
        image_path: Path to the local image file

    Returns:
        Caption string, or empty string on failure
    """
    if _blip_model is None:
        load_blip()
    if _blip_model is None:
        return ""

    try:
        import torch
        from PIL import Image

        img = Image.open(image_path).convert("RGB")
        inputs = _blip_processor(img, return_tensors="pt")
        with torch.no_grad():
            out = _blip_model.generate(**inputs, max_new_tokens=60)
        caption = _blip_processor.decode(out[0], skip_special_tokens=True)
        return caption.strip()
    except Exception as e:
        logger.warning(f"Caption generation failed for {image_path}: {e}")
        return ""


def generate_image_embedding(image_path: str) -> List[float]:
    """
    Generate a 512-dim CLIP embedding for a meme image.
    This embedding is stored in Qdrant's 'image' named vector.

    Args:
        image_path: Path to the local image file

    Returns:
        List of 512 floats (normalized), or zero vector on failure
    """
    if _clip_model is None:
        load_clip()
    if _clip_model is None:
        return [0.0] * 512

    try:
        import torch
        from PIL import Image

        img = Image.open(image_path).convert("RGB")
        inputs = _clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            features = _clip_model.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
        return features[0].tolist()
    except Exception as e:
        logger.warning(f"CLIP embedding failed for {image_path}: {e}")
        return [0.0] * 512


def extract_text_ocr(image_path: str) -> str:
    """
    Extract text overlaid on a meme image using Tesseract OCR.
    Example output: "ONE DOES NOT SIMPLY / WALK INTO MORDOR"

    Args:
        image_path: Path to the local image file

    Returns:
        Extracted text string, or empty string on failure
    """
    try:
        import pytesseract
        from PIL import Image, ImageFilter

        # On Windows, set the tesseract path if needed
        if sys.platform == "win32":
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path

        img = Image.open(image_path)
        # Preprocess for better OCR accuracy
        img = img.convert("L")  # Grayscale
        img = img.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR failed for {image_path}: {e}")
        return ""


def process_meme_image(image_path: str) -> Dict:
    """
    Full image processing pipeline for a single meme.
    Returns dict with caption, ocr_text, and image_embedding.
    """
    result = {
        "caption": "",
        "ocr_text": "",
        "image_embedding": [0.0] * 512,
    }

    if not image_path or not os.path.exists(image_path):
        return result

    result["caption"] = generate_caption(image_path)
    result["ocr_text"] = extract_text_ocr(image_path)
    result["image_embedding"] = generate_image_embedding(image_path)

    return result
```

---

## Step 2: Create the Full Indexing Script

**File (create new):** `scripts/full_index_pipeline.py`

```python
"""
Full meme indexing pipeline:
1. Load raw meme data
2. Download images (if not local)
3. Process with BLIP (captions) + OCR (text) + CLIP (image embedding)
4. Generate text embeddings (MiniLM)
5. Generate combined embeddings (896-dim)
6. Upsert to Qdrant
7. Update database metadata
"""

import json
import os
import sys
import time
import requests
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.image_processing_service import (
    load_blip, load_clip,
    process_meme_image,
)
from app.services.embedding_service import embed_text, get_combined_embedding


DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
IMAGES_DIR = RAW_DIR / "images"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

for d in [PROCESSED_DIR, IMAGES_DIR, EMBEDDINGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def download_image(url: str, meme_id: str) -> str:
    """Download image to local disk if not already present."""
    ext = url.split(".")[-1].split("?")[0][:4]
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "jpg"
    path = IMAGES_DIR / f"{meme_id}.{ext}"
    if path.exists():
        return str(path)
    try:
        resp = requests.get(url, timeout=10, stream=True)
        if resp.status_code == 200:
            path.write_bytes(resp.content)
            return str(path)
    except Exception as e:
        print(f"  ⚠ Failed to download {url}: {e}")
    return ""


def run_pipeline():
    # Load raw memes
    master_file = RAW_DIR / "memes_master.json"
    if not master_file.exists():
        print("❌ No memes_master.json found. Run scripts/build_huge_dataset.py first.")
        return

    with open(master_file) as f:
        memes = json.load(f)

    print(f"📦 Loaded {len(memes)} raw memes")

    # Load image models
    print("🧠 Loading BLIP + CLIP models (this takes 1-2 minutes on first run)...")
    load_blip()
    load_clip()

    processed = []
    for i, meme in enumerate(memes):
        print(f"\n[{i+1}/{len(memes)}] Processing: {meme.get('name', 'Unknown')}")

        # 1. Download image if we only have a URL
        image_path = meme.get("image_path", "")
        if not image_path and meme.get("image_url"):
            image_path = download_image(meme["image_url"], meme["id"])
            meme["image_path"] = image_path

        # 2. Run image processing (BLIP + OCR + CLIP)
        img_result = process_meme_image(image_path)

        # 3. Build rich text description
        parts = [
            f"Meme: {meme.get('name', '')}",
            f"Caption: {img_result['caption']}" if img_result["caption"] else "",
            f"Text on image: {img_result['ocr_text']}" if img_result["ocr_text"] else "",
            f"Emotions: {', '.join(meme.get('emotions', []))}",
            f"Keywords: {', '.join(meme.get('keywords', []))}",
            f"Categories: {', '.join(meme.get('categories', []))}",
        ]
        text_description = "\n".join(p for p in parts if p)

        # 4. Generate text embedding
        text_embedding = embed_text(text_description[:512])

        # 5. Generate combined embedding (65% text + 35% image)
        combined_embedding = get_combined_embedding(
            text_embedding,
            img_result["image_embedding"],
            text_weight=0.65,
            image_weight=0.35,
        )

        processed.append({
            **meme,
            "caption": img_result["caption"],
            "ocr_text": img_result["ocr_text"],
            "text_description": text_description,
            "text_embedding": text_embedding,
            "image_embedding": img_result["image_embedding"],
            "combined_embedding": combined_embedding,
        })

        if (i + 1) % 100 == 0:
            print(f"  ✅ Processed {i+1}/{len(memes)}")

    # Save processed data
    output_file = EMBEDDINGS_DIR / "memes_with_full_embeddings.json"
    with open(output_file, "w") as f:
        json.dump(processed, f)
    print(f"\n✅ Saved {len(processed)} fully processed memes to {output_file}")

    # Now index to Qdrant
    print("\n📡 Indexing to Qdrant...")
    try:
        from scripts.index_qdrant import index_memes_from_file
        index_memes_from_file(str(output_file))
        print("✅ Qdrant indexing complete")
    except Exception as e:
        print(f"⚠ Qdrant indexing skipped: {e}")
        print("  Run manually: python scripts/index_qdrant.py")


if __name__ == "__main__":
    start = time.time()
    run_pipeline()
    elapsed = time.time() - start
    print(f"\n⏱ Total pipeline time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
```

---

## Step 3: Add BLIP/CLIP Config to `.env.example`

**Add to:** `.env.example`

```env
# ── Image AI Models (Indexing Only) ────────────────────────────────
# These run during indexing, NOT at inference time
BLIP_MODEL=Salesforce/blip-image-captioning-base
CLIP_MODEL=openai/clip-vit-base-patch32
# Set to 'false' to skip image processing during indexing
ENABLE_IMAGE_PROCESSING=true
```

---

## Step 4: Update the Qdrant Indexing Script

The existing `scripts/index_qdrant.py` needs to accept the new embedding format with all 3 vector types.

**Add this function to:** `scripts/index_qdrant.py`

```python
def index_memes_from_file(filepath: str, batch_size: int = 100):
    """Index memes that have text, image, and combined embeddings."""
    import json
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

    client = QdrantClient(
        url=os.environ.get("QDRANT_URL"),
        api_key=os.environ.get("QDRANT_API_KEY"),
    )

    with open(filepath) as f:
        memes = json.load(f)

    for batch_start in range(0, len(memes), batch_size):
        batch = memes[batch_start:batch_start + batch_size]
        points = []

        for meme in batch:
            point_id = abs(hash(meme["id"])) % (10**18)
            vectors = {"text": meme["text_embedding"]}

            # Add image vector if it's not all zeros
            if any(v != 0.0 for v in meme.get("image_embedding", [])):
                vectors["image"] = meme["image_embedding"]

            # Add combined vector
            if meme.get("combined_embedding"):
                vectors["combined"] = meme["combined_embedding"]

            points.append(PointStruct(
                id=point_id,
                vectors=vectors,
                payload={
                    "meme_id": meme["id"],
                    "name": meme.get("name", ""),
                    "slug": meme.get("slug", ""),
                    "caption": meme.get("caption", ""),
                    "ocr_text": meme.get("ocr_text", ""),
                    "emotions": meme.get("emotions", []),
                    "keywords": meme.get("keywords", []),
                    "categories": meme.get("categories", []),
                    "image_url": meme.get("image_url", ""),
                    "gif_url": meme.get("gif_url", ""),
                    "mp4_url": meme.get("mp4_url", ""),
                    "thumb_url": meme.get("thumb_url", ""),
                    "has_gif": bool(meme.get("gif_url")),
                    "has_video": bool(meme.get("mp4_url")),
                    "nsfw": meme.get("nsfw", False),
                    "popularity_score": meme.get("popularity_score", 0.0),
                },
            ))

        client.upsert(collection_name="memes", points=points)
        print(f"  Indexed batch {batch_start}–{batch_start + len(batch)}")

    print(f"✅ Indexed {len(memes)} memes with full embeddings")
```

---

## Running the Full Pipeline

```powershell
cd "d:\Meme GPT"

# Step 1: Collect memes (if not already done)
python scripts/build_huge_dataset.py

# Step 2: Full image processing + embedding + indexing
python scripts/full_index_pipeline.py
```

**Expected time:** 15-30 minutes for 5,000 memes on CPU (BLIP is ~0.3s per image)

---

## Verification Checklist

- [ ] `image_processing_service.py` exists in `backend/app/services/`
- [ ] BLIP generates captions like "a man pointing at a screen"
- [ ] CLIP generates 512-dim non-zero vectors for images
- [ ] OCR extracts text like "ONE DOES NOT SIMPLY"
- [ ] Qdrant collection has all 3 vector spaces populated
- [ ] Search quality improves with image-enriched embeddings
