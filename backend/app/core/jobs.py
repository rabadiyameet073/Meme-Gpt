"""Background Jobs & Structured Logging Module for MemeGPT.
Handles asynchronous task processing (search logging, usage counter updates,
popularity recalculation, cache warming, and analytics aggregation).
"""
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.core.cache import query_cache
from app.database import (
    Feedback,
    Meme,
    MemeUsage,
    SearchLog,
    SessionLocal,
    sanitize_input,
)

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


# `feedback.action` vocabulary accepted by POST /api/v1/feedback → the signal
# names `rerank_service.calculate_popularity_score` consumes.
ACTION_TO_SIGNAL = {
    "view": "views",
    "click": "clicks",
    "copy": "copies",
    "download": "downloads",
    "share": "shares",
    "thumbs_up": "thumbs_up",
    "thumbs_down": "thumbs_down",
}


def _feedback_window_counts(db: Session, window_days: int) -> Dict[str, Dict[str, int]]:
    """Aggregate trailing `feedback` rows per meme into scoring signals."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    counts: Dict[str, Dict[str, int]] = {}
    rows = (
        db.query(Feedback.meme_id, Feedback.action)
        .filter(Feedback.created_at >= cutoff)
        .all()
    )
    for meme_id, action in rows:
        signal = ACTION_TO_SIGNAL.get(action)
        if signal:
            counts.setdefault(meme_id, {}).setdefault(signal, 0)
            counts[meme_id][signal] += 1
    return counts


def recalculate_persisted_popularity(db: Session, window_days: int = 30) -> Dict[str, Any]:
    """Scheduled Job: persist `memes.popularity_score` and `memes.viral_score`.

    Specification: 05_AI_System/Scoring_Logic.md and
    03_Backend/Background_Jobs.md ("Popularity update | Daily 4:00 UTC |
    Recalculate popularity_scores").

    `popularity_score` is the documented weighted engagement formula applied to
    the trailing feedback window; it feeds the composite scorer's popularity
    term and the fallback catalog ordering in `search_service`.

    `viral_score` is derived purely from the stored counters on the seeded
    0-100 scale. The previous implementation read `meme.viral_score` back into
    its own formula, so every run tripled the value — after a week of scheduled
    runs the column overflowed into nonsense. Nothing here reads its own output,
    so repeated runs converge on a fixed point instead of compounding.
    """
    from app.services.rerank_service import calculate_popularity_score

    recent = _feedback_window_counts(db, window_days)
    memes = db.query(Meme).all()

    updated = 0
    with_recent = 0
    for meme in memes:
        signals = dict(recent.get(meme.id) or {})
        if signals:
            with_recent += 1
        else:
            # No feedback inside the window — fall back to the cumulative
            # counters already recorded on the row rather than inventing data.
            signals = {
                "views": meme.view_count or 0,
                "downloads": meme.download_count or 0,
                "copies": meme.usage_count or 0,
                "thumbs_up": meme.upvotes or 0,
                "thumbs_down": meme.downvotes or 0,
            }

        popularity = calculate_popularity_score(signals)
        velocity = round(max(0.0, (
            (meme.upvotes or 0) * 2.0
            - (meme.downvotes or 0) * 1.5
            + (meme.usage_count or 0) * 0.5
            + (meme.view_count or 0) * 0.1
            + (meme.download_count or 0) * 2.0
        )), 2)

        if (
            abs((meme.popularity_score or 0.0) - popularity) > 1e-6
            or abs((meme.viral_score or 0.0) - velocity) > 1e-6
        ):
            updated += 1
        meme.popularity_score = popularity
        meme.viral_score = velocity

    db.commit()
    logger.info(
        f"popularity_recalculated: total_memes={len(memes)} updated={updated} "
        f"with_recent_feedback={with_recent} window_days={window_days}"
    )
    return {
        "status": "success",
        "total_memes": len(memes),
        "updated_memes": updated,
        "with_recent_feedback": with_recent,
        "window_days": window_days,
    }


def recalculate_popularity_scores(
    db: Optional[Session] = None,
    window_days: int = 30,
) -> Dict[str, Any]:
    """Scheduled Job: Recalculates popularity scores from the trailing feedback window."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        return recalculate_persisted_popularity(db, window_days=window_days)
    except Exception as e:
        logger.error(f"popularity_recalculation_error: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        if close_db:
            db.close()


def warm_up_cache_task(queries: Optional[List[str]] = None) -> Dict[str, Any]:
    """Scheduled / Maintenance Job: Pre-caches the documented top queries.

    Writes into the `search:{md5}` keyspace that `recommendation_service`
    actually reads via `make_cache_key`. The previous implementation wrote
    `rec:{query}:gif`, a namespace no code path ever looked up, so the job
    reported success while warming entries that could never be hit.

    `search_logs` stores only an irreversible query hash (GDPR), so the warm set
    cannot be recovered from history. It comes from the suggestion-chip corpus
    the UI really offers, which is what users type first.
    """
    from app.core.cache import make_cache_key
    from app.meme_matcher import match_memes
    from app.services.suggestion_chips_service import (
        get_dynamic_time_based_chips,
        get_static_suggestion_chips,
    )

    if queries:
        warm_queries = [q for q in dict.fromkeys(queries) if q]
    else:
        chips = get_dynamic_time_based_chips() + get_static_suggestion_chips()
        warm_queries = [q for q in dict.fromkeys(c.get("query") for c in chips) if q]

    db = SessionLocal()
    warmed = 0
    try:
        memes = [m.to_dict() for m in db.query(Meme).limit(50).all()]
        if not memes:
            logger.warning("cache_warmup_skipped: no memes indexed")
            return {"status": "skipped", "warmed_queries": 0, "reason": "no memes"}

        for raw_query in warm_queries:
            clean_q = sanitize_input(raw_query)
            if not clean_q:
                continue
            res = match_memes(clean_q, memes, format_preference="gif")
            res["cached"] = True
            query_cache.set(make_cache_key(clean_q, "gif", False), res, ttl=3600)
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
