"""
Push notification registration — POST /api/v1/mobile/push-tokens.

The mobile client obtains an Expo push token after the user grants notification
permission and POSTs it here. Before this existed the endpoint, the table and the
client wiring were all missing, so "push notifications" was a documented feature
with nothing behind it.

Covered:
- registration creates a device row and masks the token in the response
- re-registration is idempotent (no duplicate rows, row reactivated)
- deletion deactivates rather than hard-deleting, and drops out of the list
- unknown token delete is a 404
- an unsupported platform is rejected by validation
"""

import pytest

from app.database import DeviceToken

TOKEN = "ExponentPushToken[test-device-0001]"


def test_register_push_token_creates_masked_device(client, db):
    resp = client.post(
        "/api/v1/mobile/push-tokens",
        json={"token": TOKEN, "platform": "android", "app_version": "1.0.0"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["created"] is True

    device = body["device"]
    assert device["platform"] == "android"
    assert device["app_version"] == "1.0.0"
    assert device["active"] is True
    # The raw token is a device credential and must not be echoed back.
    assert TOKEN not in resp.text
    assert device["token_preview"].startswith("ExponentPushTo")

    stored = db.query(DeviceToken).filter(DeviceToken.token == TOKEN).all()
    assert len(stored) == 1


def test_register_push_token_is_idempotent(client, db):
    first = client.post("/api/v1/mobile/push-tokens", json={"token": TOKEN, "platform": "android"})
    second = client.post("/api/v1/mobile/push-tokens", json={"token": TOKEN, "platform": "ios"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["created"] is False
    assert second.json()["device"]["platform"] == "ios"

    rows = db.query(DeviceToken).filter(DeviceToken.token == TOKEN).all()
    assert len(rows) == 1, "re-registering the same token must not create a duplicate"
    assert rows[0].active is True


def test_unregister_push_token_deactivates_and_hides_it(client, db):
    client.post("/api/v1/mobile/push-tokens", json={"token": TOKEN, "platform": "ios"})

    listed = client.get("/api/v1/mobile/push-tokens")
    assert listed.status_code == 200
    assert listed.json()["count"] == 1

    removed = client.delete(f"/api/v1/mobile/push-tokens/{TOKEN}")
    assert removed.status_code == 200
    assert removed.json()["device"]["active"] is False

    # The row is kept for auditability but is no longer an active target.
    row = db.query(DeviceToken).filter(DeviceToken.token == TOKEN).first()
    assert row is not None
    assert row.active is False

    assert client.get("/api/v1/mobile/push-tokens").json()["count"] == 0


def test_unregister_unknown_token_returns_404(client):
    resp = client.delete("/api/v1/mobile/push-tokens/ExponentPushToken[never-registered]")
    assert resp.status_code == 404


@pytest.mark.parametrize("platform", ["blackberry", "", "ANDROID"])
def test_register_push_token_rejects_unknown_platform(client, platform):
    resp = client.post("/api/v1/mobile/push-tokens", json={"token": TOKEN, "platform": platform})
    assert resp.status_code == 422
