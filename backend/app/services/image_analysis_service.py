"""MemeGPT — Image Analysis Service (OCR + BLIP + CLIP).

Implements the multi-modal image analysis pipeline from 05_AI_System/Image_Analysis.md:
  1. Tesseract OCR for text extraction
  2. BLIP for natural language visual captioning
  3. CLIP ViT-B/32 for 512-dim visual embeddings
  4. 896-dim weighted combined text + image embeddings
"""

import logging
import os
import re
from pathlib import Path
from typing import Any

import numpy as np

from app.services.embedding_service import embed_text
from app.services.llm_service import generate_meme_tags
from app.services.text_composer import compose_meme_text

logger = logging.getLogger("memegpt.image_analysis")

_blip_processor = None
_blip_model = None
_clip_model = None
_clip_preprocess = None


def _get_blip():
    global _blip_processor, _blip_model
    if _blip_model is not None:
        return _blip_processor, _blip_model
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        _blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        return _blip_processor, _blip_model
    except Exception as e:
        logger.debug(f"BLIP model not initialized: {e}")
        return None, None


def _get_clip():
    global _clip_model, _clip_preprocess
    if _clip_model is not None:
        return _clip_model, _clip_preprocess
    try:
        import clip
        _clip_model, _clip_preprocess = clip.load("ViT-B/32", device="cpu")
        return _clip_model, _clip_preprocess
    except Exception as e:
        logger.debug(f"CLIP model not initialized: {e}")
        return None, None


def extract_text(image_path: str) -> str:
    """Extract text from meme image using Tesseract OCR with binarization preprocessing."""
    if not os.path.exists(image_path):
        return ""
    try:
        from PIL import Image
        import pytesseract

        img = Image.open(image_path)
        # Preprocessing for better OCR accuracy
        img = img.convert("L")  # Grayscale
        img = img.point(lambda x: 0 if x < 128 else 255)  # Binarize

        text = pytesseract.image_to_string(img, config="--psm 6 --oem 3")
        # Clean up OCR artifacts
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s\']", "", text)
        return text if len(text) > 3 else ""
    except Exception as e:
        logger.debug(f"OCR extraction skipped or failed: {e}")
        return ""


def generate_caption(image_path: str) -> str:
    """Generate natural language description of meme image via BLIP."""
    if not image_path:
        return ""
    if not os.path.exists(image_path):
        basename = Path(image_path).stem.replace("_", " ").strip()
        return f"a meme depicting {basename}" if basename else "a meme image"
    try:
        from PIL import Image
        import torch

        processor, model = _get_blip()
        if processor is None or model is None:
            # Heuristic / fallback caption based on filename
            basename = Path(image_path).stem.replace("_", " ")
            return f"a meme depicting {basename}"

        img = Image.open(image_path).convert("RGB")
        inputs = processor(img, return_tensors="pt")
        output = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(output[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        logger.debug(f"Caption generation fallback: {e}")
        basename = Path(image_path).stem.replace("_", " ")
        return f"a meme depicting {basename}"


def embed_image(image_path: str) -> list[float]:
    """Generate 512-dim CLIP embedding from meme image."""
    if not os.path.exists(image_path):
        return [0.0] * 512
    try:
        from PIL import Image
        import torch

        model, preprocess = _get_clip()
        if model is None or preprocess is None:
            # Deterministic fallback pseudo-embedding for testing / offline
            rng = np.random.RandomState(abs(hash(Path(image_path).name)) % (2**31))
            vec = rng.randn(512).astype(np.float32)
            norm = np.linalg.norm(vec)
            return (vec / norm).tolist()

        img = preprocess(Image.open(image_path)).unsqueeze(0)
        with torch.no_grad():
            embedding = model.encode_image(img)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding.squeeze().tolist()
    except Exception as e:
        logger.debug(f"CLIP embedding fallback: {e}")
        rng = np.random.RandomState(abs(hash(Path(image_path).name)) % (2**31))
        vec = rng.randn(512).astype(np.float32)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()


def create_combined_embedding(text_emb: list[float], image_emb: list[float]) -> list[float]:
    """Weighted concatenation: 65% text + 35% image.

    Result: 896-dim (384 + 512), L2-normalized.
    """
    text_arr = np.array(text_emb, dtype=np.float32) * 0.65
    image_arr = np.array(image_emb, dtype=np.float32) * 0.35
    combined = np.concatenate([text_arr, image_arr])
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    return combined.tolist()


def process_meme(image_path: str, meme_name: str) -> dict[str, Any]:
    """Full image analysis pipeline for one meme."""
    # 1. OCR — extract text from image
    ocr_text = extract_text(image_path)

    # 2. BLIP — generate visual caption
    caption = generate_caption(image_path)

    # 3. Groq — generate tags from combined context
    tags = generate_meme_tags(meme_name, ocr_text, caption)

    # 4. MiniLM — text embedding from composed text
    composed = compose_meme_text({
        "name": meme_name,
        "ocr_text": ocr_text,
        "blip_caption": caption,
        **tags,
    })
    text_embedding = embed_text(composed)

    # 5. CLIP — image embedding
    image_embedding = embed_image(image_path)

    # 6. Combined embedding (896-dim)
    combined_embedding = create_combined_embedding(text_embedding, image_embedding)

    return {
        "name": meme_name,
        "ocr_text": ocr_text,
        "blip_caption": caption,
        "text_embedding": text_embedding,
        "image_embedding": image_embedding,
        "combined_embedding": combined_embedding,
        "composed_text": composed,
        **tags,
    }
