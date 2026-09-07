"""
MemeGPT — Image Processing Service for Meme Indexing.

Runs OFFLINE (during indexing, not real-time).
Models:
  - BLIP: Auto-generate captions for meme images (446MB)
  - CLIP: Generate 512-dim image embeddings (400MB)
  - Tesseract: OCR text extraction from meme images (20MB)

Specification: 03_ML_PIPELINE_AND_TRAINING.md, Guide 03
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
        logger.info("BLIP model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load BLIP: {e}")


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
        logger.info("CLIP model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load CLIP: {e}")


def generate_caption(image_path: str) -> str:
    """
    Generate a natural language caption for a meme image using BLIP.
    Example output: "a man in a suit pointing at a television"
    """
    if not image_path or not os.path.exists(image_path):
        return ""

    if _blip_model is None:
        load_blip()
    if _blip_model is None or _blip_processor is None:
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
    """
    if not image_path or not os.path.exists(image_path):
        return [0.0] * 512

    if _clip_model is None:
        load_clip()
    if _clip_model is None or _clip_processor is None:
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
    """
    if not image_path or not os.path.exists(image_path):
        return ""

    try:
        import pytesseract
        from PIL import Image, ImageFilter

        if sys.platform == "win32":
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path

        img = Image.open(image_path)
        img = img.convert("L")  # Grayscale
        img = img.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")
        return text.strip()
    except Exception as e:
        logger.debug(f"OCR skipped or failed for {image_path}: {e}")
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
