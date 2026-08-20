"""Tests for Webhooks API from 07_APIs/Webhooks.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.webhook_service import (
    generate_webhook_signature,
    verify_webhook_signature,
    create_webhook_payload,
    get_supported_webhook_events,
)

client = TestClient(app)


def test_webhook_supported_events():
    response = client.get("/api/v1/webhooks/events")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    events = data["events"]
    assert "meme.trending" in events
    assert "meme.new" in events
    assert "search.popular" in events
    assert "collection.updated" in events


def test_webhook_crud_and_dispatch():
    # 1. Register webhook
    payload = {
        "url": "https://example.com/webhooks/memegpt",
        "events": ["meme.trending", "meme.new"],
        "secret": "my_super_secret_webhook_key_123",
    }
    response = client.post("/api/v1/webhooks", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    wh_id = res["webhook"]["id"]
    assert res["webhook"]["url"] == "https://example.com/webhooks/memegpt"
    assert "meme.trending" in res["webhook"]["events"]

    # 2. List webhooks
    res_list = client.get("/api/v1/webhooks")
    assert res_list.status_code == 200
    assert any(w["id"] == wh_id for w in res_list.json()["webhooks"])

    # 3. Test dispatch
    dispatch_req = {
        "event": "meme.trending",
        "data": {
            "meme_id": "meme_042",
            "name": "This Is Fine",
            "trending_score": 0.94,
        }
    }
    res_disp = client.post("/api/v1/webhooks/test-dispatch", json=dispatch_req)
    assert res_disp.status_code == 200
    disp_data = res_disp.json()
    assert disp_data["success"] is True
    assert disp_data["dispatched_count"] >= 1
    delivery = disp_data["deliveries"][0]
    assert delivery["headers"]["X-Webhook-Event"] == "meme.trending"
    assert "X-Webhook-Signature" in delivery["headers"]
    assert delivery["payload"]["data"]["meme_id"] == "meme_042"

    # 4. Delete webhook
    res_del = client.delete(f"/api/v1/webhooks/{wh_id}")
    assert res_del.status_code == 200
    assert res_del.json()["deleted_id"] == wh_id


def test_webhook_invalid_registration():
    # Invalid URL scheme
    bad_url = {
        "url": "ftp://invalid-url.com",
        "events": ["meme.trending"],
        "secret": "valid_secret_123",
    }
    res_bad_url = client.post("/api/v1/webhooks", json=bad_url)
    assert res_bad_url.status_code == 400

    # Unsupported event
    bad_event = {
        "url": "https://example.com/hook",
        "events": ["invalid.event.name"],
        "secret": "valid_secret_123",
    }
    res_bad_event = client.post("/api/v1/webhooks", json=bad_event)
    assert res_bad_event.status_code == 400


def test_webhook_signature_verification():
    secret = "secret_key_abc_123"
    payload = {
        "event": "meme.trending",
        "timestamp": "2026-08-02T04:30:00Z",
        "data": {
            "meme_id": "meme_042",
            "name": "This Is Fine",
            "trending_score": 0.94,
        },
    }

    sig = generate_webhook_signature(payload, secret)
    assert sig.startswith("sha256=")

    # Valid check
    assert verify_webhook_signature(payload, secret, sig) is True

    # Tampered payload
    tampered_payload = {**payload, "event": "meme.tampered"}
    assert verify_webhook_signature(tampered_payload, secret, sig) is False

    # Wrong secret
    assert verify_webhook_signature(payload, "wrong_secret", sig) is False
