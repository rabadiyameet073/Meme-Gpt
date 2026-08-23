"""Database CRUD Tests from 10_Testing/Backend_Tests.md."""

from app.database import SessionLocal, Meme, Feedback


def test_database_session():
    db = SessionLocal()
    try:
        count = db.query(Meme).count()
        assert isinstance(count, int)
    finally:
        db.close()


def test_database_feedback_query():
    db = SessionLocal()
    try:
        feedbacks = db.query(Feedback).limit(5).all()
        assert isinstance(feedbacks, list)
    finally:
        db.close()
