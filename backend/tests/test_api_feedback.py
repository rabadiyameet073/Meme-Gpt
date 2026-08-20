"""Tests for Feedback API from 07_APIs/Feedback_API.md."""

import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, Meme, Feedback

client = TestClient(app)
init_db()


def test_post_feedback_endpoint_valid_actions():
    with next(get_db()) as db:
        # Create test meme
        test_id = f"test_fb_meme_{uuid.uuid4().hex[:8]}"
        meme = Meme(
            id=test_id,
            name="Test Feedback Meme",
            slug=f"test-fb-{test_id}",
            category="test",
            dialogue="dialogue",
            explanation="explanation",
            keywords="[]",
            viral_score=1.0,
            usage_count=0,
        )
        db.add(meme)
        db.commit()

    # 1. Download action
    payload = {
        "query_id": "q_xyz789",
        "meme_id": test_id,
        "action": "download",
        "session_id": "sess_abc123",
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Feedback recorded"

    # 2. View action
    payload_view = {
        "query_id": "q_xyz789",
        "meme_id": test_id,
        "action": "view",
        "session_id": "sess_abc123",
    }
    response_view = client.post("/api/v1/feedback", json=payload_view)
    assert response_view.status_code == 200
    assert response_view.json()["success"] is True

    # 3. Thumbs up action
    payload_up = {
        "query_id": "q_xyz789",
        "meme_id": test_id,
        "action": "thumbs_up",
        "session_id": "sess_abc123",
    }
    response_up = client.post("/api/v1/feedback", json=payload_up)
    assert response_up.status_code == 200
    assert response_up.json()["success"] is True

    # Check database persistence
    with next(get_db()) as db:
        fb_records = db.query(Feedback).filter(Feedback.meme_id == test_id).all()
        assert len(fb_records) >= 3
        actions = {r.action for r in fb_records}
        assert "download" in actions
        assert "view" in actions
        assert "thumbs_up" in actions


def test_post_feedback_invalid_action():
    with next(get_db()) as db:
        test_id = f"test_invalid_{uuid.uuid4().hex[:8]}"
        db.add(Meme(
            id=test_id,
            name="Invalid FB Meme",
            slug=f"invalid-fb-{test_id}",
            category="test",
            dialogue="dialogue",
            explanation="explanation",
            keywords="[]",
        ))
        db.commit()

    payload = {
        "query_id": "q_123",
        "meme_id": test_id,
        "action": "non_existent_action",
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 400
    res_data = response.json()
    err_msg = res_data.get("message") or res_data.get("detail", "")
    assert "Invalid action" in err_msg or "error" in res_data


def test_post_feedback_meme_not_found():
    payload = {
        "query_id": "q_123",
        "meme_id": "non_existent_meme_id_99999",
        "action": "click",
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 404
    res_data = response.json()
    err_msg = res_data.get("message") or res_data.get("detail", "")
    assert "Meme not found" in err_msg or "error" in res_data
