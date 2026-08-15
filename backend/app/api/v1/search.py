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
            db.add(MemeUsage(meme_id=meme.id, query=query, confidence=confidence, session_id="api-session"))
        db.add(SearchLog(query=query, match_count=match_count, latency_ms=latency_ms, session_id="api-session"))
        db.commit()
    except Exception as e:
        logger.error(f"Error in background search log task: {e}")
        db.rollback()
    finally:
        db.close()


from app.core.jobs import log_search_task, update_usage_counts_task


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
    if not is_valid_input(raw_query):
        raise HTTPException(status_code=400, detail="Query must be 3-2000 characters")

    fmt_pref = body.format_preference or "gif"

    memes = _memes_from_db(db)
    if not memes:
        raise HTTPException(status_code=503, detail="Database empty. Run: python backend/seed.py")

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

    # Structure top results into standard results key if not already present
    if "results" not in result:
        result["results"] = result.get("topFive", [])
    if "query_id" not in result:
        result["query_id"] = hashlib.md5(f"{raw_query}:{fmt_pref}".encode("utf-8")).hexdigest()[:12]
    if "response_time_ms" not in result:
        result["response_time_ms"] = int(result.get("latencyMs", 0))

    primary_id = result.get("primary", {}).get("id") if result.get("primary") else None
    top_ids = [m.get("id") for m in result.get("results", []) if m.get("id")]

    # Enqueue non-blocking background jobs
    background_tasks.add_task(
        log_search_task,
        query=raw_query,
        match_count=len(result.get("results", [])),
        latency_ms=result.get("latencyMs", 0),
        emotion=result.get("detectedEmotion") or result.get("intent", {}).get("primary_emotion"),
        cached=result.get("cached", False),
        session_id=body.session_id or "anonymous",
        primary_meme_id=primary_id,
        confidence=result.get("primary", {}).get("confidence", 0.8),
    )

    if top_ids:
        background_tasks.add_task(update_usage_counts_task, top_ids)

    return result

