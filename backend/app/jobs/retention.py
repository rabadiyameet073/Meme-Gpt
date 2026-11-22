"""
MemeGPT — Data Retention Job.
Per documentation: Search logs and feedback older than 30 days are deleted.
Run this daily via scheduler or cron.
"""

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("memegpt.retention")

RETENTION_DAYS = 30


def run_retention_cleanup():
    """Delete search logs and feedback older than RETENTION_DAYS.
    Protected by a distributed Redis lock to ensure a single runner across horizontal workers (BE-09).
    """
    from app.core.cache import get_redis_client
    client = get_redis_client()
    if client:
        try:
            lock_acquired = bool(client.set("lock:job:retention_cleanup", "1", nx=True, ex=3600))
            if not lock_acquired:
                logger.info("Retention cleanup skipped: already completed or active on another worker.")
                return {"status": "skipped", "reason": "lock_held"}
        except Exception as e:
            logger.debug(f"Distributed lock error: {e}")

    from app.database import SessionLocal, SearchLog, Feedback

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    db = SessionLocal()
    try:
        deleted_logs = (
            db.query(SearchLog)
            .filter(SearchLog.created_at < cutoff)
            .delete()
        )

        deleted_feedback = (
            db.query(Feedback)
            .filter(Feedback.created_at < cutoff)
            .delete()
        )

        db.commit()
        logger.info(
            f"Retention cleanup: deleted {deleted_logs} logs, "
            f"{deleted_feedback} feedback older than {RETENTION_DAYS} days"
        )
        return {"deleted_logs": deleted_logs, "deleted_feedback": deleted_feedback}

    except Exception as e:
        db.rollback()
        logger.error(f"Retention cleanup failed: {e}")
        return {"error": str(e)}
    finally:
        db.close()
