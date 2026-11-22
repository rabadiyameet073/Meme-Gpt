import hashlib
import logging
import time
import tempfile
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import Meme, MemeUsage, SearchLog, SessionLocal, get_db, is_valid_input, sanitize_input
from app.models.search import SearchRequest, AnalyzeRequest, SearchResponse
from app.meme_matcher import match_memes
from app.core.rate_limit import require_route_rate_limit

logger = logging.getLogger("memegpt.api.search")
router = APIRouter(tags=["Search & Recommendations"])

_MEMES_CACHE: Optional[List[Dict[str, Any]]] = None
_MEMES_CACHE_EXPIRES: float = 0.0


def invalidate_memes_cache():
    """Invalidate cached meme list on data mutations."""
    global _MEMES_CACHE, _MEMES_CACHE_EXPIRES
    _MEMES_CACHE = None
    _MEMES_CACHE_EXPIRES = 0.0


def _get_cached_memes(db: Optional[Session] = None) -> list[dict]:
    """
    Returns active meme objects from cache or database.
    Caches results with a 5-minute TTL to avoid loading the entire database on every search request (BE-08).
    """
    global _MEMES_CACHE, _MEMES_CACHE_EXPIRES
    now = time.time()
    if _MEMES_CACHE is not None and now < _MEMES_CACHE_EXPIRES:
        return _MEMES_CACHE

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        memes = db.query(Meme).filter(
            Meme.moderation_status != "removed"
        ).all()
        _MEMES_CACHE = [
            {
                **m.to_dict(),
                "videoRef": m.video_ref,
                "gifRef": m.gif_ref,
            }
            for m in memes
        ]
        _MEMES_CACHE_EXPIRES = now + 300.0  # 5 minutes TTL
        return _MEMES_CACHE
    finally:
        if close_db:
            db.close()


def _memes_from_db(db: Session) -> list[dict]:
    return _get_cached_memes(db)


def _log_search_background(primary_meme_id: str, query: str, match_count: int, confidence: float, latency_ms: float):
    """Background task for async search analytics logging with privacy hash."""
    db = SessionLocal()
    try:
        query_hash = hashlib.md5(query.encode("utf-8")).hexdigest()
        logger.info(f"Logging search (hash: {query_hash[:8]}, latency: {latency_ms}ms)")
        meme = db.query(Meme).filter(Meme.id == primary_meme_id).first()
        if meme:
            meme.usage_count += 1
            db.add(MemeUsage(meme_id=meme.id, query=query_hash, confidence=confidence, session_id="api-session"))
        db.add(SearchLog(
            query_hash=query_hash,
            result_count=match_count,
            latency_ms=latency_ms,
            top_meme_id=primary_meme_id,
            cache_hit=False,
            session_id="api-session"
        ))
        db.commit()
    except Exception as e:
        logger.error(f"Error in background search log task: {e}")
        db.rollback()
    finally:
        db.close()


from app.core.jobs import log_search_task, update_usage_counts_task
from app.services.search_service import build_search_response_payload


@router.post(
    "/search",
    summary="AI-powered natural language meme search",
    response_model=SearchResponse,
    dependencies=[Depends(require_route_rate_limit("search"))],
)
async def search_memes_endpoint(
    body: SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """AI-powered meme recommendation search:
    Cache -> Intent Parsing -> Emotion Detection -> Query Embedding -> Vector Similarity -> Re-ranking
    """
    raw_query = sanitize_input(body.query)
    if not is_valid_input(raw_query) or len(raw_query.strip()) == 0:
        raise HTTPException(status_code=422, detail="Query must be between 1 and 2000 characters")

    fmt_pref = body.format_preference or "gif"
    limit = min(max(body.limit, 1), 20)

    categories_filter = body.filters.categories if body.filters else None
    exclude_ids = body.filters.exclude_ids if body.filters else None

    memes = _memes_from_db(db)
    if not memes:
        return {
            "success": True,
            "query_id": f"q_{hashlib.md5(f'{raw_query}:{fmt_pref}'.encode('utf-8')).hexdigest()[:8]}",
            "results": [],
            "reason": "database_empty",
            "message": "Search service is operational, but database contains no memes.",
            "data": {
                "query": raw_query,
                "matches": [],
                "count": 0,
            },
        }

    try:
        from app.services.recommendation_service import recommend
        result = await recommend(
            user_text=raw_query,
            format_pref=fmt_pref,
            nsfw=getattr(body, "nsfw", False),
            session_id=body.session_id,
            memes_from_db=memes,
            limit=limit,
            categories=categories_filter,
            exclude_ids=exclude_ids,
        )
    except Exception as e:
        logger.error(f"AI recommendation pipeline failed, falling back to rule engine: {e}")
        result = match_memes(raw_query, memes, format_preference=fmt_pref)
        result["cached"] = False

    query_id = result.get("query_id") or f"q_{hashlib.md5(f'{raw_query}:{fmt_pref}'.encode('utf-8')).hexdigest()[:8]}"
    detected_emotion = result.get("detectedEmotion") or result.get("intent", {}).get("primary_emotion") or "relatable"
    latency_ms = int(result.get("latencyMs", result.get("response_time_ms", 0)))
    is_cached = result.get("cached", False)

    raw_candidates = result.get("results") or result.get("topFive") or ([result["primary"]] if result.get("primary") else memes[:5])

    # Assemble response matching 07_APIs/Search_API.md
    search_payload = build_search_response_payload(
        query_id=query_id,
        raw_results=raw_candidates,
        query_text=raw_query,
        limit=limit,
        categories_filter=categories_filter,
        exclude_ids=exclude_ids,
        detected_emotion=detected_emotion,
        response_time_ms=latency_ms,
        cached=is_cached,
    )

    # Attach backwards compatibility keys if present
    if "primary" in result:
        search_payload["primary"] = result["primary"]
    if "topFive" in result:
        search_payload["topFive"] = result["topFive"]

    primary_id = search_payload["results"][0]["id"] if search_payload["results"] else None
    top_ids = [m["id"] for m in search_payload["results"] if m.get("id")]

    # Enqueue non-blocking background jobs
    top_score = search_payload["results"][0].get("score", 0.85) if search_payload.get("results") else 0.85
    background_tasks.add_task(
        log_search_task,
        query=raw_query,
        match_count=len(search_payload["results"]),
        latency_ms=latency_ms,
        emotion=detected_emotion,
        cached=is_cached,
        session_id=body.session_id or "anonymous",
        primary_meme_id=primary_id,
        confidence=top_score,
    )

    if top_ids:
        background_tasks.add_task(update_usage_counts_task, top_ids)

    return search_payload


@router.post(
    "/search/image",
    summary="Reverse image search / visual meme recommendation",
    dependencies=[Depends(require_route_rate_limit("search"))],
)
async def search_by_image(
    file: UploadFile = File(...),
    limit: int = 5,
    nsfw: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Search memes by uploading an image (reverse-image search / CLIP visual matching - API-13).
    Extracts visual embedding via CLIP ViT-B/32 and queries Qdrant 'image' named vectors.
    """
    limit = min(max(limit, 1), 20)
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image file uploaded")

    temp_dir = Path(tempfile.gettempdir()) / "memegpt_uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / f"search_{uuid.uuid4().hex[:8]}_{file.filename or 'upload.jpg'}"
    temp_file.write_bytes(contents)

    start_time = time.perf_counter()
    query_id = f"q_img_{uuid.uuid4().hex[:8]}"

    try:
        from app.services.image_analysis_service import embed_image, generate_caption
        img_vector = embed_image(str(temp_file))
        caption = generate_caption(str(temp_file)) or file.filename or "uploaded image"

        from app.services import search_service
        candidates = search_service.vector_search(
            query_vector=img_vector,
            vector_name="image",
            top_k=max(15, limit * 3),
            nsfw=nsfw,
            query_text=caption,
        )

        memes = _get_cached_memes(db)
        if memes and candidates:
            db_lookup = {m["id"]: m for m in memes}
            for c in candidates:
                if not c.get("meme") or not c["meme"].get("name"):
                    db_m = db_lookup.get(c.get("id"))
                    if db_m:
                        c["meme"] = db_m

        if not candidates:
            candidates = search_service._db_fallback_search(limit)

        latency_ms = max(int((time.perf_counter() - start_time) * 1000), 1)

        payload = build_search_response_payload(
            query_id=query_id,
            raw_results=candidates,
            query_text=caption,
            limit=limit,
            detected_emotion="visual_match",
            response_time_ms=latency_ms,
            cached=False,
        )
        return payload
    except Exception as e:
        logger.error(f"Image search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image search processing error: {e}")
    finally:
        try:
            if temp_file.exists():
                temp_file.unlink()
        except Exception:
            pass

