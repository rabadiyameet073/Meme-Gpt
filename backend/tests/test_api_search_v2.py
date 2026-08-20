"""Tests for Search API from 07_APIs/Search_API.md."""

import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, Meme

client = TestClient(app)
init_db()


def test_post_search_standard_request():
    with next(get_db()) as db:
        test_id = f"search_meme_{uuid.uuid4().hex[:6]}"
        db.add(Meme(
            id=test_id,
            name="Meeting Could Be Email",
            slug=f"meeting-email-{test_id}",
            category="work",
            dialogue="This meeting could have been an email",
            explanation="Unnecessary corporate meeting reaction",
            keywords='["work", "meeting", "email", "stress"]',
            gif_ref="https://cdn.memegpt.com/gifs/meeting-email.gif",
            image_ref="https://cdn.memegpt.com/images/meeting-email.jpg",
        ))
        db.commit()

    payload = {
        "query": "my boss scheduled a meeting that could have been an email",
        "format_preference": "gif",
        "nsfw": False,
        "limit": 5,
        "session_id": "sess_abc123",
        "filters": {
            "categories": ["work"],
            "exclude_ids": [],
        },
    }

    response = client.post("/api/v1/search", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "query_id" in data
    assert "results" in data
    assert len(data["results"]) >= 1
    assert "intent_parsed" in data
    assert "response_time_ms" in data
    assert "cached" in data

    first = data["results"][0]
    assert "id" in first
    assert "name" in first
    assert "slug" in first
    assert "relevance_score" in first
    assert "emotion_match" in first
    assert "preview_url" in first
    assert "formats" in first
    assert "share_url" in first
    assert "categories" in first


def test_post_search_exclude_filter():
    with next(get_db()) as db:
        test_id = f"exclude_{uuid.uuid4().hex[:6]}"
        db.add(Meme(
            id=test_id,
            name="Exclude This Meme",
            slug=f"exclude-{test_id}",
            category="gaming",
            dialogue="Excluded dialogue",
            explanation="Excluded explanation",
            keywords="[]",
        ))
        db.commit()

    payload = {
        "query": "gaming memes",
        "limit": 5,
        "filters": {
            "exclude_ids": [test_id],
        },
    }

    response = client.post("/api/v1/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    result_ids = [m["id"] for m in data["results"]]
    assert test_id not in result_ids


def test_post_search_validation_error():
    # Empty query violates min_length=1
    payload = {
        "query": "",
    }
    response = client.post("/api/v1/search", json=payload)
    assert response.status_code in (400, 422)
