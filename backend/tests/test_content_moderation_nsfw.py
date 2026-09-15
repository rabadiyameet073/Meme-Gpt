"""
Unit and Integration Tests for Guide 05: Content Moderation & NSFW.
Tests:
- Community flagging API (POST /api/v1/moderation/flag)
- Auto-escalation threshold (5 flags -> pending_review)
- Moderation review queue (GET /api/v1/moderation/queue)
- Admin review actions (POST /api/v1/moderation/review approve & remove)
- Search and list queries excluding removed memes
- Trending catalog excluding removed memes
- CLIP zero-shot NSFW classifier service & API (POST /api/v1/moderation/classify)
"""

import pytest
from unittest.mock import patch, MagicMock
from app.database import Meme, MemeFlag
from app.services.trending_service import get_trending_catalog, _TRENDING_HOURLY_CACHE


def test_flag_meme_creates_flag_and_increments_count(client, db, sample_meme):
    """Community flagging creates a MemeFlag record and increments meme.flag_count."""
    resp = client.post(
        "/api/v1/moderation/flag",
        json={"meme_id": sample_meme.id, "reason": "nsfw", "details": "Explicit visual content"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["flagged"] is True
    assert data["total_flags"] == 1
    assert data["moderation_status"] == "approved"

    # Verify in DB
    db.refresh(sample_meme)
    assert sample_meme.flag_count == 1
    flag = db.query(MemeFlag).filter(MemeFlag.meme_id == sample_meme.id).first()
    assert flag is not None
    assert flag.reason == "nsfw"
    assert flag.details == "Explicit visual content"
    assert flag.status == "pending"


def test_flag_meme_invalid_reason(client, sample_meme):
    """Flagging with an unsupported reason returns 400 Bad Request."""
    resp = client.post(
        "/api/v1/moderation/flag",
        json={"meme_id": sample_meme.id, "reason": "nonsense_reason"},
    )
    assert resp.status_code == 400
    assert "Invalid reason" in resp.text


def test_flag_meme_not_found(client):
    """Flagging a non-existent meme returns 404."""
    resp = client.post(
        "/api/v1/moderation/flag",
        json={"meme_id": "nonexistent-id-999", "reason": "spam"},
    )
    assert resp.status_code == 404


def test_auto_queue_at_five_flags(client, db, sample_meme):
    """Meme status automatically transitions to pending_review on 5th flag."""
    sample_meme.flag_count = 0
    sample_meme.moderation_status = "approved"
    db.commit()

    for i in range(1, 5):
        resp = client.post(
            "/api/v1/moderation/flag",
            json={"meme_id": sample_meme.id, "reason": "offensive", "details": f"Flag #{i}"},
        )
        assert resp.status_code == 200
        assert resp.json()["moderation_status"] == "approved"
        assert resp.json()["total_flags"] == i

    # 5th flag triggers pending_review
    resp = client.post(
        "/api/v1/moderation/flag",
        json={"meme_id": sample_meme.id, "reason": "offensive", "details": "Flag #5"},
    )
    assert resp.status_code == 200
    assert resp.json()["moderation_status"] == "pending_review"
    assert resp.json()["total_flags"] == 5

    db.refresh(sample_meme)
    assert sample_meme.moderation_status == "pending_review"
    assert sample_meme.flag_count == 5


def test_get_moderation_queue(client, db, sample_meme):
    """Moderation queue returns all memes with status == pending_review."""
    sample_meme.moderation_status = "pending_review"
    sample_meme.flag_count = 7
    flag = MemeFlag(
        meme_id=sample_meme.id,
        reason="nsfw",
        details="Reported by user test",
    )
    db.add(flag)
    db.commit()

    resp = client.get("/api/v1/moderation/queue")
    assert resp.status_code == 200
    data = resp.json()
    assert "queue" in data
    queue_ids = [m["id"] for m in data["queue"]]
    assert sample_meme.id in queue_ids

    # Check that flag details are included
    item = next(m for m in data["queue"] if m["id"] == sample_meme.id)
    assert item["flag_count"] == 7
    assert len(item["flags"]) >= 1
    assert item["flags"][0]["reason"] == "nsfw"


def test_admin_review_approve(client, db, sample_meme):
    """Admin 'approve' resets flag_count to 0, sets status to approved, and dismisses flags."""
    sample_meme.moderation_status = "pending_review"
    sample_meme.flag_count = 5
    flag = MemeFlag(meme_id=sample_meme.id, reason="spam", status="pending")
    db.add(flag)
    db.commit()

    resp = client.post(
        "/api/v1/moderation/review",
        json={"meme_id": sample_meme.id, "action": "approve"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"

    db.refresh(sample_meme)
    assert sample_meme.moderation_status == "approved"
    assert sample_meme.flag_count == 0

    db.refresh(flag)
    assert flag.status == "dismissed"
    assert flag.reviewed_at is not None


def test_admin_review_remove(client, db, sample_meme):
    """Admin 'remove' sets status to removed and marks flags reviewed."""
    sample_meme.moderation_status = "pending_review"
    sample_meme.flag_count = 6
    flag = MemeFlag(meme_id=sample_meme.id, reason="offensive", status="pending")
    db.add(flag)
    db.commit()

    resp = client.post(
        "/api/v1/moderation/review",
        json={"meme_id": sample_meme.id, "action": "remove"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "removed"

    db.refresh(sample_meme)
    assert sample_meme.moderation_status == "removed"

    db.refresh(flag)
    assert flag.status == "reviewed"
    assert flag.reviewed_at is not None


def test_admin_review_invalid_action(client, sample_meme):
    """Admin review with invalid action returns 400 Bad Request."""
    resp = client.post(
        "/api/v1/moderation/review",
        json={"meme_id": sample_meme.id, "action": "ignore"},
    )
    assert resp.status_code == 400
    assert "Action must be 'approve' or 'remove'" in resp.text


def test_search_and_memes_exclude_removed(client, db, sample_meme):
    """Removed memes must be excluded from search queries and meme listings."""
    # Initially, sample_meme is approved
    resp = client.get("/api/v1/memes")
    assert resp.status_code == 200
    meme_ids = [m["id"] for m in resp.json()["items"]]
    assert sample_meme.id in meme_ids

    # Set sample_meme to removed
    sample_meme.moderation_status = "removed"
    db.commit()

    # Listing must not include sample_meme
    resp = client.get("/api/v1/memes")
    assert resp.status_code == 200
    meme_ids = [m["id"] for m in resp.json()["items"]]
    assert sample_meme.id not in meme_ids

    # Search endpoint must not include sample_meme
    search_resp = client.post(
        "/api/v1/search",
        json={"query": "drake pointing", "limit": 10},
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    result_ids = [r["id"] for r in search_data.get("results", [])]
    if search_data.get("primary"):
        result_ids.append(search_data["primary"]["id"])
    assert sample_meme.id not in result_ids


def test_trending_excludes_removed(db, sample_meme):
    """Trending catalog must omit memes with moderation_status == 'removed'."""
    _TRENDING_HOURLY_CACHE.clear()

    # Active memes
    catalog_before = get_trending_catalog(db=db, category="all", period="24h")
    ids_before = [item["id"] for item in catalog_before["data"]["results"]]
    assert sample_meme.id in ids_before

    # Suppress meme
    sample_meme.moderation_status = "removed"
    db.commit()
    _TRENDING_HOURLY_CACHE.clear()

    catalog_after = get_trending_catalog(db=db, category="all", period="24h")
    ids_after = [item["id"] for item in catalog_after["data"]["results"]]
    assert sample_meme.id not in ids_after



def test_classify_endpoint_mocked(client):
    """POST /api/v1/moderation/classify returns zero-shot safety scores."""
    with patch("app.services.nsfw_service.classify_image_from_url") as mock_classify:
        mock_classify.return_value = (False, 0.0825, "safe content")
        resp = client.post(
            "/api/v1/moderation/classify",
            json={"image_url": "https://i.imgflip.com/test.jpg"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_nsfw"] is False
        assert data["confidence"] == 0.0825
        assert data["category"] == "safe content"

    # Test NSFW positive response
    with patch("app.services.nsfw_service.classify_image_from_url") as mock_classify:
        mock_classify.return_value = (True, 0.8950, "nsfw adult content")
        resp = client.post(
            "/api/v1/moderation/classify",
            json={"image_url": "https://i.imgflip.com/nsfw.jpg"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_nsfw"] is True
        assert data["confidence"] == 0.8950
        assert data["category"] == "nsfw adult content"


def test_classify_missing_params(client):
    """Missing both image_url and image_path returns 400."""
    resp = client.post("/api/v1/moderation/classify", json={})
    assert resp.status_code == 400
    assert "Provide either image_url or image_path" in resp.text


def test_nsfw_service_fallback():
    """NSFW service gracefully handles unloaded CLIP model."""
    from app.services.nsfw_service import classify_image
    with patch("app.services.nsfw_service._clip_model", None):
        with patch("app.services.nsfw_service._load_clip"):
            is_nsfw, conf, cat = classify_image("dummy_path.jpg")
            assert is_nsfw is False
            assert conf == 0.0
            assert cat == "safe content"
