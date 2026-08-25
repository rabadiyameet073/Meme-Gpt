import hashlib
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Meme, MemeUsage, SearchLog, SessionLocal, get_db, is_valid_input, sanitize_input
from app.models.search import SearchRequest, AnalyzeRequest
from app.meme_matcher import match_memes

logger = logging.getLogger("memegpt.api.search")
router = APIRouter(tags=["Search & Recommendations"])


def _memes_from_db(db: Session) -> list[dict]:
    memes = db.query(Meme).all()
    return [
        {
            **m.to_dict(),
            "videoRef": m.video_ref,
            "gifRef": m.gif_ref,
        }
        for m in memes
    ]


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


@router.post("/search", summary="AI-powered natural language meme search")
async def search_memes_endpoint(
    body: SearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """AI-powered meme recommendation search:
    Cache -> Intent Parsing -> Emotion Detection -> Query Embedding -> Vector Similarity -> Re-ranking
    """
    raw_query = sanitize_input(body.query)
    if not is_valid_input(raw_query) and len(raw_query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query must be between 1 and 2000 characters")

    fmt_pref = body.format_preference or "gif"
    limit = min(max(body.limit, 1), 20)

    categories_filter = body.filters.categories if body.filters else None
    exclude_ids = body.filters.exclude_ids if body.filters else None

    memes = _memes_from_db(db)
    if not memes:
        raise HTTPException(status_code=503, detail="Search service is temporarily unavailable. Database empty.")

    try:
        from app.services.recommendation_service import recommend
        result = await recommend(
            user_text=raw_query,
            format_pref=fmt_pref,
            memes_from_db=memes,
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
    background_tasks.add_task(
        log_search_task,
        query=raw_query,
        match_count=len(search_payload["results"]),
        latency_ms=latency_ms,
        emotion=detected_emotion,
        cached=is_cached,
        session_id=body.session_id or "anonymous",
        primary_meme_id=primary_id,
        confidence=0.85,
    )

    if top_ids:
        background_tasks.add_task(update_usage_counts_task, top_ids)

    return search_payload

