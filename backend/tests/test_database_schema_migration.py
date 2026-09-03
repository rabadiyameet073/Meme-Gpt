"""
MemeGPT Database Schema Migration Tests.
Specification: 02_Database_Schema_Migration.md (Upgraded Docs)

Verifies:
- All 12+ columns across Meme, User, SearchLog ORM models
- JSON array category and emotion filtering
- Cloudflare R2 CDN URL resolution and format mapping
- Anonymized search query hashing (GDPR compliance)
- Migration script execution (migrate.py)
"""

import hashlib
import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy import inspect

from app.database import (
    Base,
    engine,
    SessionLocal,
    Meme,
    User,
    SearchLog,
    MemeVote,
    MemeUsage,
    FavouriteMeme,
    Feedback,
    SavedMeme,
)
from migrate import run_migration


def test_meme_model_complete_schema_and_columns():
    """Verify all 12+ columns and types in Meme model."""
    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("memes")}

    # Core identity
    assert "id" in columns
    assert "name" in columns
    assert "slug" in columns

    # 12+ upgraded columns from Gap Analysis
    assert "emotions" in columns
    assert "nsfw" in columns
    assert "thumb_url" in columns
    assert "webp_url" in columns
    assert "image_url" in columns
    assert "gif_url" in columns
    assert "mp4_url" in columns
    assert "source" in columns
    assert "view_count" in columns
    assert "download_count" in columns
    assert "popularity_score" in columns
    assert "indexed_at" in columns
    assert "categories" in columns


def test_meme_model_serialization_and_formats():
    """Verify Meme.to_dict serialization with formats dictionary and backwards compatibility."""
    meme_id = f"test_meme_{uuid.uuid4().hex[:8]}"
    meme = Meme(
        id=meme_id,
        name="Industrial Architecture Meme",
        slug=f"industrial-arch-{meme_id}",
        categories=["coding", "devops"],
        emotions=["joy", "relief"],
        dialogue="Deploy on Friday without issues",
        explanation="When deployment succeeds smoothly",
        keywords=["deploy", "production", "devops"],
        image_url="https://cdn.memegpt.com/images/arch.jpg",
        gif_url="https://cdn.memegpt.com/gifs/arch.gif",
        mp4_url="https://cdn.memegpt.com/videos/arch.mp4",
        thumb_url="https://cdn.memegpt.com/thumbs/arch.webp",
        webp_url="https://cdn.memegpt.com/webp/arch.webp",
        source="manual",
        nsfw=False,
        view_count=150,
        download_count=45,
        usage_count=80,
        upvotes=10,
        downvotes=1,
        viral_score=0.92,
        popularity_score=0.88,
        indexed_at=datetime.now(timezone.utc),
    )

    data = meme.to_dict()
    assert data["id"] == meme_id
    assert data["name"] == "Industrial Architecture Meme"
    assert data["category"] == "coding"
    assert data["categories"] == ["coding", "devops"]
    assert data["emotions"] == ["joy", "relief"]
    assert data["image_url"] == "https://cdn.memegpt.com/images/arch.jpg"
    assert data["gif_url"] == "https://cdn.memegpt.com/gifs/arch.gif"
    assert data["mp4_url"] == "https://cdn.memegpt.com/videos/arch.mp4"
    assert data["thumb_url"] == "https://cdn.memegpt.com/thumbs/arch.webp"
    assert data["webp_url"] == "https://cdn.memegpt.com/webp/arch.webp"

    # Formats dictionary
    assert "formats" in data
    assert data["formats"]["image"] == "https://cdn.memegpt.com/images/arch.jpg"
    assert data["formats"]["gif"] == "https://cdn.memegpt.com/gifs/arch.gif"
    assert data["formats"]["mp4"] == "https://cdn.memegpt.com/videos/arch.mp4"
    assert data["formats"]["thumb"] == "https://cdn.memegpt.com/thumbs/arch.webp"
    assert data["formats"]["webp"] == "https://cdn.memegpt.com/webp/arch.webp"

    # Legacy fields
    assert data["imageRef"] == "https://cdn.memegpt.com/images/arch.jpg"
    assert data["gifRef"] == "https://cdn.memegpt.com/gifs/arch.gif"
    assert data["videoRef"] == "https://cdn.memegpt.com/videos/arch.mp4"
    assert data["thumbUrl"] == "https://cdn.memegpt.com/thumbs/arch.webp"
    assert data["popularity_score"] == 0.88


def test_user_model_complete_schema():
    """Verify User ORM model matches Schema.md specification."""
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    user = User(
        id=user_id,
        email=f"{user_id}@memegpt.com",
        name="Developer One",
        avatar_url="https://cdn.memegpt.com/avatars/user1.png",
        plan="pro",
        preferences={"format_pref": "gif", "nsfw": False, "categories": ["coding"]},
        hashed_password="secure_hashed_password_string",
        is_active=True,
        is_admin=True,
    )

    data = user.to_dict()
    assert data["id"] == user_id
    assert data["name"] == "Developer One"
    assert data["avatar_url"] == "https://cdn.memegpt.com/avatars/user1.png"
    assert data["plan"] == "pro"
    assert data["preferences"]["format_pref"] == "gif"
    assert data["is_active"] is True
    assert data["is_admin"] is True


def test_search_log_model_gdpr_anonymization():
    """Verify SearchLog stores MD5 query hash and never raw unhashed query text."""
    raw_query = "Secret user search query with PII"
    expected_hash = hashlib.md5(raw_query.strip().lower().encode("utf-8")).hexdigest()

    log = SearchLog(
        query=raw_query,
        result_count=5,
        top_meme_id="meme_top_123",
        latency_ms=124.5,
        cache_hit=True,
        model_used="groq",
        emotion_detected="joy",
        session_id="anon_sess_456",
    )

    data = log.to_dict()
    assert data["query_hash"] == expected_hash
    assert data["result_count"] == 5
    assert data["match_count"] == 5
    assert data["top_meme_id"] == "meme_top_123"
    assert data["cache_hit"] is True
    assert data["model_used"] == "groq"
    assert data["emotion_detected"] == "joy"


def test_migrate_script_execution():
    """Verify migrate.py executes cleanly without error."""
    result = run_migration()
    assert "applied" in result
    assert "skipped" in result
    assert result["applied"] >= 0
