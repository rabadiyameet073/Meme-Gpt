from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal, Meme, SearchLog
from app.core.jobs import (
    log_search_task,
    update_usage_counts_task,
    recalculate_popularity_scores,
    warm_up_cache_task,
    aggregate_analytics_task,
    hash_query_privacy,
)

init_db()
client = TestClient(app)


def test_privacy_query_hashing():
    q = "Secret production error with customer email user@example.com"
    h1 = hash_query_privacy(q)
    h2 = hash_query_privacy(q)
    assert h1 == h2
    assert len(h1) == 12
    assert "user@example.com" not in h1


def test_log_search_background_task():
    db = SessionLocal()
    initial_count = db.query(SearchLog).count()

    log_search_task(
        query="Friday deploy break everything",
        match_count=5,
        latency_ms=123.4,
        emotion="fear",
        cached=False,
        session_id="test-session-123"
    )

    new_count = db.query(SearchLog).count()
    assert new_count == initial_count + 1

    latest = db.query(SearchLog).order_by(SearchLog.created_at.desc()).first()
    assert latest.match_count == 5
    assert latest.latency_ms == 123.4
    db.close()


def test_popularity_and_cache_jobs():
    # 1. Recalculate popularity
    res = recalculate_popularity_scores()
    assert res["status"] == "success"
    assert res["updated_memes"] >= 0

    # 2. Warm up cache
    warm_res = warm_up_cache_task(["deploy to production", "first try success"])
    assert warm_res["status"] == "success"
    assert warm_res["warmed_queries"] >= 1

    # 3. Aggregate analytics
    stats = aggregate_analytics_task()
    assert "total_searches" in stats
    assert "avg_latency_ms" in stats


def test_admin_job_endpoints():
    # 1. Unauthorized attempt returns 403
    unauth = client.post("/api/v1/auth/jobs/warm-up")
    assert unauth.status_code == 403

    # 2. Authorized admin trigger returns 200
    auth_res = client.post(
        "/api/v1/auth/jobs/warm-up",
        headers={"X-API-Key": "memegpt_admin_secret_key"}
    )
    assert auth_res.status_code == 200
    assert auth_res.json()["status"] == "success"
