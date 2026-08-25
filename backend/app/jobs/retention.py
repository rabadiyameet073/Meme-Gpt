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
    """Delete search logs and feedback older than RETENTION_DAYS."""
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
