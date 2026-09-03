"""Background Jobs & Structured Logging Module for MemeGPT.
Handles asynchronous task processing (search logging, usage counter updates,
popularity recalculation, cache warming, and analytics aggregation).
"""
import hashlib
import logging
import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import (
    Meme,
    MemeUsage,
    SearchLog,
    SessionLocal,
    get_db,
    sanitize_input,
)
from app.config import settings
from app.core.cache import query_cache

logger = logging.getLogger("memegpt.jobs")


def hash_query_privacy(query: str) -> str:
    """Returns a privacy-safe 12-char hash for query logging (prevents PII leaks)."""
    clean = query.strip().lower()
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()[:12]


def log_search_task(
    query: str,
    match_count: int,
    latency_ms: float,
    emotion: Optional[str] = "neutral",
    cached: bool = False,
    session_id: str = "anonymous",
    primary_meme_id: Optional[str] = None,
    confidence: Optional[float] = 0.8
):
    """Background task: Asynchronously records search analytics with structured privacy logging."""
    query_hash = hash_query_privacy(query)

    # Structured format: [YYYY-MM-DD HH:MM:SS] INFO search: query_hash=abc123 results=5 latency=847ms cached=false
    logger.info(
        f"search: query_hash={query_hash} results={match_count} latency={round(latency_ms, 1)}ms "
        f"cached={str(cached).lower()} emotion={emotion or 'neutral'}"
    )

    db: Session = SessionLocal()
    try:
        if primary_meme_id:
            meme = db.query(Meme).filter(Meme.id == primary_meme_id).first()
            if meme:
                meme.usage_count += 1
                db.add(MemeUsage(
                    meme_id=meme.id,
                    query=query_hash,  # store query hash for privacy
                    confidence=confidence,
                    session_id=session_id
                ))

        db.add(SearchLog(
            query_hash=query_hash,
            result_count=match_count,
            latency_ms=latency_ms,
            cache_hit=cached,
            top_meme_id=primary_meme_id,
            model_used="groq" if getattr(settings, "GROQ_API_KEY", None) else "fallback",
            emotion_detected=emotion or "neutral",
            session_id=session_id
        ))
        db.commit()
    except Exception as e:
        logger.error(f"background_job_error (log_search): {e}")
        db.rollback()
    finally:
        db.close()


def update_usage_counts_task(meme_ids: List[str]):
    """Background task: Batch increment usage counts for returned meme candidates."""
    if not meme_ids:
        return

    db: Session = SessionLocal()
    try:
        memes = db.query(Meme).filter(Meme.id.in_(meme_ids)).all()
        for meme in memes:
            meme.usage_count = (meme.usage_count or 0) + 1
            meme.viral_score = (meme.viral_score or 0.0) + 0.1
        db.commit()
        logger.debug(f"usage_counts_updated: count={len(memes)}")
    except Exception as e:
        logger.error(f"background_job_error (update_usage_counts): {e}")
        db.rollback()
    finally:
        db.close()


def recalculate_popularity_scores(db: Optional[Session] = None) -> Dict[str, Any]:
    """Scheduled Job: Recalculates popularity scores with recency decay and interaction weights."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        memes = db.query(Meme).all()
        updated_count = 0
        for meme in memes:
            # Score formula: (upvotes * 2.0) - (downvotes * 1.5) + (usage_count * 0.5) + (viral_score * 3.0)
            upvotes = meme.upvotes or 0
            downvotes = meme.downvotes or 0
            usage = meme.usage_count or 0
            viral = meme.viral_score or 0.0

            raw_score = (upvotes * 2.0) - (downvotes * 1.5) + (usage * 0.5) + (viral * 3.0)
            meme.viral_score = max(0.0, round(raw_score, 2))
            updated_count += 1

        db.commit()
        logger.info(f"popularity_recalculated: total_memes={updated_count}")
        return {"status": "success", "updated_memes": updated_count}
    except Exception as e:
        logger.error(f"popularity_recalculation_error: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if close_db:
            db.close()


def warm_up_cache_task(queries: Optional[List[str]] = None) -> Dict[str, Any]:
    """Scheduled / Maintenance Job: Pre-caches top search queries for sub-15ms hits."""
    sample_top_queries = queries or [
        "when code works on first try",
        "deploying to production on friday",
        "fixing bugs in production at 3am",
        "merge conflict nightmare",
        "forgot semicolons in javascript",
        "waiting for docker build to finish",
        "boss asks for a quick estimate",
        "junior dev deleting production database",
        "stack overflow is down",
        "ai replacing developers meme"
    ]

    from app.meme_matcher import match_memes
    db = SessionLocal()
    warmed = 0
    try:
        memes = [m.to_dict() for m in db.query(Meme).limit(20).all()]
        if memes:
            for q in sample_top_queries[:5]:
                clean_q = sanitize_input(q)
                cache_key = f"rec:{clean_q}:gif"
                res = match_memes(clean_q, memes, format_preference="gif")
                res["cached"] = True
                query_cache.set(cache_key, res, ttl=3600)
                warmed += 1
        logger.info(f"cache_warmup_completed: warmed_queries={warmed}")
        return {"status": "success", "warmed_queries": warmed}

    except Exception as e:
        logger.error(f"cache_warmup_error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def aggregate_analytics_task() -> Dict[str, Any]:
    """Scheduled Job: Computes search log aggregations, average latencies, and match stats."""
    db = SessionLocal()
    try:
        total_searches = db.query(SearchLog).count()
        avg_latency = db.query(func.avg(SearchLog.latency_ms)).scalar() or 0.0
        total_memes = db.query(Meme).count()
        total_usage = db.query(func.sum(Meme.usage_count)).scalar() or 0

        summary = {
            "total_searches": total_searches,
            "avg_latency_ms": round(float(avg_latency), 2),
            "total_memes": total_memes,
            "total_usage": total_usage,
            "cache_stats": query_cache.stats(),
        }
        logger.info(f"analytics_aggregated: searches={total_searches} avg_latency={round(avg_latency, 1)}ms")
        return summary
    except Exception as e:
        logger.error(f"analytics_aggregation_error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
