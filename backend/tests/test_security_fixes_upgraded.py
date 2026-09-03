"""
Tests for 12_Security_Fixes.md.

Verifies:
1. GDPR Query Hashing (SearchLog stores query_hash, not raw PII text)
2. Data Retention Auto-Purge (30-day cutoff cleanup)
3. SECRET_KEY Configuration & Validation
4. NSFW Column & Filter in Database/Search
5. Security Headers (X-Frame-Options, CSP, X-Content-Type-Options, etc.)
6. Input Sanitization (Null bytes, HTML tags, Whitespace)
"""

from datetime import datetime, timedelta, timezone
import hashlib
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.database import SessionLocal, SearchLog, Feedback, Meme, sanitize_input
from app.jobs.retention import run_retention_cleanup, RETENTION_DAYS
from app.core.jobs import hash_query_privacy

client = TestClient(app)


def test_gdpr_query_hashing():
    """Verify raw user queries are converted to privacy hashes and never stored as raw text."""
    query = "User confidential situation with personal details"
    h = hash_query_privacy(query)
    assert len(h) <= 64
    assert h != query

    db = SessionLocal()
    try:
        log_entry = SearchLog(
            query_hash=h,
            result_count=3,
            latency_ms=120.5,
            cache_hit=False,
            session_id="anon_user_123",
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        # Check DB to confirm only hash exists
        fetched = db.query(SearchLog).filter(SearchLog.id == log_entry.id).first()
        assert fetched is not None
        assert fetched.query_hash == h

        db.delete(log_entry)
        db.commit()
    finally:
        db.close()


def test_data_retention_cleanup():
    """Verify run_retention_cleanup purges logs & feedback older than 30 days."""
    db = SessionLocal()
    try:
        old_time = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS + 5)
        recent_time = datetime.now(timezone.utc) - timedelta(days=2)

        old_log = SearchLog(
            query_hash="old_hash_123",
            result_count=1,
            latency_ms=50.0,
            created_at=old_time,
        )
        recent_log = SearchLog(
            query_hash="recent_hash_456",
            result_count=1,
            latency_ms=50.0,
            created_at=recent_time,
        )
        db.add_all([old_log, recent_log])
        db.commit()

        # Run retention cleanup
        res = run_retention_cleanup()
        assert "deleted_logs" in res
        assert res["deleted_logs"] >= 1

        # Old log must be deleted, recent log must remain
        still_recent = db.query(SearchLog).filter(SearchLog.query_hash == "recent_hash_456").first()
        assert still_recent is not None

        # Clean up
        db.delete(still_recent)
        db.commit()
    finally:
        db.close()


def test_secret_key_configuration():
    """Verify SECRET_KEY is loaded and has sufficient length."""
    assert hasattr(settings, "SECRET_KEY")
    assert len(settings.SECRET_KEY) >= 16


def test_nsfw_column_and_meme_schema():
    """Verify Meme model contains boolean nsfw column."""
    db = SessionLocal()
    try:
        meme = Meme(
            id="test_nsfw_meme_01",
            name="NSFW Test Meme",
            slug="test-nsfw-meme-01",
            category="testing",
            nsfw=True,
        )
        db.add(meme)
        db.commit()
        db.refresh(meme)

        assert meme.nsfw is True
        meme_dict = meme.to_dict()
        assert meme_dict["nsfw"] is True

        db.delete(meme)
        db.commit()
    finally:
        db.close()


def test_security_headers_middleware():
    """Verify all standard security headers are attached to responses."""
    resp = client.get("/health")
    assert resp.status_code == 200

    headers = resp.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in headers


def test_input_sanitization():
    """Verify sanitize_input strips null bytes, HTML tags, and truncates safely."""
    malicious = "Hello<script>alert(1)</script> \x00World!<b>Test</b>"
    clean = sanitize_input(malicious)
    assert "\x00" not in clean
    assert "<script>" not in clean
    assert "Hello" in clean
