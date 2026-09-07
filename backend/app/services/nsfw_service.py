"""
NSFW Content Classification using CLIP zero-shot.
Uses CLIP's text-image alignment to classify memes as safe/nsfw.
Runs during indexing and on user-uploaded content.
"""
import logging
import os
import tempfile
from typing import Tuple

logger = logging.getLogger("memegpt.nsfw")

_clip_model = None
_clip_processor = None
MODELS_CACHE_DIR = os.getenv("MODELS_CACHE_DIR", "./model_cache")

NSFW_LABELS = ["safe content", "nsfw adult content", "violent content", "hate speech imagery"]
NSFW_THRESHOLD = 0.45  # Score above this = flagged


def _load_clip():
    global _clip_model, _clip_processor
    if _clip_model is not None:
        return
    try:
        from transformers import CLIPModel, CLIPProcessor
        _clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32", cache_dir=MODELS_CACHE_DIR
        )
        _clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32", cache_dir=MODELS_CACHE_DIR
        )
        logger.info("NSFW CLIP classifier loaded")
    except Exception as e:
        logger.error(f"Failed to load CLIP for NSFW: {e}")


def classify_image(image_path: str) -> Tuple[bool, float, str]:
    """
    Classify an image as NSFW or safe using CLIP zero-shot.

    Returns: (is_nsfw: bool, confidence: float, category: str)
    """
    _load_clip()
    if _clip_model is None or _clip_processor is None:
        return False, 0.0, "safe content"

    try:
        import torch
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        inputs = _clip_processor(
            text=NSFW_LABELS, images=image, return_tensors="pt", padding=True
        )

        with torch.no_grad():
            outputs = _clip_model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]

        scores = {label: float(prob) for label, prob in zip(NSFW_LABELS, probs)}
        nsfw_score = max(scores.get("nsfw adult content", 0), scores.get("violent content", 0))
        top_label = max(scores, key=scores.get)

        is_nsfw = nsfw_score > NSFW_THRESHOLD
        return is_nsfw, nsfw_score, top_label

    except Exception as e:
        logger.warning(f"NSFW classification failed for {image_path}: {e}")
        return False, 0.0, "safe content"


def classify_image_from_url(url: str) -> Tuple[bool, float, str]:
    """Download image from URL and classify."""
    import requests
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(resp.content)
                temp_path = f.name
            try:
                return classify_image(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        return False, 0.0, "safe content"
    except Exception as e:
        logger.warning(f"Failed to classify image from URL {url}: {e}")
        return False, 0.0, "safe content"
