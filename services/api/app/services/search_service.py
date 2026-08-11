"""
Vector Search Service — Qdrant with graceful local fallback.
Uses local in-memory data from backend/data/embeddings.json when Qdrant unavailable.
Target: ~50ms on Qdrant Cloud, near-instant on local.
"""
import json
import logging
import math
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("services.search")

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"
EMBEDDINGS_FILE = DATA_DIR / "embeddings" / "memes_with_embeddings.json"
BACKEND_EMBEDDINGS = Path(__file__).resolve().parent.parent.parent.parent.parent / "backend" / "data" / "embeddings.json"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class QdrantSearchService:
    def __init__(self):
        self._qdrant = None
        self._attempted = False
        self._local_index: list[dict] = []
        self._collection = "memes"

    def _get_qdrant(self):
        if self._attempted:
            return self._qdrant
        self._attempted = True
        try:
            from qdrant_client import QdrantClient
            from app.core.config import settings
            url = settings.QDRANT_URL
            api_key = settings.QDRANT_API_KEY or None
            self._qdrant = QdrantClient(url=url, api_key=api_key, timeout=5)
            self._qdrant.get_collections()
            logger.info(f"Qdrant connected: {url}")
        except Exception as e:
            logger.warning(f"Qdrant unavailable: {e} — using local cosine search fallback.")
            self._qdrant = None
            self._load_local_index()
        return self._qdrant

    def _load_local_index(self) -> None:
        """Load pre-computed embeddings from JSON for offline dev."""
        for path in [EMBEDDINGS_FILE, BACKEND_EMBEDDINGS]:
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._local_index = json.load(f)
                    logger.info(f"Loaded {len(self._local_index)} memes from local index: {path}")
                    return
                except Exception as e:
                    logger.warning(f"Could not load {path}: {e}")
        # Fall back to built-in demo data so the app works before the pipeline runs
        try:
            from app.core.demo_data import DEMO_MEMES
            self._local_index = DEMO_MEMES
            logger.info(f"Loaded {len(DEMO_MEMES)} demo memes (run data pipeline for full index).")
        except Exception as e:
            logger.warning(f"Could not load demo data: {e}")

    def search(
        self,
        query_vector: list[float],
        emotion: str = "neutral",
        format_pref: str = "any",
        nsfw: bool = False,
        top_k: int = 10,
    ) -> list[dict]:
        """Vector search with filter support."""
        client = self._get_qdrant()
        if client:
            return self._qdrant_search(query_vector, emotion, format_pref, nsfw, top_k)
        return self._local_search(query_vector, format_pref, nsfw, top_k)

    def _qdrant_search(
        self, query_vector, emotion, format_pref, nsfw, top_k
    ) -> list[dict]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        conditions = [FieldCondition(key="nsfw", match=MatchValue(value=nsfw))]
        if format_pref == "gif":
            conditions.append(FieldCondition(key="has_gif", match=MatchValue(value=True)))
        elif format_pref == "video":
            conditions.append(FieldCondition(key="has_video", match=MatchValue(value=True)))
        from qdrant_client.models import Filter
        search_filter = Filter(must=conditions)
        try:
            results = self._qdrant.search(
                collection_name=self._collection,
                query_vector=("text", query_vector),
                query_filter=search_filter,
                limit=top_k,
                with_payload=True,
                score_threshold=0.40,
            )
            return [{"meme": r.payload, "score": r.score} for r in results]
        except Exception as e:
            logger.error(f"Qdrant search error: {e}")
            return []

    def _local_search(self, query_vector, format_pref, nsfw, top_k) -> list[dict]:
        """Cosine similarity search on local embeddings.json."""
        if not self._local_index:
            return []
        scored = []
        for meme in self._local_index:
            emb = meme.get("text_embedding") or meme.get("embedding", [])
            if not emb:
                continue
            if meme.get("nsfw", False) and not nsfw:
                continue
            score = _cosine_similarity(query_vector, emb)
            if score > 0.3:
                scored.append({"meme": meme, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


search_service = QdrantSearchService()
