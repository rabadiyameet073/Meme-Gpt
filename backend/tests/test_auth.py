"""
MemeGPT — Authentication & API Key Tests.
"""

import pytest
from app.core.auth import (
    hash_api_key,
    generate_api_key,
    create_access_token,
    verify_jwt_token,
    lookup_api_key_tier,
)


def test_api_key_hashing():
    """Test API key hashing is deterministic SHA-256."""
    key = "mgpt_live_test1234567890abcdef"
    h1 = hash_api_key(key)
    h2 = hash_api_key(key)
    assert h1 == h2
    assert len(h1) == 64


def test_generate_api_key(db_session):
    """Test API key generation creates record with correct prefix and hash."""
    api_key_obj, raw_token = generate_api_key(
        db=db_session,
        tier="pro",
        name="Test Pro Key",
    )
    assert raw_token.startswith("mgpt_live_")
    assert api_key_obj.tier == "pro"
    assert api_key_obj.key_hash == hash_api_key(raw_token)

    # Verify lookup
    tier, is_admin = lookup_api_key_tier(raw_token, db_session)
    assert tier == "pro"
    assert is_admin is False


def test_jwt_token_creation_and_verification():
    """Test creating and decoding short-lived JWT token."""
    payload = {"sub": "user-123", "email": "test@memegpt.com", "role": "user"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    decoded = verify_jwt_token(token)
    assert decoded.get("sub") == "user-123"
    assert decoded.get("email") == "test@memegpt.com"
    assert decoded.get("type") == "access"
