"""MemeGPT — Vector Search Service (Qdrant + Fallback).

Searches for similar memes using vector embeddings via Qdrant.
Falls back to in-memory cosine similarity when Qdrant is unavailable.

Target latency: ~50ms per search.

Specification: 03_ML_PIPELINE_AND_TRAINING.md, Low_Level_Architecture.md
"""

import json
import logging
import math
from pathlib import Path
from typing import Optional

from app.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_HOST,
    QDRANT_PORT,
    QDRANT_COLLECTION,
    EMBEDDING_DIM,
    DATA_DIR,
)

logger = logging.getLogger("memegpt.search")

_qdrant_client = None
_qdrant_available = None  # None = not checked yet
_local_index: dict[str, dict] | None = None


def _get_qdrant():
    """Lazy-initialize Qdrant client."""
    global _qdrant_client, _qdrant_available

    if _qdrant_available is False:
        return None
    if _qdrant_client is not None:
        return _qdrant_client

    try:
        from qdrant_client import QdrantClient

        if QDRANT_URL:
            _qdrant_client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY or None,
                timeout=10,
            )
        else:
            _qdrant_client = QdrantClient(
                host=QDRANT_HOST,
                port=QDRANT_PORT,
                timeout=10,
            )

        # Verify collection exists
        collections = _qdrant_client.get_collections().collections
        names = [c.name for c in collections]
        if QDRANT_COLLECTION in names:
            count = _qdrant_client.get_collection(QDRANT_COLLECTION).points_count
            logger.info(f"✅ Qdrant connected — collection '{QDRANT_COLLECTION}' has {count} vectors")
            _qdrant_available = True
        else:
            logger.warning(f"Qdrant collection '{QDRANT_COLLECTION}' not found. Using local fallback.")
            _qdrant_available = False
            _qdrant_client = None

    except Exception as e:
        logger.warning(f"Qdrant not available ({e}). Using local fallback search.")
        _qdrant_available = False
        _qdrant_client = None

    return _qdrant_client


def _load_local_index() -> dict[str, dict]:
    """Load pre-computed embeddings from local JSON file for fallback search."""
    global _local_index
    if _local_index is not None:
        return _local_index

    _local_index = {}
    path = DATA_DIR / "embeddings.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for item in data:
                _local_index[item["id"]] = {
                    "vector": item["vector"],
                    "payload": item.get("payload", {}),
                }
            logger.info(f"Loaded {len(_local_index)} embeddings for local fallback search")
        except Exception as e:
            logger.error(f"Failed to load embeddings file: {e}")
    else:
        logger.warning(f"No embeddings file at {path} — local search will be limited")

    return _local_index


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    dot = sum(a[i] * b[i] for i in range(n))
    mag_a = math.sqrt(sum(x * x for x in a[:n]))
    mag_b = math.sqrt(sum(x * x for x in b[:n]))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def search(
    query_vector: list[float],
    emotion: str = "",
    format_pref: str = "",
    nsfw: bool = False,
    top_k: int = 10,
) -> list[dict]:
    """Search for similar memes using vector similarity.

    First tries Qdrant, then falls back to local in-memory search.

    Returns a list of dicts with keys: id, score, meme (payload dict).
    """
    client = _get_qdrant()

    if client is not None:
        return _qdrant_search(client, query_vector, emotion, format_pref, nsfw, top_k)
    else:
        return _local_search(query_vector, emotion, format_pref, top_k)


def _qdrant_search(
    client,
    query_vector: list[float],
    emotion: str,
    format_pref: str,
    nsfw: bool,
    top_k: int,
) -> list[dict]:
    """Search using Qdrant vector database."""
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Build filter conditions
        conditions = []
        if not nsfw:
            conditions.append(FieldCondition(key="nsfw", match=MatchValue(value=False)))
        if format_pref == "gif":
            conditions.append(FieldCondition(key="has_gif", match=MatchValue(value=True)))
        elif format_pref in ("video", "mp4"):
            conditions.append(FieldCondition(key="has_video", match=MatchValue(value=True)))

        query_filter = Filter(must=conditions) if conditions else None

        results = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=0.3,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "meme": hit.payload or {},
            }
            for hit in results
        ]

    except Exception as e:
        logger.error(f"Qdrant search failed: {e}")
        return _local_search(query_vector, emotion, format_pref, top_k)


def _local_search(
    query_vector: list[float],
    emotion: str,
    format_pref: str,
    top_k: int,
) -> list[dict]:
    """Fallback: search using local in-memory embeddings with cosine similarity."""
    index = _load_local_index()

    if not index:
        logger.warning("No local index available for search")
        return []

    scored = []
    for meme_id, entry in index.items():
        vec = entry["vector"]
        sim = _cosine_similarity(query_vector, vec)

        # Small bonus for emotion match
        payload = entry.get("payload", {})
        if emotion and emotion in str(payload.get("emotions", [])):
            sim += 0.05

        # Small bonus for format match
        if format_pref == "gif" and payload.get("has_gif"):
            sim += 0.02
        elif format_pref in ("video", "mp4") and payload.get("has_video"):
            sim += 0.02

        scored.append({
            "id": meme_id,
            "score": min(sim, 1.0),
            "meme": payload,
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
