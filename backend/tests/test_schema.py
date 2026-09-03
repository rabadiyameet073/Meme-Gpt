"""
Unit tests for Database Schema verification from 14_Testing_Suite.md.
"""

def test_meme_has_all_required_columns(db):
    """Verify Meme model has all documented columns."""
    from app.database import Meme
    from sqlalchemy import inspect

    inspector = inspect(db.bind)
    cols = {c["name"] for c in inspector.get_columns("memes")}

    required = {
        "id", "name", "slug", "categories", "emotions",
        "nsfw", "thumb_url", "source", "view_count",
        "download_count", "popularity_score", "indexed_at",
    }
    missing = required - cols
    assert not missing, f"Missing columns: {missing}"


def test_search_log_no_raw_query(db):
    """SearchLog should have query_hash for GDPR privacy compliance."""
    from sqlalchemy import inspect
    inspector = inspect(db.bind)
    cols = {c["name"] for c in inspector.get_columns("search_logs")}
    assert "query_hash" in cols
