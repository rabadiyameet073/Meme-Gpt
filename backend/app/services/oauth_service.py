"""OAuth provider integration for Google and GitHub."""
import httpx
import logging
from typing import Optional, Dict

from app.config import settings

logger = logging.getLogger("memegpt.oauth")

# Google OAuth
GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = getattr(settings, "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")

# GitHub OAuth
GITHUB_CLIENT_ID = getattr(settings, "GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = getattr(settings, "GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = getattr(settings, "GITHUB_REDIRECT_URI", "http://localhost:8000/api/v1/auth/github/callback")


def _get_google_client_id() -> str:
    return getattr(settings, "GOOGLE_CLIENT_ID", GOOGLE_CLIENT_ID) or GOOGLE_CLIENT_ID

def _get_google_client_secret() -> str:
    return getattr(settings, "GOOGLE_CLIENT_SECRET", GOOGLE_CLIENT_SECRET) or GOOGLE_CLIENT_SECRET

def _get_google_redirect_uri() -> str:
    return getattr(settings, "GOOGLE_REDIRECT_URI", GOOGLE_REDIRECT_URI) or GOOGLE_REDIRECT_URI

def _get_github_client_id() -> str:
    return getattr(settings, "GITHUB_CLIENT_ID", GITHUB_CLIENT_ID) or GITHUB_CLIENT_ID

def _get_github_client_secret() -> str:
    return getattr(settings, "GITHUB_CLIENT_SECRET", GITHUB_CLIENT_SECRET) or GITHUB_CLIENT_SECRET

def _get_github_redirect_uri() -> str:
    return getattr(settings, "GITHUB_REDIRECT_URI", GITHUB_REDIRECT_URI) or GITHUB_REDIRECT_URI


def get_google_auth_url() -> str:
    """Generate Google OAuth consent URL."""
    return (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={_get_google_client_id()}&"
        f"redirect_uri={_get_google_redirect_uri()}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline"
    )


async def exchange_google_code(code: str) -> Optional[Dict]:
    """Exchange authorization code for Google user info."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": _get_google_client_id(),
            "client_secret": _get_google_client_secret(),
            "redirect_uri": _get_google_redirect_uri(),
            "grant_type": "authorization_code",
        })
        if token_resp.status_code != 200:
            logger.error(f"Google token exchange failed: {token_resp.text}")
            return None

        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            return None

        user_info = user_resp.json()
        return {
            "provider": "google",
            "oauth_id": user_info["id"],
            "email": user_info["email"],
            "name": user_info.get("name", ""),
            "avatar_url": user_info.get("picture", ""),
        }


def get_github_auth_url() -> str:
    """Generate GitHub OAuth URL."""
    return (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={_get_github_client_id()}&"
        f"redirect_uri={_get_github_redirect_uri()}&"
        f"scope=user:email"
    )


async def exchange_github_code(code: str) -> Optional[Dict]:
    """Exchange authorization code for GitHub user info."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": _get_github_client_id(),
                "client_secret": _get_github_client_secret(),
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        tokens = token_resp.json()
        access_token = tokens.get("access_token")
        if not access_token:
            return None

        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_resp.json()

        email_resp = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        emails = email_resp.json() if email_resp.status_code == 200 else []
        primary_email = next((e["email"] for e in emails if isinstance(e, dict) and e.get("primary")), user_info.get("email", ""))

        return {
            "provider": "github",
            "oauth_id": str(user_info["id"]),
            "email": primary_email or user_info.get("email", ""),
            "name": user_info.get("name") or user_info.get("login", ""),
            "avatar_url": user_info.get("avatar_url", ""),
        }
