"""
MemeGPT — Image Processing Service for Meme Indexing.
Consolidated adapter pointing to the unified image_analysis_service.
"""
from typing import Dict, List, Optional
from app.services.image_analysis_service import (
    _get_blip,
    _get_clip,
    extract_text as extract_text_ocr,
    generate_caption,
    embed_image as generate_image_embedding,
    process_meme,
)

def load_blip():
    """Load BLIP captioning model."""
    _get_blip()

def load_clip():
    """Load CLIP image embedding model."""
    _get_clip()

def process_meme_image(image_path: str) -> Dict:
    """Full image processing pipeline for a single meme."""
    res = process_meme(image_path, "")
    return {
        "caption": res.get("blip_caption", ""),
        "ocr_text": res.get("ocr_text", ""),
        "image_embedding": res.get("image_embedding", [0.0] * 512),
    }

__all__ = [
    "load_blip",
    "load_clip",
    "generate_caption",
    "generate_image_embedding",
    "extract_text_ocr",
    "process_meme_image",
]
