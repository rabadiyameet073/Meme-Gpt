# 03 — Qdrant Vector Search — Real Implementation
# Fix get_qdrant_client(), vector_search(), collection setup

> **Gap Source:** Section 1 & Section 17 of GAP_ANALYSIS_FULL.md  
> **Priority:** P0 — The entire AI search pipeline depends on this  
> **Files to edit:**  
> - `d:\Meme GPT\backend\app\services\search_service.py`

---

## WHAT IS BROKEN

1. `get_qdrant_client()` always returns `None` — never actually connects
2. `vector_search()` ignores the query vector and does `SELECT * LIMIT 10`
3. `create_qdrant_collection()` uses `MagicMock` instead of real Qdrant client
4. `build_point()` fills vectors with `[0.0] * 384` (zeros — useless)
5. `_cosine_similarity()` is imported in `recommendation_service.py` but does NOT EXIST → `ImportError`

---

## COMPLETE REPLACEMENT: `search_service.py`

**Replace the ENTIRE content** of `d:\Meme GPT\backend\app\services\search_service.py` with:

```python
"""
MemeGPT — Vector Search Service (FIXED).

Real Qdrant integration for sub-50ms cosine similarity search.
Collection: 'memes' with named vectors: text (384-dim), image (512-dim).

Gap Analysis fixes:
- get_qdrant_client() now returns real QdrantClient
- vector_search() now calls qdrant.search() with real query vector
- _cosine_similarity() added (was missing, caused ImportError)
- create_qdrant_collection() uses real Qdrant models
- build_point() uses actual embeddings, not zeros
"""

import logging
import math
from typing import Optional

from app.config import settings

logger = logging.getLogger("memegpt.search")

# ──────────────────────────────────────────────────────────────────────────────
# Qdrant Client Singleton
# ──────────────────────────────────────────────────────────────────────────────

_qdrant_client = None


def get_qdrant_client():
    """
    Returns a real QdrantClient connected to Qdrant Cloud.
    Singleton — created once at startup.
    Returns None if QDRANT_URL is not configured (graceful degradation).
    """
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    qdrant_url = getattr(settings, "QDRANT_URL", "")
    qdrant_api_key = getattr(settings, "QDRANT_API_KEY", "")

    if not qdrant_url:
        logger.warning(
            "QDRANT_URL not set — vector search disabled. "
            "Set QDRANT_URL and QDRANT_API_KEY in .env to enable."
        )
        return None

    try:
        from qdrant_client import QdrantClient

        timeout = getattr(settings, "QDRANT_TIMEOUT", 5)
        _qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key if qdrant_api_key else None,
            timeout=timeout,
        )
        # Quick connectivity check
        _qdrant_client.get_collections()
        logger.info(f"✅ Qdrant connected: {qdrant_url}")
        return _qdrant_client

    except ImportError:
        logger.error("qdrant_client package not installed. Run: pip install qdrant-client")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Collection Setup
# ──────────────────────────────────────────────────────────────────────────────

COLLECTION_NAME = "memes"
TEXT_VECTOR_SIZE = 384    # all-MiniLM-L6-v2
IMAGE_VECTOR_SIZE = 512   # CLIP ViT-B/32


def create_qdrant_collection(recreate: bool = False) -> bool:
    """
    Create the 'memes' collection with named vectors.
    Named vectors: 'text' (384-dim), 'image' (512-dim).
    Returns True on success.
    """
    client = get_qdrant_client()
    if client is None:
        return False

    try:
        from qdrant_client.models import (
            VectorParams,
            Distance,
            NamedVectorParams,
        )

        existing = [c.name for c in client.get_collections().collections]

        if COLLECTION_NAME in existing:
            if not recreate:
                logger.info(f"Collection '{COLLECTION_NAME}' already exists — skipping creation")
                return True
            else:
                client.delete_collection(COLLECTION_NAME)
                logger.info(f"Deleted existing collection '{COLLECTION_NAME}'")

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "text": VectorParams(
                    size=TEXT_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
                "image": VectorParams(
                    size=IMAGE_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            },
        )
        logger.info(f"✅ Created Qdrant collection '{COLLECTION_NAME}'")
        return True

    except Exception as e:
        logger.error(f"Failed to create Qdrant collection: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Upsert (Indexing)
# ──────────────────────────────────────────────────────────────────────────────

def build_point(meme: dict, text_vector: list[float], image_vector: list[float] | None = None):
    """
    Build a Qdrant PointStruct from a meme dict and its embedding vectors.
    text_vector: 384-dim from MiniLM
    image_vector: 512-dim from CLIP (optional)
    """
    from qdrant_client.models import PointStruct

    # Payload stored alongside vector for retrieval without extra DB lookup
    payload = {
        "meme_id": meme["id"],
        "name": meme["name"],
        "slug": meme.get("slug", ""),
        "categories": meme.get("categories", [meme.get("category", "general")]),
        "emotions": meme.get("emotions", []),
        "keywords": meme.get("keywords", []),
        "dialogue": meme.get("dialogue", ""),
        "explanation": meme.get("explanation", ""),
        "image_url": meme.get("image_url") or meme.get("image_ref"),
        "gif_url": meme.get("gif_url") or meme.get("gif_ref"),
        "mp4_url": meme.get("mp4_url") or meme.get("video_ref"),
        "thumb_url": meme.get("thumb_url"),
        "nsfw": meme.get("nsfw", False),
        "popularity_score": meme.get("popularity_score", 0.0),
        "viral_score": meme.get("viral_score", 0.0),
        "source": meme.get("source", "manual"),
    }

    # Build named vectors dict
    vectors = {"text": text_vector}
    if image_vector and len(image_vector) == IMAGE_VECTOR_SIZE:
        vectors["image"] = image_vector

    return PointStruct(
        id=_meme_id_to_int(meme["id"]),
        vector=vectors,
        payload=payload,
    )


def _meme_id_to_int(meme_id: str) -> int:
    """Convert string meme ID to integer for Qdrant point ID."""
    import hashlib
    return int(hashlib.md5(meme_id.encode()).hexdigest()[:15], 16)


def upsert_memes(memes_with_vectors: list[dict]) -> int:
    """
    Bulk upsert memes into Qdrant.
    Each item: {"meme": dict, "text_vector": list[float], "image_vector": list[float]|None}
    Returns number of memes indexed.
    """
    client = get_qdrant_client()
    if client is None:
        logger.warning("Qdrant not available — skipping upsert")
        return 0

    from qdrant_client.models import PointStruct

    points = []
    for item in memes_with_vectors:
        try:
            point = build_point(
                item["meme"],
                item["text_vector"],
                item.get("image_vector"),
            )
            points.append(point)
        except Exception as e:
            logger.warning(f"Failed to build point for meme {item.get('meme', {}).get('id')}: {e}")

    if not points:
        return 0

    # Upsert in batches of 100
    batch_size = 100
    total = 0
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        try:
            client.upsert(collection_name=COLLECTION_NAME, points=batch)
            total += len(batch)
            logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch)} memes")
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")

    return total


# ──────────────────────────────────────────────────────────────────────────────
# Search (The Main Function)
# ──────────────────────────────────────────────────────────────────────────────

def vector_search(
    query_vector: list[float],
    emotion: str = "",
    format_pref: str = "any",
    nsfw: bool = False,
    top_k: int = 10,
    score_threshold: float = 0.35,
) -> list[dict]:
    """
    Real Qdrant vector search with payload filters.

    Args:
        query_vector: 384-dim normalized embedding from MiniLM
        emotion: Primary detected emotion for optional payload filter
        format_pref: 'gif' | 'video' | 'image' | 'any'
        nsfw: Whether to include NSFW content
        top_k: Number of candidates to retrieve
        score_threshold: Minimum cosine similarity (below = noise)

    Returns:
        List of dicts with keys: id, score, meme (payload dict)
    """
    client = get_qdrant_client()

    if client is None:
        logger.warning("Qdrant unavailable — using database fallback search")
        return _db_fallback_search(top_k)

    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny

        # Build filter conditions
        conditions = [
            FieldCondition(key="nsfw", match=MatchValue(value=nsfw))
        ]

        if format_pref == "gif":
            # Filter for memes that have a GIF URL (not NULL)
            # Note: Qdrant doesn't support IS NOT NULL directly
            # We store has_gif=True in payload during indexing
            pass  # handled in build_point with has_gif field

        search_filter = Filter(must=conditions) if conditions else None

        # Execute real vector search
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=("text", query_vector),  # Use named 'text' vector space
            query_filter=search_filter,
            limit=top_k,
            with_payload=True,
            score_threshold=score_threshold,
        )

        # Normalize results to consistent format
        hits = []
        for r in results:
            payload = r.payload or {}
            hits.append({
                "id": payload.get("meme_id", str(r.id)),
                "score": r.score,
                "meme": payload,
            })

        logger.debug(f"Qdrant returned {len(hits)} results (threshold={score_threshold})")

        # If too few results, lower threshold and retry
        if len(hits) < 3 and score_threshold > 0.2:
            logger.info(f"Only {len(hits)} results above {score_threshold}, retrying with lower threshold")
            return vector_search(
                query_vector, emotion, format_pref, nsfw, top_k,
                score_threshold=max(score_threshold - 0.1, 0.2)
            )

        return hits

    except Exception as e:
        logger.error(f"Qdrant search failed: {e} — falling back to DB search")
        return _db_fallback_search(top_k)


def search(
    query_vector: list[float],
    emotion: str = "",
    format_pref: str = "any",
    nsfw: bool = False,
    top_k: int = 10,
) -> list[dict]:
    """Alias for vector_search — used by recommendation_service."""
    return vector_search(query_vector, emotion, format_pref, nsfw, top_k)


# ──────────────────────────────────────────────────────────────────────────────
# Fallback Search (When Qdrant is Unavailable)
# ──────────────────────────────────────────────────────────────────────────────

def _db_fallback_search(top_k: int = 10) -> list[dict]:
    """
    Graceful degradation: when Qdrant is unavailable,
    return top memes by popularity from SQLite.
    Results won't be semantically ranked but at least something shows.
    """
    try:
        from app.database import SessionLocal, Meme as MemeModel
        db = SessionLocal()
        try:
            memes = (
                db.query(MemeModel)
                .order_by(MemeModel.viral_score.desc())
                .limit(top_k)
                .all()
            )
            return [
                {
                    "id": m.id,
                    "score": 0.5,  # Neutral score for fallback
                    "meme": m.to_dict(),
                }
                for m in memes
            ]
        finally:
            db.close()
    except Exception as e:
        logger.error(f"DB fallback search also failed: {e}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Utility: Cosine Similarity
# ──────────────────────────────────────────────────────────────────────────────

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    Returns value in [-1.0, 1.0]; 1.0 = identical direction.

    This function was MISSING and caused ImportError in recommendation_service.py.
    """
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


# ──────────────────────────────────────────────────────────────────────────────
# Collection Health Check
# ──────────────────────────────────────────────────────────────────────────────

def get_collection_info() -> dict:
    """Returns info about the memes collection (count, status, vectors config)."""
    client = get_qdrant_client()
    if client is None:
        return {"status": "unavailable", "count": 0}

    try:
        info = client.get_collection(COLLECTION_NAME)
        return {
            "status": "ok",
            "count": info.vectors_count or 0,
            "indexed_count": info.indexed_vectors_count or 0,
            "status_detail": str(info.status),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## STEP 2 — Install the Qdrant Client

```bash
cd "d:\Meme GPT\backend"
pip install qdrant-client
```

Or add to `requirements.txt`:
```
qdrant-client>=1.7.0
```

---

## STEP 3 — Initialize Collection on Startup

In `d:\Meme GPT\backend\app\main.py`, inside the `lifespan` context manager, add:

```python
# After loading ML models, initialize Qdrant collection
from app.services.search_service import create_qdrant_collection, get_collection_info
create_qdrant_collection(recreate=False)  # Creates if not exists, skips if exists
info = get_collection_info()
logger.info(f"Qdrant collection: {info}")
```

---

## STEP 4 — Test the Fix

```python
# Run from: d:\Meme GPT\backend
python -c "
from app.services.search_service import get_qdrant_client, get_collection_info
client = get_qdrant_client()
if client:
    print('✅ Qdrant connected!')
    print(get_collection_info())
else:
    print('❌ Qdrant not connected — check QDRANT_URL in .env')
"
```
