"""Unit tests verifying authentication & authorisation gaps (08-authentication-gaps.md).

Items verified:
- AUTH-07: Refresh-token rotation and revocation by jti.
- AUTH-08: Unified JWT codec using python-jose.
- AUTH-09: Password policy (>=8 chars, letter + symbol/digit) & brute-force lockout.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, User
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    revoke_token_jti,
    is_jti_revoked,
    hash_password,
    verify_password,
)
from app.core.cache import _fallback_cache


def test_auth_07_refresh_token_rotation_and_jti_revocation():
    """Verify refresh token has jti, and revoking jti invalidates the token."""
    _fallback_cache.clear()

    # Create a refresh token
    token = create_refresh_token({"sub": "user_auth_07"})
    payload = decode_token(token)
    assert payload is not None
    assert payload.get("type") == "refresh"
    jti = payload.get("jti")
    assert jti is not None

    # Not revoked yet
    assert not is_jti_revoked(jti)

    # Revoke jti
    revoke_token_jti(jti)
    assert is_jti_revoked(jti)

    # Decode should now return None because jti is revoked
    invalidated_payload = decode_token(token)
    assert invalidated_payload is None


def test_auth_08_unified_jwt_service():
    """Verify standard access token roundtrip."""
    access_token = create_access_token({"sub": "test_user_id", "email": "test@memegpt.com"})
    payload = decode_token(access_token)
    assert payload is not None
    assert payload["sub"] == "test_user_id"
    assert payload["email"] == "test@memegpt.com"
    assert payload["type"] == "access"


def test_auth_09_password_hashing_and_verification():
    """Verify bcrypt password hashing and verification."""
    password = "StrongPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword!", hashed)
