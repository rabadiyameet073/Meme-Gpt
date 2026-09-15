"""
Comprehensive tests for Guide 04 — User Authentication & OAuth
Tests Google/GitHub OAuth URLs, callbacks, JWT tokens, email/password registration,
login, token refresh, and /auth/me profile endpoint.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, get_db, User
from app.services.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

init_db()
client = TestClient(app)


def test_password_hashing():
    """Verify bcrypt password hashing and verification."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_access_and_refresh_tokens():
    """Verify JWT access and refresh token creation, decoding, and type separation."""
    access_token = create_access_token({"sub": "user_42", "email": "tester@memegpt.com"})
    refresh_token = create_refresh_token({"sub": "user_42"})

    decoded_access = decode_token(access_token)
    assert decoded_access is not None
    assert decoded_access["sub"] == "user_42"
    assert decoded_access["type"] == "access"
    assert "exp" in decoded_access

    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh is not None
    assert decoded_refresh["sub"] == "user_42"
    assert decoded_refresh["type"] == "refresh"


def test_google_login_url():
    """GET /api/v1/auth/google/login returns Google OAuth consent URL."""
    resp = client.get("/api/v1/auth/google/login")
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert "accounts.google.com" in data["url"]
    assert "client_id=" in data["url"]
    assert "redirect_uri=" in data["url"]
    assert "scope=openid" in data["url"]


def test_github_login_url():
    """GET /api/v1/auth/github/login returns GitHub OAuth consent URL."""
    resp = client.get("/api/v1/auth/github/login")
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert "github.com/login/oauth/authorize" in data["url"]
    assert "client_id=" in data["url"]
    assert "scope=user:email" in data["url"]


def test_user_registration_flow():
    """POST /api/v1/auth/register creates user, sets cookies, and returns tokens."""
    unique_email = "reg_test_user@memegpt.com"
    with next(get_db()) as db:
        db.query(User).filter(User.email == unique_email).delete()
        db.commit()

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "Password1234!",
            "name": "Registration Tester",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_email
    assert data["user"]["name"] == "Registration Tester"
    assert data["user"]["plan"] == "free"

    # Duplicate registration should fail
    dup_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "AnotherPassword123!",
            "name": "Duplicate User",
        },
    )
    assert dup_resp.status_code == 400
    assert "already registered" in dup_resp.json()["detail"].lower()


def test_user_login_flow():
    """POST /api/v1/auth/login authenticates with correct credentials and rejects incorrect ones."""
    email = "login_test_user@memegpt.com"
    password = "CorrectHorseBatteryStaple!"

    with next(get_db()) as db:
        existing = db.query(User).filter(User.email == email).first()
        if not existing:
            u = User(
                email=email,
                name="Login Tester",
                hashed_password=hash_password(password),
                plan="free",
            )
            db.add(u)
            db.commit()

    # Successful login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == email

    # Invalid password
    bad_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!"},
    )
    assert bad_resp.status_code == 401
    assert "invalid" in bad_resp.json()["detail"].lower()

    # Unknown email
    unknown_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent_person_xyz@memegpt.com", "password": password},
    )
    assert unknown_resp.status_code == 401


def test_auth_me_protection_and_profile():
    """
    Test GET /api/v1/auth/me:
    1. Without token -> 401 Unauthorized
    2. With invalid token -> 401 Unauthorized
    3. With refresh token instead of access token -> 401 Unauthorized
    4. With valid access token -> 200 OK + user profile
    """
    # 1. Without token
    no_token_resp = client.get("/api/v1/auth/me")
    assert no_token_resp.status_code == 401

    # 2. With garbage token
    bad_token_resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt"})
    assert bad_token_resp.status_code == 401

    # Create test user in DB
    email = "profile_check@memegpt.com"
    user_id = ""
    with next(get_db()) as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name="Profile Checker", plan="pro")
            db.add(user)
            db.commit()
            db.refresh(user)
        user_id = user.id

    # 3. With refresh token
    refresh_token = create_refresh_token({"sub": user_id})
    refresh_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_resp.status_code == 401

    # 4. With valid access token
    access_token = create_access_token({"sub": user_id, "email": email})
    ok_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert ok_resp.status_code == 200
    user_data = ok_resp.json()["user"]
    assert user_data["id"] == user_id
    assert user_data["email"] == email


def test_token_refresh_endpoint():
    """POST /api/v1/auth/refresh takes valid refresh token and issues new access token."""
    email = "refresh_me@memegpt.com"
    user_id = ""
    with next(get_db()) as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name="Refresh Tester")
            db.add(user)
            db.commit()
            db.refresh(user)
        user_id = user.id

    refresh_token = create_refresh_token({"sub": user_id})

    resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    new_decoded = decode_token(data["access_token"])
    assert new_decoded["sub"] == user_id
    assert new_decoded["type"] == "access"


def test_update_profile_and_preferences():
    """PUT /api/v1/auth/me updates profile fields for authenticated user."""
    email = "update_pref_user@memegpt.com"
    user_id = ""
    with next(get_db()) as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name="Before Update")
            db.add(user)
            db.commit()
            db.refresh(user)
        user_id = user.id

    token = create_access_token({"sub": user_id, "email": email})

    update_resp = client.put(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "After Update",
            "preferred_format": "mp4",
            "theme": "light",
            "nsfw_enabled": True,
            "preferences": {"custom_tag": "work_memes"},
        },
    )
    assert update_resp.status_code == 200
    updated_user = update_resp.json()["user"]
    assert updated_user["name"] == "After Update"
    assert updated_user["preferred_format"] == "mp4"
    assert updated_user["theme"] == "light"
    assert updated_user["nsfw_enabled"] is True
    assert updated_user["preferences"].get("custom_tag") == "work_memes"


@pytest.mark.asyncio
async def test_google_oauth_callback_flow():
    """Mock Google OAuth callback and verify user creation & token generation."""
    mock_user_info = {
        "provider": "google",
        "oauth_id": "google_uid_999888",
        "email": "google_test_user@gmail.com",
        "name": "Google User",
        "avatar_url": "https://lh3.googleusercontent.com/avatar.jpg",
    }

    with patch("app.api.v1.auth.exchange_google_code", new=AsyncMock(return_value=mock_user_info)):
        resp = client.get("/api/v1/auth/google/callback?code=mock_google_auth_code_123")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "google_test_user@gmail.com"
        assert data["user"]["oauth_provider"] == "google"


@pytest.mark.asyncio
async def test_github_oauth_callback_flow():
    """Mock GitHub OAuth callback and verify user creation & token generation."""
    mock_user_info = {
        "provider": "github",
        "oauth_id": "github_uid_555666",
        "email": "octocat@github.com",
        "name": "The Octocat",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231",
    }

    with patch("app.api.v1.auth.exchange_github_code", new=AsyncMock(return_value=mock_user_info)):
        resp = client.get("/api/v1/auth/github/callback?code=mock_github_auth_code_456")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "octocat@github.com"
        assert data["user"]["oauth_provider"] == "github"


def test_logout_endpoint():
    """POST /api/v1/auth/logout clears auth cookies."""
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
