"""
Weekly Re-ranker Optimization Script
Analyzes Feedback and SearchLog tables to update popularity and emotion affinity scores.
"""
import sys
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal, Meme, Feedback
from sqlalchemy import func, case

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memegpt.optimizer")


def optimize_weights():
    db = SessionLocal()
    try:
        stats = db.query(
            Feedback.meme_id,
            func.count(Feedback.id).label("total_interactions"),
            func.sum(case((Feedback.action == "thumbs_up", 1), else_=0)).label("upvotes"),
            func.sum(case((Feedback.action == "thumbs_down", 1), else_=0)).label("downvotes"),
        ).group_by(Feedback.meme_id).all()

        updated_count = 0
        for s in stats:
            meme = db.query(Meme).filter(Meme.id == s.meme_id).first()
            if meme and s.total_interactions > 0:
                upvotes = s.upvotes or 0
                total = s.total_interactions
                score = (upvotes + 1.0) / (total + 2.0)
                meme.popularity_score = round(score, 3)
                updated_count += 1

        db.commit()
        print(f"[SUCCESS] Updated popularity scores for {updated_count} memes.")
    finally:
        db.close()


if __name__ == "__main__":
    optimize_weights()
