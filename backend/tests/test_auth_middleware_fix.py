"""
Unit and integration tests for Auth Middleware Fix from 08_Auth_Middleware_Fix.md:
- DB-based tier enforcement (SHA-256 hash lookup)
- Secure API key generation and revocation
- Header verification (X-RateLimit-Tier, X-RateLimit-Limit)
- Attack string rejection (e.g. 'pro_mygeneratedkey' should not grant Pro tier)
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, ApiKey
from app.core.auth import (
    hash_api_key,
    lookup_api_key_tier,
    get_rate_limit_for_tier,
    generate_api_key,
)

client = TestClient(app)


def test_hash_api_key_deterministic():
    k1 = "mgpt_free_0123456789abcdef"
    h1 = hash_api_key(k1)
    h2 = hash_api_key(k1)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex length


def test_lookup_api_key_tier_db_enforcement():
    db = SessionLocal()
    try:
        # 1. Create a Pro API Key
        record, raw_key = generate_api_key(db, tier="pro", name="Pro Integration Test Key")
        assert raw_key.startswith("mgpt_")
        assert record.tier == "pro"

        # 2. Look up key in DB
        tier, is_admin = lookup_api_key_tier(raw_key, db)
        assert tier == "pro"
        assert is_admin is False

        # 3. Revoke key
        record.revoked = True
        db.commit()

        # 4. Revoked key must return anonymous
        tier_revoked, _ = lookup_api_key_tier(raw_key, db)
        assert tier_revoked == "anonymous"

        # Clean up
        db.delete(record)
        db.commit()
    finally:
        db.close()


def test_spoofed_key_string_rejected():
    db = SessionLocal()
    try:
        # Attacker tries passing a string containing "pro" or "admin" to bypass auth
        attacker_key = "pro_fake_injected_key_123"
        tier, is_admin = lookup_api_key_tier(attacker_key, db)
        assert tier == "anonymous"
        assert is_admin is False

        attacker_admin_key = "admin_super_injected_key"
        tier_admin, is_admin_2 = lookup_api_key_tier(attacker_admin_key, db)
        assert tier_admin == "anonymous"
        assert is_admin_2 is False
    finally:
        db.close()


def test_api_request_with_valid_key_headers():
    db = SessionLocal()
    try:
        record, raw_key = generate_api_key(db, tier="free", name="Header Test Key")

        # Test request using X-API-Key header
        resp = client.get("/api/v1/auth/tier", headers={"X-API-Key": raw_key})
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "free"
        assert data["rate_limit"] == 120
        assert resp.headers.get("X-RateLimit-Tier") == "free"
        assert resp.headers.get("X-RateLimit-Limit") == "120"

        # Clean up
        db.delete(record)
        db.commit()
    finally:
        db.close()
