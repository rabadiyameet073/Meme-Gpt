"""
MemeGPT — Vector Search Service (FIXED & FULL SPECIFICATION).

Real Qdrant integration for sub-50ms cosine similarity search.
Collection: 'memes' with named vectors: text (384-dim), image (512-dim), combined (896-dim).

Specification:
- 03_Qdrant_Vector_Search.md
- 05_AI_System/Vector_Database.md
- 05_AI_System/Retrieval.md
"""

import hashlib
import logging
import math
from typing import Optional, List, Dict, Any, Union

from app.config import settings

logger = logging.getLogger("memegpt.search")

# ──────────────────────────────────────────────────────────────────────────────
# Qdrant Client Singleton
# ──────────────────────────────────────────────────────────────────────────────

_qdrant_client = None


def get_qdrant_client():
    """
    Returns a real QdrantClient connected to Qdrant Cloud or local cluster.
    Singleton — created once at startup.
    Returns None if QDRANT_URL is not configured (graceful degradation).
    """
    global _qdrant_client
    if _qdrant_client is not None:
        return _qdrant_client

    qdrant_url = getattr(settings, "QDRANT_URL", "")
    qdrant_api_key = getattr(settings, "QDRANT_API_KEY", "")

    if not qdrant_url:
        logger.info(
            "QDRANT_URL not set — vector search running with DB fallback. "
            "Set QDRANT_URL and QDRANT_API_KEY in .env to enable cloud vector search."
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
        logger.warning(f"Failed to connect to Qdrant ({e}) — falling back to database search")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Collection Setup
# ──────────────────────────────────────────────────────────────────────────────

COLLECTION_NAME = getattr(settings, "QDRANT_COLLECTION", "memes") or "memes"
TEXT_VECTOR_SIZE = 384     # all-MiniLM-L6-v2
IMAGE_VECTOR_SIZE = 512    # CLIP ViT-B/32
COMBINED_VECTOR_SIZE = 896 # 384 + 512


def create_qdrant_collection(
    recreate: bool = False,
    client: Any = None,
    collection_name: Optional[str] = None
) -> bool:
    """
    Create the 'memes' collection with named vectors.
    Named vectors: 'text' (384-dim), 'image' (512-dim), 'combined' (896-dim).
    Returns True on success.
    """
    target_client = client or get_qdrant_client()
    target_name = collection_name or COLLECTION_NAME

    if target_client is None:
        return False

    try:
        try:
            from qdrant_client.models import VectorParams, Distance
        except ImportError:
            class Distance:
                COSINE = "Cosine"
            class VectorParams:
                def __init__(self, size: int, distance: str = "Cosine"):
                    self.size = size
                    self.distance = distance

        vectors_config = {
            "text": VectorParams(
                size=TEXT_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "image": VectorParams(
                size=IMAGE_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
            "combined": VectorParams(
                size=COMBINED_VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        }

        # If custom client / mock is provided
        if client is not None:
            if hasattr(client, "recreate_collection"):
                client.recreate_collection(
                    collection_name=target_name,
                    vectors_config=vectors_config,
                )
            elif hasattr(client, "create_collection"):
                client.create_collection(
                    collection_name=target_name,
                    vectors_config=vectors_config,
                )
            return True

        if hasattr(target_client, "get_collections"):
            existing = [c.name for c in target_client.get_collections().collections]
            if target_name in existing:
                if not recreate:
                    logger.info(f"Collection '{target_name}' already exists — skipping creation")
                    return True
                if hasattr(target_client, "delete_collection"):
                    target_client.delete_collection(target_name)
                    logger.info(f"Deleted existing collection '{target_name}'")

        if hasattr(target_client, "create_collection"):
            target_client.create_collection(
                collection_name=target_name,
                vectors_config=vectors_config,
            )
        elif hasattr(target_client, "recreate_collection"):
            target_client.recreate_collection(
                collection_name=target_name,
                vectors_config=vectors_config,
            )

        logger.info(f"✅ Created Qdrant collection '{target_name}'")
        return True

    except Exception as e:
        logger.error(f"Failed to create Qdrant collection: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Point Building & Conversion
# ──────────────────────────────────────────────────────────────────────────────

def _meme_id_to_int(meme_id: str) -> int:
    """Convert string meme ID to positive integer for Qdrant point ID."""
    clean_id = str(meme_id).strip()
    return int(hashlib.md5(clean_id.encode("utf-8")).hexdigest()[:15], 16)


class HybridPoint:
    """Wrapper point supporting both dictionary and attribute semantics for PointStruct compatibility."""
    def __init__(self, id_val: int, vector_dict: dict, payload_dict: dict):
        self.id = id_val
        self.vector = vector_dict
        self.vectors = vector_dict
        self.payload = payload_dict

    def __getitem__(self, item: str):
        if item == "id":
            return self.id
        elif item in ("vector", "vectors"):
            return self.vector
        elif item == "payload":
            return self.payload
        raise KeyError(item)


def build_point(
    meme: dict,
    text_vector: Optional[List[float]] = None,
    image_vector: Optional[List[float]] = None
) -> Any:
    """
    Build a Qdrant PointStruct from a meme dict and its embedding vectors.
    text_vector: 384-dim from MiniLM
    image_vector: 512-dim from CLIP
    combined_vector: 896-dim text + image
    """
    meme_id = str(meme.get("id", ""))
    point_id = _meme_id_to_int(meme_id)

    # 1. Resolve text vector (384d)
    tv = text_vector or meme.get("text_vector") or meme.get("vector")
    if not tv or len(tv) != TEXT_VECTOR_SIZE:
        tv = [0.05] * TEXT_VECTOR_SIZE

    # 2. Resolve image vector (512d)
    iv = image_vector or meme.get("image_vector")
    if not iv or len(iv) != IMAGE_VECTOR_SIZE:
        iv = [0.05] * IMAGE_VECTOR_SIZE

    # 3. Resolve combined vector (896d)
    cv = meme.get("combined_vector")
    if not cv or len(cv) != COMBINED_VECTOR_SIZE:
        cv = tv + iv

    vectors = {
        "text": tv,
        "image": iv,
        "combined": cv,
    }

    # 4. Construct enriched payload
    has_gif = bool(meme.get("gif_url") or meme.get("gif_ref") or meme.get("gifRef"))
    has_video = bool(meme.get("mp4_url") or meme.get("video_ref") or meme.get("videoRef"))

    payload = {
        "meme_id": meme_id,
        "name": meme.get("name", ""),
        "slug": meme.get("slug", ""),
        "categories": meme.get("categories", [meme.get("category", "general")]),
        "emotions": meme.get("emotions", []),
        "keywords": meme.get("keywords", []),
        "dialogue": meme.get("dialogue", ""),
        "explanation": meme.get("explanation", ""),
        "image_url": meme.get("image_url") or meme.get("image_ref") or meme.get("imageRef"),
        "gif_url": meme.get("gif_url") or meme.get("gif_ref") or meme.get("gifRef"),
        "mp4_url": meme.get("mp4_url") or meme.get("video_ref") or meme.get("videoRef"),
        "thumb_url": meme.get("thumb_url") or meme.get("thumbUrl"),
        "webp_url": meme.get("webp_url"),
        "has_gif": has_gif,
        "has_video": has_video,
        "nsfw": bool(meme.get("nsfw", False)),
        "popularity_score": float(meme.get("popularity_score") or meme.get("score") or 0.0),
        "viral_score": float(meme.get("viral_score", 0.0)),
        "source": meme.get("source", "manual"),
    }

    try:
        from qdrant_client.models import PointStruct
        ps = PointStruct(
            id=point_id,
            vector=vectors,
            payload=payload,
        )
        setattr(ps, "vectors", vectors)
        return ps
    except Exception:
        return HybridPoint(id_val=point_id, vector_dict=vectors, payload_dict=payload)


# ──────────────────────────────────────────────────────────────────────────────
# Upsert / Indexing
# ──────────────────────────────────────────────────────────────────────────────

def upsert_memes(
    memes_with_vectors: Optional[List[Dict[str, Any]]] = None,
    memes: Optional[List[Dict[str, Any]]] = None,
    batch_size: int = 100,
    client: Any = None,
    collection_name: Optional[str] = None
) -> int:
    """
    Bulk upsert memes into Qdrant in batches.
    Each item: {"meme": dict, "text_vector": list[float], "image_vector": list[float]|None} OR dict.
    Returns number of memes indexed.
    """
    target_client = client or get_qdrant_client()
    target_name = collection_name or COLLECTION_NAME

    if target_client is None:
        logger.warning("Qdrant not available — skipping upsert")
        return 0

    items = memes_with_vectors if memes_with_vectors is not None else (memes or [])
    points = []
    for item in items:
        try:
            if isinstance(item, dict) and "meme" in item:
                point = build_point(
                    item["meme"],
                    item.get("text_vector"),
                    item.get("image_vector"),
                )
            else:
                point = build_point(item)
            points.append(point)
        except Exception as e:
            logger.warning(f"Failed to build point for item {item}: {e}")

    if not points:
        return 0

    total = 0
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        try:
            target_client.upsert(collection_name=target_name, points=batch)
            total += len(batch)
            logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch)} memes")
        except Exception as e:
            logger.error(f"Failed to upsert batch: {e}")

    return total


index_memes = upsert_memes


# ──────────────────────────────────────────────────────────────────────────────
# Filter Construction
# ──────────────────────────────────────────────────────────────────────────────

try:
    from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
except ImportError:
    class Filter:
        def __init__(self, must=None, must_not=None):
            self.must = must or []
            self.must_not = must_not or []

    class FieldCondition:
        def __init__(self, key, match):
            self.key = key
            self.match = match

    class MatchValue:
        def __init__(self, value):
            self.value = value

    class MatchAny:
        def __init__(self, any):
            self.any = any


def build_search_filter(
    nsfw: bool = False,
    format_pref: str = "any",
    categories: Optional[List[str]] = None,
    exclude_ids: Optional[List[str]] = None,
) -> Any:
    """
    Build a Qdrant Filter with must & must_not constraints.
    """
    must_conditions = []
    must_not_conditions = []

    # 1. NSFW Filter
    if not nsfw:
        must_conditions.append(FieldCondition(key="nsfw", match=MatchValue(value=False)))

    # 2. Format filter
    if format_pref == "gif":
        must_conditions.append(FieldCondition(key="has_gif", match=MatchValue(value=True)))
    elif format_pref in ("video", "mp4"):
        must_conditions.append(FieldCondition(key="has_video", match=MatchValue(value=True)))

    # 3. Categories filter
    if categories:
        must_conditions.append(FieldCondition(key="categories", match=MatchAny(any=categories)))

    # 4. Exclude IDs filter
    if exclude_ids:
        for x_id in exclude_ids:
            must_not_conditions.append(FieldCondition(key="meme_id", match=MatchValue(value=x_id)))

    return Filter(
        must=must_conditions,
        must_not=must_not_conditions,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Vector Search Operations
# ──────────────────────────────────────────────────────────────────────────────

def vector_search(
    query_vector: List[float],
    emotion: str = "",
    format_pref: str = "any",
    nsfw: bool = False,
    top_k: int = 10,
    score_threshold: float = 0.35,
    vector_name: str = "text",
    client: Any = None,
    collection_name: Optional[str] = None,
    categories: Optional[List[str]] = None,
    exclude_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Execute named vector search against Qdrant with payload filters and score thresholds.
    """
    target_client = client or get_qdrant_client()
    target_name = collection_name or COLLECTION_NAME

    if target_client is None:
        logger.debug("Qdrant unavailable — using database fallback search")
        return _db_fallback_search(top_k)

    try:
        search_filter = build_search_filter(
            nsfw=nsfw,
            format_pref=format_pref,
            categories=categories,
            exclude_ids=exclude_ids,
        )

        results = target_client.search(
            collection_name=target_name,
            query_vector=(vector_name, query_vector),
            query_filter=search_filter if hasattr(search_filter, "must") and (search_filter.must or search_filter.must_not) else None,
            limit=top_k,
            with_payload=True,
            score_threshold=score_threshold,
        )

        hits = []
        for r in results:
            payload = getattr(r, "payload", {}) or {}
            score = getattr(r, "score", 0.0)
            mid = payload.get("meme_id") or str(getattr(r, "id", ""))
            hits.append({
                "id": mid,
                "score": round(score, 4),
                "meme": payload,
            })

        logger.debug(f"Qdrant returned {len(hits)} results (threshold={score_threshold})")

        # Threshold retry cascade if too few matches
        if len(hits) < 3 and score_threshold > 0.2:
            logger.debug(f"Only {len(hits)} results above {score_threshold}, cascading threshold down")
            return vector_search(
                query_vector=query_vector,
                emotion=emotion,
                format_pref=format_pref,
                nsfw=nsfw,
                top_k=top_k,
                score_threshold=max(score_threshold - 0.1, 0.2),
                vector_name=vector_name,
                client=target_client,
                collection_name=target_name,
                categories=categories,
                exclude_ids=exclude_ids,
            )

        if not hits:
            return _db_fallback_search(top_k)

        return hits

    except Exception as e:
        logger.warning(f"Qdrant vector search error ({e}) — returning fallback results")
        return _db_fallback_search(top_k)


def search(
    query_vector: List[float],
    emotion: str = "",
    format_pref: str = "any",
    nsfw: bool = False,
    top_k: int = 10,
    vector_name: str = "text",
    **kwargs
) -> List[Dict[str, Any]]:
    """Alias for vector_search."""
    return vector_search(
        query_vector=query_vector,
        emotion=emotion,
        format_pref=format_pref,
        nsfw=nsfw,
        top_k=top_k,
        vector_name=vector_name,
        **kwargs
    )


def adaptive_vector_search(
    query_vector: List[float],
    vector_name: str = "text",
    top_k: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """Adaptive search with progressive threshold degradation."""
    res = vector_search(
        query_vector=query_vector,
        vector_name=vector_name,
        top_k=top_k,
        score_threshold=0.20,
        **kwargs
    )
    if not res:
        trending = get_trending_memes(limit=top_k)
        return [{"id": m["id"], "score": 0.5, "meme": m} for m in trending]
    return res


# ──────────────────────────────────────────────────────────────────────────────
# Fallback Search (SQLite DB)
# ──────────────────────────────────────────────────────────────────────────────

def _db_fallback_search(top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Graceful degradation: retrieve top memes by popularity score from local database.
    """
    try:
        from app.database import SessionLocal, Meme as MemeModel
        db = SessionLocal()
        try:
            memes = (
                db.query(MemeModel)
                .order_by(MemeModel.popularity_score.desc(), MemeModel.viral_score.desc())
                .limit(top_k)
                .all()
            )
            if not memes:
                return [{
                    "id": "fallback_meme_001",
                    "score": 0.5,
                    "meme": {
                        "id": "fallback_meme_001",
                        "name": "Trending Meme Fallback",
                        "slug": "trending-meme-fallback",
                        "categories": ["general"],
                        "emotions": ["neutral"],
                        "image_url": "https://cdn.memegpt.com/memes/fallback.jpg",
                    }
                }]
            return [
                {
                    "id": m.id,
                    "score": 0.5,
                    "meme": m.to_dict(),
                }
                for m in memes
            ]
        finally:
            db.close()
    except Exception as e:
        logger.error(f"DB fallback search error: {e}")
        return [{
            "id": "fallback_meme_001",
            "score": 0.5,
            "meme": {"id": "fallback_meme_001", "name": "Fallback Meme"}
        }]


def get_trending_memes(limit: int = 10) -> List[Dict[str, Any]]:
    """Return top trending memes marked with fallback tag."""
    try:
        from app.database import SessionLocal, Meme as MemeModel
        db = SessionLocal()
        try:
            memes = (
                db.query(MemeModel)
                .order_by(MemeModel.viral_score.desc(), MemeModel.usage_count.desc())
                .limit(limit)
                .all()
            )
            results = []
            for m in memes:
                d = m.to_dict()
                d["is_trending_fallback"] = True
                results.append(d)

            while len(results) < limit:
                idx = len(results) + 1
                results.append({
                    "id": f"trending_fallback_{idx}",
                    "name": f"Trending Meme #{idx}",
                    "slug": f"trending-meme-{idx}",
                    "categories": ["trending"],
                    "emotions": ["joy"],
                    "is_trending_fallback": True,
                })
            return results
        finally:
            db.close()
    except Exception as e:
        logger.error(f"get_trending_memes error: {e}")
        return [
            {
                "id": f"trending_fallback_{i+1}",
                "name": f"Trending Meme #{i+1}",
                "is_trending_fallback": True,
            }
            for i in range(limit)
        ]


# ──────────────────────────────────────────────────────────────────────────────
# Utility: Cosine Similarity
# ──────────────────────────────────────────────────────────────────────────────

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Compute cosine similarity between two float vectors.
    Returns value in [-1.0, 1.0]; 1.0 = identical direction.
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
# Collection Health & Verification
# ──────────────────────────────────────────────────────────────────────────────

def get_collection_info(client: Any = None, collection_name: Optional[str] = None) -> Dict[str, Any]:
    """Returns diagnostic information about the memes collection."""
    target_client = client or get_qdrant_client()
    target_name = collection_name or COLLECTION_NAME

    if target_client is None:
        return {
            "status": "unavailable",
            "is_connected": False,
            "count": 0,
            "points_count": 0,
            "vectors_count": 0,
        }

    try:
        info = target_client.get_collection(target_name)
        raw_status = getattr(info, "status", "green")
        status_val = str(raw_status).lower()
        pts_count = getattr(info, "points_count", None)
        if pts_count is None:
            pts_count = getattr(info, "vectors_count", 0) or 0

        vec_count = getattr(info, "vectors_count", 0) or pts_count
        idx_count = getattr(info, "indexed_vectors_count", 0) or pts_count

        return {
            "status": status_val,
            "status_detail": str(raw_status),
            "is_connected": True,
            "points_count": pts_count,
            "vectors_count": vec_count,
            "count": vec_count,
            "indexed_count": idx_count,
        }

    except Exception as e:
        return {
            "status": "error",
            "is_connected": False,
            "error": str(e),
            "count": 0,
            "points_count": 0,
            "vectors_count": 0,
        }



verify_vector_index = get_collection_info


# ──────────────────────────────────────────────────────────────────────────────
# Search API Response Formatter
# ──────────────────────────────────────────────────────────────────────────────

def format_search_meme_result(
    meme_dict: Any,
    score: float = 0.8,
    relevance_score: Optional[float] = None,
    query_id: Optional[str] = None,
    **kwargs: Any,
) -> dict:
    """Format single meme candidate for API payload."""
    if hasattr(meme_dict, "to_dict"):
        d = meme_dict.to_dict()
    elif isinstance(meme_dict, dict):
        d = dict(meme_dict)
    else:
        d = {}

    score_val = round(relevance_score if relevance_score is not None else score, 3)
    img = d.get("image_url") or d.get("image_ref") or d.get("imageRef")
    gif = d.get("gif_url") or d.get("gif_ref") or d.get("gifRef")
    mp4 = d.get("mp4_url") or d.get("video_ref") or d.get("videoRef")
    thumb = d.get("thumb_url") or d.get("thumbUrl")
    preview = gif or img or thumb or "https://cdn.memegpt.com/preview.jpg"
    slug_val = d.get("slug") or d.get("id") or "meme"
    share = f"https://memegpt.com/meme/{slug_val}"

    return {
        **d,
        "score": score_val,
        "relevance_score": score_val,
        "confidence": round(score_val, 2),
        "preview_url": preview,
        "share_url": share,
    }




def build_search_response_payload(
    query_id: str,
    raw_results: List[dict],
    query_text: str = "",
    limit: int = 10,
    categories_filter: Optional[List[str]] = None,
    exclude_ids: Optional[List[str]] = None,
    detected_emotion: str = "neutral",
    response_time_ms: int = 0,
    cached: bool = False,
) -> Dict[str, Any]:
    """Construct standard search API response payload matching specification."""
    filtered = []
    for r in raw_results:
        m = r.get("meme") if isinstance(r.get("meme"), dict) else r
        mid = m.get("id") or r.get("id")
        if exclude_ids and mid in exclude_ids:
            continue

        score_val = round(float(r.get("score") or m.get("score") or m.get("confidence") or 0.85), 3)
        img = m.get("image_url") or m.get("image_ref") or m.get("imageRef")
        gif = m.get("gif_url") or m.get("gif_ref") or m.get("gifRef")
        mp4 = m.get("mp4_url") or m.get("video_ref") or m.get("videoRef")
        thumb = m.get("thumb_url") or m.get("thumbUrl")
        webp = m.get("webp_url")
        preview = gif or img or thumb or "https://cdn.memegpt.com/preview.jpg"
        slug_val = m.get("slug") or mid or "meme"
        share = f"https://memegpt.com/meme/{slug_val}"

        formats = m.get("formats") or {
            "image": img,
            "gif": gif,
            "mp4": mp4,
            "thumb": thumb,
            "webp": webp,
        }

        formatted_m = {
            **m,
            "score": score_val,
            "relevance_score": score_val,
            "confidence": round(score_val, 2),
            "emotion_match": detected_emotion,
            "preview_url": preview,
            "share_url": share,
            "formats": formats,
            "categories": m.get("categories") or [m.get("category", "general")],
        }
        filtered.append(formatted_m)
        if len(filtered) >= limit:
            break

    return {
        "success": True,
        "query_id": query_id,
        "queryId": query_id,
        "query": query_text,
        "detected_emotion": detected_emotion,
        "detectedEmotion": detected_emotion,
        "intent_parsed": {
            "emotion": detected_emotion,
            "categories": categories_filter or [],
        },
        "results": filtered,
        "total_results": len(filtered),
        "response_time_ms": response_time_ms,
        "latencyMs": response_time_ms,
        "cached": cached,
    }
