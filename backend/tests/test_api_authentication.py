"""Tests for API Authentication from 07_APIs/Authentication.md."""

import pytest
from datetime import timedelta
from fastapi import HTTPException
from app.database import get_db, init_db, ApiKey
from app.core.auth import (
    get_api_tier,
    verify_api_key,
    generate_api_key,
    hash_api_key,
    create_access_token,
    create_refresh_token,
    verify_jwt_token,
    get_jwt_cookie_settings,
    AuthContext,
)
from app.services.auth_service import (
    get_auth_roadmap,
    get_auth_tiers_matrix,
    validate_api_key_format,
    create_user_session_tokens,
    get_oauth_providers_catalog,
)

init_db()


@pytest.mark.asyncio
async def test_anonymous_access_context():
    # Phase 1: Anonymous access without header returns anonymous tier and 60 req/min
    context = await get_api_tier(x_api_key=None, db=None)
    assert context.tier == "anonymous"
    assert context.rate_limit == 60
    assert context.user_id is None
    assert context.is_admin is False


@pytest.mark.asyncio
async def test_api_key_generation_and_verification():
    with next(get_db()) as db:
        # Generate new mgpt_live_ key
        key_obj, raw_token = generate_api_key(db, tier="pro", name="Test Pro Key", env="live")
        assert raw_token.startswith("mgpt_live_")
        assert len(raw_token) == len("mgpt_live_") + 32
        assert validate_api_key_format(raw_token) is True

        # Verify key in database via get_api_tier
        context = await get_api_tier(x_api_key=raw_token, db=db)
        assert context.tier == "pro"
        assert context.rate_limit == 300

        # Revoke key and verify 401 is raised
        key_obj.revoked = True
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            await get_api_tier(x_api_key=raw_token, db=db)
        assert exc_info.value.status_code == 401
        assert "Invalid or revoked API key" in exc_info.value.detail


@pytest.mark.asyncio
async def test_invalid_api_key():
    with next(get_db()) as db:
        with pytest.raises(HTTPException) as exc_info:
            await get_api_tier(x_api_key="mgpt_live_invalidkey1234567890abcdef", db=db)
        assert exc_info.value.status_code == 401


def test_validate_api_key_format():
    assert validate_api_key_format("mgpt_live_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4") is True
    assert validate_api_key_format("mgpt_test_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4") is True
    assert validate_api_key_format("pk_live_a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4") is True
    assert validate_api_key_format("invalid_key_format") is False
    assert validate_api_key_format("") is False


def test_jwt_access_and_refresh_tokens():
    payload = {"sub": "user_123", "email": "test@example.com", "plan": "pro"}
    
    access_token = create_access_token(payload, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(payload, expires_delta=timedelta(days=7))

    decoded_access = verify_jwt_token(access_token)
    assert decoded_access["sub"] == "user_123"
    assert decoded_access["type"] == "access"

    decoded_refresh = verify_jwt_token(refresh_token)
    assert decoded_refresh["sub"] == "user_123"
    assert decoded_refresh["type"] == "refresh"

    cookie_settings = get_jwt_cookie_settings()
    assert cookie_settings["httponly"] is True
    assert cookie_settings["secure"] is True
    assert cookie_settings["samesite"] == "lax"


def test_auth_services_catalogs():
    roadmap = get_auth_roadmap()
    assert len(roadmap["roadmap"]) == 3
    assert roadmap["roadmap"][0]["name"] == "Anonymous Access (MVP)"
    assert roadmap["roadmap"][1]["name"] == "API Key Authentication"
    assert roadmap["roadmap"][2]["name"] == "User Accounts (OAuth + JWT)"

    tiers = get_auth_tiers_matrix()
    assert len(tiers) == 4
    tier_map = {t["tier"]: t for t in tiers}
    assert tier_map["anonymous"]["rate_limit_per_min"] == 60
    assert tier_map["free"]["rate_limit_per_min"] == 120
    assert tier_map["pro"]["rate_limit_per_min"] == 300
    assert tier_map["internal"]["rate_limit_per_min"] == 1000

    oauth = get_oauth_providers_catalog()
    assert any(p["provider"] == "google" for p in oauth)
