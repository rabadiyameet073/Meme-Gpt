"""
Text Embedding Service — MiniLM-L6-v2 (80 MB, Apache 2.0).
Loaded once at startup via FastAPI lifespan.
Real-time inference: ~50ms on CPU.
Falls back to hash-based vector if model unavailable.

Also handles emotion detection via j-hartmann/emotion-english-distilroberta-base
(250 MB, MIT). Real-time: ~100ms on CPU.
"""
import logging
from typing import Optional

logger = logging.getLogger("services.embedding")

EMOTIONS_7 = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]


class EmbeddingService:
    def __init__(self):
        self._text_model = None           # MiniLM-L6-v2
        self._emotion_pipeline = None     # DistilRoBERTa
        self._model_loaded = False
        self._emotion_loaded = False

    # ── Startup / Shutdown ───────────────────────────────────────────────────

    def load_models(self) -> None:
        """Called once at app startup via lifespan hook."""
        self._load_text_model()
        self._load_emotion_model()

    def _load_text_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._text_model = SentenceTransformer("all-MiniLM-L6-v2")
            self._model_loaded = True
            logger.info("MiniLM-L6-v2 loaded (384-dim text embedding).")
        except Exception as e:
            logger.warning(f"MiniLM unavailable: {e} — hash fallback active.")

    def _load_emotion_model(self) -> None:
        try:
            from transformers import pipeline as hf_pipeline
            self._emotion_pipeline = hf_pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True,
                device=-1,  # CPU
            )
            self._emotion_loaded = True
            logger.info("DistilRoBERTa emotion model loaded (7-class).")
        except Exception as e:
            logger.warning(f"Emotion model unavailable: {e} — rule-based fallback active.")

    # ── Text Embedding ────────────────────────────────────────────────────────

    def embed_text(self, text: str) -> list[float]:
        """Returns 384-dim normalised embedding vector."""
        if self._text_model:
            try:
                return self._text_model.encode(
                    text[:512], normalize_embeddings=True
                ).tolist()
            except Exception as e:
                logger.error(f"Embedding error: {e}")
        return self._hash_fallback(text)

    def _hash_fallback(self, text: str) -> list[float]:
        """Deterministic 384-dim fallback when model is unavailable."""
        vec = [0.0] * 384
        for i, ch in enumerate(text[:512]):
            idx = (ord(ch) * 31 + i) % 384
            vec[idx] += 0.1
        mag = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / mag for v in vec]

    # ── Emotion Detection ─────────────────────────────────────────────────────

    def detect_emotion(self, text: str) -> dict:
        """
        Returns {primary, secondary, confidence}.
        Uses DistilRoBERTa if loaded, rule-based otherwise.
        ~100ms on CPU.
        """
        if self._emotion_pipeline:
            try:
                results = self._emotion_pipeline(text[:512])[0]
                sorted_em = sorted(results, key=lambda x: x["score"], reverse=True)
                return {
                    "primary": sorted_em[0]["label"].lower(),
                    "secondary": sorted_em[1]["label"].lower() if len(sorted_em) > 1 else None,
                    "confidence": round(sorted_em[0]["score"], 3),
                }
            except Exception as e:
                logger.error(f"Emotion detection error: {e}")
        return self._rule_emotion(text)

    def _rule_emotion(self, text: str) -> dict:
        t = text.lower()
        if any(k in t for k in ["bug", "error", "fail", "broken", "crash"]):
            return {"primary": "frustration", "secondary": "anger", "confidence": 0.85}
        if any(k in t for k in ["exam", "scared", "fear", "nervous"]):
            return {"primary": "fear", "secondary": "sadness", "confidence": 0.80}
        if any(k in t for k in ["win", "success", "finally", "passed"]):
            return {"primary": "joy", "secondary": "surprise", "confidence": 0.90}
        if any(k in t for k in ["monday", "tired", "hate", "ugh"]):
            return {"primary": "sadness", "secondary": "neutral", "confidence": 0.75}
        return {"primary": "neutral", "secondary": "joy", "confidence": 0.60}

    # ── Query Building ────────────────────────────────────────────────────────

    def build_query_text(self, user_text: str, intent: dict, emotion: dict) -> str:
        """
        Combine original input + LLM parsed intent + detected emotion
        into a single rich text for embedding.
        """
        parts = [
            f"User said: {user_text}",
            f"Situation: {intent.get('situation', '')}",
            f"Emotion: {emotion.get('primary', 'neutral')}, {emotion.get('secondary', '')}",
            f"Tone: {intent.get('tone', '')}",
            f"Keywords: {', '.join(intent.get('keywords', []))}",
            f"Meme type needed: {intent.get('meme_format', 'reaction')}",
        ]
        return "\n".join(p for p in parts if p.split(": ", 1)[-1].strip())


embedding_service = EmbeddingService()
