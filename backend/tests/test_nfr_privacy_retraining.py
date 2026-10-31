"""
MemeGPT — Unit & Integration Tests for Non-Functional Requirements, Privacy & Retraining (Guide 15).
"""

import sys
import uuid
from pathlib import Path

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

# Add workspace root to sys.path so root scripts can be imported during test runs
workspace_root = str(Path(__file__).resolve().parent.parent.parent)
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from app.core.auth import create_access_token
from app.core.jobs import recalculate_persisted_popularity
from app.database import Feedback, Meme, SavedMeme, SearchLog, SessionLocal, User
from app.main import app
from app.services.llm_service import _rule_based_intent
from scripts.dmca_takedown import process_takedown
from scripts.optimize_rerank_weights import calibrate

client = TestClient(app)


# ── Step 1: CDN Cache-Control Headers Middleware ─────────────────────────────

def test_cache_control_headers():
    """Verify CacheHeaderMiddleware injects long-lived and trending cache headers."""
    # 1. Download endpoint caching
    r_dl = client.get("/api/v1/memes/drake-pointing/download?format=gif", follow_redirects=False)
    assert "Cache-Control" in r_dl.headers
    assert "31536000" in r_dl.headers["Cache-Control"]

    # 2. Trending endpoint caching
    r_tr = client.get("/api/v1/trending")
    assert "Cache-Control" in r_tr.headers
    assert "1800" in r_tr.headers["Cache-Control"]


# ── Step 2: GDPR Automated Data Deletion Protocol ────────────────────────────

def test_gdpr_data_deletion_flow():
    """Test GDPR Right to be Forgotten: purges saved memes, user, and anonymizes feedback."""
    db: Session = SessionLocal()
    unique_email = f"gdpr_user_{uuid.uuid4().hex[:8]}@example.com"
    test_user = User(
        email=unique_email,
        username=f"gdpr_{uuid.uuid4().hex[:6]}",
        hashed_password="fakehashedpassword123",
        plan="free",
        is_active=True,
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    user_id = test_user.id

    # Create a saved meme record
    saved = SavedMeme(
        user_id=user_id,
        meme_id="m_ed49b1216dfd",
        collection_name="Favorites",
    )
    # Create a feedback entry
    fb = Feedback(
        user_id=user_id,
        session_id=str(user_id),
        meme_id="m_ed49b1216dfd",
        action="thumbs_up",
    )
    # Create a search log entry
    slog = SearchLog(
        session_id=str(user_id),
        query_hash="test_hash_123",
        result_count=5,
    )
    db.add(saved)
    db.add(fb)
    db.add(slog)
    db.commit()

    # Generate auth token
    token = create_access_token({"sub": str(user_id), "email": unique_email})
    headers = {"Authorization": f"Bearer {token}"}

    # Call GDPR deletion endpoint
    resp = client.delete("/api/v1/privacy/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "purged" in data["message"]

    # Verify user record is deleted
    assert db.query(User).filter(User.id == user_id).first() is None

    # Verify saved memes are deleted
    assert db.query(SavedMeme).filter(SavedMeme.user_id == user_id).count() == 0

    # Verify feedback record is anonymized
    updated_fb = db.query(Feedback).filter(Feedback.id == fb.id).first()
    assert updated_fb.user_id == "anonymized"
    assert updated_fb.session_id == "anonymized"

    # Verify search log is anonymized
    updated_slog = db.query(SearchLog).filter(SearchLog.id == slog.id).first()
    assert updated_slog.session_id == "anonymized"

    db.close()


# ── Step 3: DMCA Takedown CLI Script ─────────────────────────────────────────

def test_dmca_takedown_dry_run():
    """Verify DMCA script dry-run executes cleanly without removing data."""
    success = process_takedown(slug="nonexistent-meme-slug-123", reason="Audit Verification", dry_run=True)
    assert success is True


def test_dmca_takedown_execution():
    """Verify DMCA takedown permanently deletes target meme from DB."""
    db: Session = SessionLocal()
    temp_slug = f"dmca-target-{uuid.uuid4().hex[:6]}"
    temp_meme = Meme(
        id=f"m_dmca_{uuid.uuid4().hex[:6]}",
        name="DMCA Infringing Test Meme",
        slug=temp_slug,
        image_url="https://example.com/dmca.jpg",
        category="testing",
        moderation_status="approved",
    )
    db.add(temp_meme)
    db.commit()

    # Verify meme exists
    assert db.query(Meme).filter(Meme.slug == temp_slug).first() is not None

    # Execute takedown
    deleted = process_takedown(slug=temp_slug, reason="DMCA Notice #999", dry_run=False)
    assert deleted is True

    # Verify meme is removed from database
    assert db.query(Meme).filter(Meme.slug == temp_slug).first() is None
    db.close()


# ── Step 4: Re-ranker Optimization ───────────────────────────────────────────

def test_optimize_rerank_weights():
    """Verify the weekly calibration job reports on the feedback loop.

    Scoring itself belongs to `sync_popularity_scores.py`; this job only measures
    whether the stored popularity ranking agrees with the thumbs users cast.
    """
    report = calibrate(window_days=7)

    assert report["window_days"] == 7
    assert report["status"] in {"ok", "insufficient_signal", "anti_correlated"}
    # Emitted in every branch so the uploaded artifact is always comparable.
    assert report["composite_weights"]["semantic"] == 0.34
    assert abs(sum(report["composite_weights"].values()) - 1.0) < 1e-9


def test_feedback_recalculates_persisted_popularity(db_session):
    """Thumbs-up feedback must raise the persisted popularity score."""
    meme = Meme(
        id="m_popularity_probe",
        name="Popularity Probe Meme",
        slug="popularity-probe-meme",
        categories=["tech"],
        emotions=["joy"],
        dialogue="probe",
        explanation="probe",
        keywords=["probe"],
        source="test",
        moderation_status="approved",
        popularity_score=0.0,
        viral_score=0.0,
    )
    db_session.add(meme)
    db_session.add_all([
        Feedback(meme_id=meme.id, action="thumbs_up", session_id="probe"),
        Feedback(meme_id=meme.id, action="download", session_id="probe"),
        Feedback(meme_id=meme.id, action="share", session_id="probe"),
    ])
    db_session.commit()

    result = recalculate_persisted_popularity(db_session, window_days=30)
    assert result["status"] == "success"
    assert result["with_recent_feedback"] >= 1

    db_session.refresh(meme)
    assert meme.popularity_score > 0.0

    # Running the job again must not change the answer: the old implementation
    # fed `viral_score` back into its own formula and tripled it every run.
    first_popularity = meme.popularity_score
    first_viral = meme.viral_score
    recalculate_persisted_popularity(db_session, window_days=30)
    db_session.refresh(meme)
    assert meme.popularity_score == first_popularity
    assert meme.viral_score == first_viral


# ── Step 5: Multi-Language Intent Extraction ─────────────────────────────────

def test_multilingual_intent_extraction():
    """Verify Spanish, Hindi, and Portuguese queries are correctly mapped to concepts."""
    # Spanish coding query
    res_es = _rule_based_intent("cuando el código no compila y te da error")
    assert "coding" in res_es["categories"]

    # Spanish/Portuguese work query
    res_work = _rule_based_intent("jefe me llama a una reunión urgente en la oficina")
    assert "work" in res_work["categories"]

    # Hindi surprise/informal query
    res_hi = _rule_based_intent("kya hua yaar itna shock kyu hai")
    assert res_hi["emotion"] in ("surprise", "neutral")
