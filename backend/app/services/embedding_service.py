"""MemeGPT — Embedding & Emotion Detection Service.

Loads two models at startup (not per-request):
  1. SentenceTransformer (all-MiniLM-L6-v2) → 384-dim text embeddings
  2. DistilRoBERTa (j-hartmann) → 7-class emotion detection

Specification: 03_ML_PIPELINE_AND_TRAINING.md, 02_TECH_STACK_AND_MODELS.md
"""

import logging
from typing import Optional

import numpy as np

from app.config import EMBEDDING_MODEL, EMOTION_MODEL, EMBEDDING_DIM

logger = logging.getLogger("memegpt.embedding")

# ── Globals: loaded once at startup via load_models() ─────────────────────────
_st_model = None
_emotion_pipeline = None
_models_loaded = False


def load_models() -> None:
    """Load ML models into memory. Called once during FastAPI lifespan startup."""
    global _st_model, _emotion_pipeline, _models_loaded

    if _models_loaded:
        return

    # 1. Text Embedding Model (all-MiniLM-L6-v2, ~80MB)
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _st_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"✅ Embedding model loaded ({EMBEDDING_DIM}-dim)")
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformer: {e}")
        _st_model = None

    # 2. Emotion Detection Model (DistilRoBERTa, ~260MB)
    try:
        from transformers import pipeline
        logger.info(f"Loading emotion model: {EMOTION_MODEL}")
        _emotion_pipeline = pipeline(
            "text-classification",
            model=EMOTION_MODEL,
            top_k=None,
            truncation=True,
        )
        logger.info("✅ Emotion model loaded")
    except Exception as e:
        logger.warning(f"Could not load emotion model: {e}")
        _emotion_pipeline = None

    _models_loaded = True


# ── Public API ────────────────────────────────────────────────────────────────


def embed_text(text: str) -> list[float]:
    """Generate a 384-dim embedding vector for the given text.

    Falls back to a zero vector if the model is unavailable.
    """
    if _st_model is None:
        logger.debug("Embedding model not loaded, returning zero vector")
        return [0.0] * EMBEDDING_DIM

    try:
        vector = _st_model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return vector.tolist()
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return [0.0] * EMBEDDING_DIM


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batch embed multiple texts efficiently."""
    if _st_model is None:
        return [[0.0] * EMBEDDING_DIM for _ in texts]
    try:
        vectors = _st_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, batch_size=64)
        return vectors.tolist()
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        return [[0.0] * EMBEDDING_DIM for _ in texts]


def detect_emotion(text: str) -> dict:
    """Detect emotions from user text using the DistilRoBERTa classifier.

    Returns:
        {
            "primary": "joy",
            "confidence": 0.87,
            "all": {"joy": 0.87, "sadness": 0.05, ...}
        }

    Falls back to regex-based detection from rule_engine if model unavailable.
    """
    if _emotion_pipeline is None:
        # Fallback to rule-based emotion detection
        from app.rule_engine import detect_emotion as rule_detect
        return rule_detect(text)

    try:
        results = _emotion_pipeline(text[:512])  # Truncate to model max
        if results and isinstance(results[0], list):
            results = results[0]

        # Map model labels to our emotion taxonomy
        label_map = {
            "anger": "frustration",
            "disgust": "frustration",
            "fear": "anxiety",
            "joy": "triumph",
            "neutral": "humor",
            "sadness": "despair",
            "surprise": "humor",
        }

        emotion_scores = {}
        for item in results:
            label = item["label"].lower()
            mapped = label_map.get(label, label)
            score = item["score"]
            emotion_scores[mapped] = emotion_scores.get(mapped, 0) + score

        # Find primary emotion
        primary = max(emotion_scores, key=emotion_scores.get)
        confidence = round(emotion_scores[primary], 3)

        return {
            "primary": primary,
            "confidence": confidence,
            "all": {k: round(v, 3) for k, v in emotion_scores.items()},
        }

    except Exception as e:
        logger.error(f"Emotion detection failed: {e}")
        from app.rule_engine import detect_emotion as rule_detect
        return rule_detect(text)


def build_query_text(user_text: str, intent: dict, emotion: dict) -> str:
    """Build enriched query text for embedding by combining user text with parsed intent.

    As specified in 03_ML_PIPELINE_AND_TRAINING.md:
    'The query text sent to the embedding model is enriched with intent + emotion context.'
    """
    parts = [user_text]

    # Add intent keywords
    keywords = intent.get("keywords", [])
    if keywords:
        parts.append(" ".join(keywords))

    # Add emotion context
    primary_emo = emotion.get("primary", "")
    if primary_emo:
        parts.append(primary_emo)

    # Add situation context
    situation = intent.get("situation", "")
    if situation and situation != user_text:
        parts.append(situation)

    return " ".join(parts)


def is_loaded() -> bool:
    """Check if models are loaded and ready."""
    return _models_loaded


get_text_embedding = embed_text
embed_meme = embed_text

