"""
MemeGPT — Embedding & Emotion Detection Service (FIXED & FULL SPECIFICATION).

Stage B of AI pipeline:
- Text embedding with all-MiniLM-L6-v2 (384 dimensions)
- Emotion detection with j-hartmann/emotion-english-distilroberta-base
- Zero-vector guards and rule-based fallbacks

Specification:
- 05_AI_Pipeline_Fix.md
- 03_ML_PIPELINE_AND_TRAINING.md
"""

import logging
import os
import math
import hashlib
from typing import Optional, List, Dict, Any

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

from app.config import settings

logger = logging.getLogger("memegpt.embedding")

_text_model = None
_emotion_pipeline = None

EMBEDDING_MODEL = getattr(settings, "EMBEDDING_MODEL", "all-MiniLM-L6-v2") or "all-MiniLM-L6-v2"
EMOTION_MODEL = getattr(settings, "EMOTION_MODEL", "j-hartmann/emotion-english-distilroberta-base") or "j-hartmann/emotion-english-distilroberta-base"
MODELS_CACHE_DIR = getattr(settings, "MODELS_CACHE_DIR", "./model_cache") or "./model_cache"


def load_models():
    """Load ML models at startup. Called from main.py lifespan."""
    global _text_model, _emotion_pipeline
    try:
        import torch
        torch.set_num_threads(2)
    except Exception:
        pass

    try:
        os.makedirs(MODELS_CACHE_DIR, exist_ok=True)
    except Exception:
        pass

    # Load sentence transformer for text embedding
    try:
        from sentence_transformers import SentenceTransformer
        _text_model = SentenceTransformer(
            EMBEDDING_MODEL,
            cache_folder=MODELS_CACHE_DIR
        )

        logger.info(f"✅ Text embedding model loaded: {EMBEDDING_MODEL}")
    except Exception as e:
        logger.warning(f"SentenceTransformer not loaded ({e}) — using fallback vector generator")

    # Load emotion classifier
    try:
        from transformers import pipeline
        _emotion_pipeline = pipeline(
            "text-classification",
            model=EMOTION_MODEL,
            top_k=None,
            device=-1,  # CPU only
        )
        logger.info(f"✅ Emotion model loaded: {EMOTION_MODEL}")
    except Exception as e:
        logger.warning(f"Emotion model not loaded ({e}) — rule-based fallback active")

    try:
        import gc
        gc.collect()
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


def embed_text(text: str) -> List[float]:
    """Encode text to 384-dim normalized vector. Returns pseudo-embedding if model not loaded."""
    if _text_model is None:
        return _fallback_embed(text)

    try:
        vector = _text_model.encode(
            (text or "")[:512],
            normalize_embeddings=True,
        )
        return vector.tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return _fallback_embed(text)


def _fallback_embed(text: str) -> List[float]:
    """Deterministic 384-dim vector for testing/fallback with unit norm."""
    clean = (text or "meme").encode("utf-8")
    h = hashlib.sha256(clean).digest()
    vec = [(float(b) / 128.0 - 1.0) for b in (h * 12)[:384]]
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(x / norm, 6) for x in vec]


def is_text_model_loaded() -> bool:
    """True only when the real MiniLM encoder is resident in memory.

    Callers use this to decide whether a cosine similarity computed from
    :func:`embed_text` is semantically meaningful or merely the deterministic
    SHA-256 placeholder produced by :func:`_fallback_embed`.
    """
    return _text_model is not None


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Encode many texts in one pass (much faster than repeated embed_text)."""
    clean = [(t or "")[:512] for t in texts]
    if not clean:
        return []

    if _text_model is None:
        return [_fallback_embed(t) for t in clean]

    try:
        vectors = _text_model.encode(clean, normalize_embeddings=True, batch_size=32)
        return [v.tolist() for v in vectors]
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        return [_fallback_embed(t) for t in clean]


def build_meme_text(meme: dict) -> str:
    """Canonical text used to embed a single meme.

    Kept in one place so the offline indexer (``generate_embeddings.py``) and
    the on-the-fly semantic fallback in ``search_service`` always embed the
    exact same representation.
    """
    def _list(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v) for v in value if v]
        if isinstance(value, str) and value.strip():
            return [value]
        return []

    categories = _list(meme.get("categories")) or _list(meme.get("category"))
    emotions = _list(meme.get("emotions")) or _list(meme.get("emotion"))
    keywords = _list(meme.get("keywords"))

    parts = [f"Meme: {meme.get('name', '')}"]
    if categories:
        parts.append(f"Category: {', '.join(categories)}")
    if emotions:
        parts.append(f"Emotions: {', '.join(emotions)}")
    if meme.get("dialogue"):
        parts.append(f"Text on meme: {meme['dialogue']}")
    if meme.get("explanation"):
        parts.append(f"When to use: {meme['explanation']}")
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords[:12])}")
    return "\n".join(parts)


def detect_emotion(text: str) -> Dict[str, Any]:
    """
    Detect primary and secondary emotion in text.
    Returns: {primary, secondary, confidence, all}
    """
    if _emotion_pipeline is None:
        return _rule_based_emotion(text)

    try:
        clean = (text or "")[:512]
        if not clean.strip():
            return _rule_based_emotion("")

        results = _emotion_pipeline(clean)[0]
        sorted_emotions = sorted(results, key=lambda x: x["score"], reverse=True)
        return {
            "primary": sorted_emotions[0]["label"],
            "secondary": sorted_emotions[1]["label"] if len(sorted_emotions) > 1 else None,
            "confidence": round(sorted_emotions[0]["score"], 3),
            "all": {e["label"]: round(e["score"], 3) for e in sorted_emotions},
        }
    except Exception as e:
        logger.warning(f"Emotion detection failed: {e}")
        return _rule_based_emotion(text)


def _rule_based_emotion(text: str) -> Dict[str, Any]:
    """Fast keyword-based emotion fallback."""
    text_lower = (text or "").lower()
    emotions = {
        "joy": ["happy", "great", "awesome", "yay", "win", "won", "winner", "prize", "love", "celebrate", "proud", "finally", "success", "promoted"],
        "anger": ["angry", "hate", "stupid", "annoying", "terrible", "awful", "furious", "rage", "frustrated"],
        "sadness": ["sad", "cry", "upset", "miss", "alone", "lost", "depressed", "disappointed"],
        "surprise": ["wow", "what", "seriously", "shocked", "unexpected", "omg", "unbelievable"],
        "fear": ["scared", "nervous", "worried", "panic", "stress", "anxiety", "deadline"],
        "disgust": ["disgusting", "gross", "ugh", "eww", "nasty", "awful"],
    }

    for emotion, keywords in emotions.items():
        if any(kw in text_lower for kw in keywords):
            return {
                "primary": emotion,
                "secondary": None,
                "confidence": 0.7,
                "all": {emotion: 0.7, "neutral": 0.3}
            }
    return {
        "primary": "neutral",
        "secondary": None,
        "confidence": 0.5,
        "all": {"neutral": 0.5}
    }


def build_query_text(user_text: str, intent: dict, emotion: dict) -> str:
    """
    Combine original input + LLM intent + detected emotion into rich query text.
    Richer text = better MiniLM embedding = better vector search results.
    """
    parts = [f"User said: {user_text}"]

    if intent.get("situation"):
        parts.append(f"Situation: {intent['situation']}")

    primary_emotion = emotion.get("primary") or intent.get("emotion_hint", "neutral")
    parts.append(f"Primary emotion: {primary_emotion}")

    if emotion.get("secondary"):
        parts.append(f"Secondary emotion: {emotion['secondary']}")

    if intent.get("tone"):
        parts.append(f"Tone: {intent['tone']}")

    if intent.get("keywords"):
        kws = intent["keywords"]
        parts.append(f"Keywords: {', '.join(kws) if isinstance(kws, list) else str(kws)}")

    if intent.get("meme_format"):
        parts.append(f"Meme format: {intent['meme_format']}")

    return "\n".join(parts)


# Compatibility aliases
get_text_embedding = embed_text


def is_loaded() -> bool:
    """Return True if ML embedding models are loaded in memory."""
    return _text_model is not None or _emotion_pipeline is not None


def embed_meme(meme: dict) -> List[float]:
    """Embed a meme dict using its combined name, explanation, and tags."""
    return embed_text(build_meme_text(meme))


def get_combined_embedding(
    text_or_emb: Any,
    image_vector: Optional[List[float]] = None,
    text_weight: float = 0.65,
    image_weight: float = 0.35,
) -> List[float]:
    """Return weighted 896-dim multimodal or 384-dim text embedding vector."""
    if isinstance(text_or_emb, list):
        text_emb = text_or_emb
    else:
        text_emb = embed_text(str(text_or_emb or ""))

    if image_vector is None:
        return text_emb

    import numpy as np
    text_arr = np.array(text_emb, dtype=np.float32) * float(text_weight)
    image_arr = np.array(image_vector, dtype=np.float32) * float(image_weight)
    combined = np.concatenate([text_arr, image_arr])
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    return combined.tolist()

