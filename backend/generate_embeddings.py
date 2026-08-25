#!/usr/bin/env python3
"""
MemeGPT — Complete Meme Indexing Pipeline (FIXED).

Pipeline:
  DB memes → download images → OCR + BLIP caption → MiniLM text embed
  → CLIP image embed → upsert to Qdrant with full payload

Run: python generate_embeddings.py [--limit 100] [--recreate] [--skip-images]
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


def load_models(skip_images: bool = False):
    """Load ML models needed for indexing."""
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

    if skip_images:
        models["clip"] = None
        models["clip_processor"] = None
        models["blip"] = None
        models["blip_processor"] = None
        return models

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
        if os.name == "nt":
            tesseract_cmd = os.getenv(
                "TESSERACT_CMD",
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )
            if os.path.exists(tesseract_cmd):
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        text = pytesseract.image_to_string(image, config="--psm 11")
        return text.strip()[:300]
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
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features[0].tolist()
    except Exception as e:
        logger.debug(f"CLIP embedding failed: {e}")
        return None


def embed_text(text: str, models: dict) -> list[float]:
    """Generate 384-dim MiniLM embedding for text."""
    if not models.get("text"):
        # Fallback
        from app.services.embedding_service import embed_text as fallback_embed
        return fallback_embed(text)
    try:
        vector = models["text"].encode(text[:512], normalize_embeddings=True)
        return vector.tolist()
    except Exception as e:
        logger.debug(f"Text embedding failed: {e}")
        from app.services.embedding_service import embed_text as fallback_embed
        return fallback_embed(text)


def build_rich_text(meme: dict, ocr_text: str = "", caption: str = "") -> str:
    """Build rich text combining all meme attributes for better embedding."""
    parts = []

    if meme.get("name"):
        parts.append(f"Meme: {meme['name']}")

    categories = meme.get("categories", []) or [meme.get("category", "general")]
    if categories:
        parts.append(f"Category: {', '.join(categories) if isinstance(categories, list) else str(categories)}")

    emotions = meme.get("emotions", [])
    if emotions:
        parts.append(f"Emotions: {', '.join(emotions) if isinstance(emotions, list) else str(emotions)}")

    if meme.get("dialogue"):
        parts.append(f"Text on meme: {meme['dialogue']}")

    if meme.get("explanation"):
        parts.append(f"When to use: {meme['explanation']}")

    keywords = meme.get("keywords", [])
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords[:10]) if isinstance(keywords, list) else str(keywords)}")

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
    os.environ.setdefault("APP_ENV", "development")

    from app.database import SessionLocal, Meme as MemeModel
    from app.services.search_service import (
        create_qdrant_collection, upsert_memes, get_qdrant_client
    )

    # 1. Initialize Qdrant collection
    logger.info("Initializing Qdrant collection...")
    client = get_qdrant_client()
    if client:
        create_qdrant_collection(recreate=recreate)
    else:
        logger.info("Qdrant not configured — skipping vector database upsert.")

    # 2. Load ML models
    logger.info("Loading ML models...")
    models = load_models(skip_images=skip_images)

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

            # Download image if requested and URL exists
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

            if i % 10 == 0 or i == len(memes):
                logger.info(f"Processed {i}/{len(memes)} memes...")

            # Upsert in batches of 50
            if len(batch) >= 50:
                if client:
                    n = upsert_memes(batch)
                    total_indexed += n
                else:
                    total_indexed += len(batch)
                batch = []

        except Exception as e:
            logger.error(f"Failed to process meme {meme.get('id')}: {e}")
            failed += 1

    # Upsert remaining
    if batch:
        if client:
            n = upsert_memes(batch)
            total_indexed += n
        else:
            total_indexed += len(batch)

    logger.info("=" * 50)
    logger.info("✅ Indexing complete!")
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
