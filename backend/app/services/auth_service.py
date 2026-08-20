"""API Authentication service for MemeGPT — roadmap, tier matrices, token helpers, and key validators.
Specification: 07_APIs/Authentication.md
"""

import re
from typing import Any
from app.core.auth import (
    generate_api_key,
    hash_api_key,
    create_access_token,
    create_refresh_token,
    verify_jwt_token,
    get_jwt_cookie_settings,
    AuthContext,
)


def get_auth_roadmap() -> dict[str, Any]:
    """Return the 3-phase authentication roadmap from 07_APIs/Authentication.md."""
    return {
        "roadmap": [
            {
                "phase": 1,
                "name": "Anonymous Access (MVP)",
                "timeline": "2026-01 to 2026-04",
                "status": "active",
                "auth_type": "None",
                "rate_limiting": "IP address rate limiting (60 req/min)",
                "rationale": "Zero friction for users. Maximum adoption.",
            },
            {
                "phase": 2,
                "name": "API Key Authentication",
                "timeline": "2026-05 to 2026-08",
                "status": "ready",
                "auth_type": "X-API-Key header (SHA-256 stored)",
                "key_format": "mgpt_live_<32-char hex>",
                "rate_limiting": "By tier: Free (120/min), Pro (300/min), Internal (1000/min)",
            },
            {
                "phase": 3,
                "name": "User Accounts (OAuth + JWT)",
                "timeline": "2026-09 to 2026-12",
                "status": "planned",
                "auth_type": "OAuth 2.0 (Google, Supabase, NextAuth) + JWT sessions",
                "tokens": "15-minute access token, 7-day refresh token in httpOnly cookie",
            },
        ],
    }


def get_auth_tiers_matrix() -> list[dict[str, Any]]:
    """Return authentication tiers, rate limits, and permission scopes."""
    return [
        {
            "tier": "anonymous",
            "rate_limit_per_min": 60,
            "requires_key": False,
            "features": ["Public Search", "Meme Detail", "Trending", "Feedback"],
        },
        {
            "tier": "free",
            "rate_limit_per_min": 120,
            "requires_key": True,
            "features": ["Search API", "Download API", "High-throughput queries"],
        },
        {
            "tier": "pro",
            "rate_limit_per_min": 300,
            "requires_key": True,
            "features": ["Multi-modal search", "Priority queue", "Custom collections", "300 req/min"],
        },
        {
            "tier": "internal",
            "rate_limit_per_min": 1000,
            "requires_key": True,
            "features": ["Admin operations", "Batch indexing", "Unlimited diagnostics"],
        },
    ]


def validate_api_key_format(key: str) -> bool:
    """Validate if API key format matches mgpt_live_... / mgpt_test_... or legacy pk_live_..."""
    if not key or not isinstance(key, str):
        return False
    
    # mgpt_live_<32 hex> or mgpt_test_<32 hex> or legacy pk_live_<32 hex>
    pattern = r"^(mgpt_(live|test)_[a-f0-9]{32}|pk_(live|test)_[a-f0-9]{32}|memegpt_[a-z0-9_]+)$"
    return bool(re.match(pattern, key.strip()))


def create_user_session_tokens(user_id: str, email: str, plan: str = "free") -> dict[str, Any]:
    """Issue JWT access and refresh token pair for a user session."""
    payload = {"sub": user_id, "email": email, "plan": plan}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 15 * 60,  # 15 minutes in seconds
        "cookie_settings": get_jwt_cookie_settings(),
    }


def get_oauth_providers_catalog() -> list[dict[str, str]]:
    """Return supported OAuth providers for Phase 3."""
    return [
        {"provider": "google", "flow": "Authorization Code + PKCE", "library": "NextAuth / Supabase"},
        {"provider": "github", "flow": "Authorization Code", "library": "NextAuth / Supabase"},
    ]
