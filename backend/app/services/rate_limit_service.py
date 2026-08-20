"""Rate Limiting Service for MemeGPT.
Specification: 07_APIs/Rate_Limiting.md
"""

import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple


def get_rate_limit_tier(api_key: Optional[str] = None) -> str:
    """Resolve rate limit tier ('free', 'developer', or 'pro') based on API key."""
    if not api_key:
        return "free"
    
    key_clean = api_key.strip().lower()
    if "admin" in key_clean or "pro" in key_clean:
        return "pro"
    elif "test" in key_clean or "dev" in key_clean or key_clean.startswith("mgpt_"):
        return "developer"
    
    return "developer"


def get_rate_limit_for_request(path: str, api_key: Optional[str] = None) -> Tuple[str, int, int]:
    """Determine rate limit tier, request limit per minute, and window seconds for a specific path.
    
    Returns:
        (tier: str, limit: int, window_seconds: int)
    """
    tier = get_rate_limit_tier(api_key)
    is_search = path.startswith("/api/v1/search") or path.startswith("/search")

    if tier == "pro":
        limit = 500 if is_search else 1000
    elif tier == "developer":
        limit = 100 if is_search else 300
    else:  # free
        limit = 30 if is_search else 60

    return tier, limit, 60


def get_rate_limit_tiers_catalog() -> List[Dict[str, Any]]:
    """Return catalog of rate limit tiers specified in 07_APIs/Rate_Limiting.md."""
    return [
        {
            "tier": "Free",
            "auth": "None (IP-based)",
            "scope": "Per IP address",
            "search_limit": 30,
            "general_limit": 60,
            "window": "60s (sliding window)",
            "header": "Client IP",
        },
        {
            "tier": "Developer",
            "auth": "API key (Free tier)",
            "scope": "Per API key",
            "search_limit": 100,
            "general_limit": 300,
            "window": "60s (sliding window)",
            "header": "X-API-Key",
        },
        {
            "tier": "Pro",
            "auth": "Paid API key / Admin",
            "scope": "Per API key",
            "search_limit": 500,
            "general_limit": 1000,
            "window": "60s (sliding window)",
            "header": "X-API-Key",
        },
    ]


def simulate_token_bucket(
    timestamps: List[float],
    current_time: float,
    limit: int,
    window_seconds: int = 60
) -> Dict[str, Any]:
    """Simulate token bucket sliding log check matching documentation algorithm."""
    window_start = current_time - window_seconds
    valid_timestamps = [t for t in timestamps if t >= window_start]
    
    allowed = len(valid_timestamps) < limit
    remaining = max(0, limit - len(valid_timestamps) - (1 if allowed else 0))
    
    retry_after = 0
    if not allowed and valid_timestamps:
        oldest = valid_timestamps[0]
        retry_after = max(1, int(window_seconds - (current_time - oldest)))
        
    reset_epoch = int(current_time + (retry_after if retry_after > 0 else window_seconds))

    return {
        "allowed": allowed,
        "count_in_window": len(valid_timestamps),
        "limit": limit,
        "remaining": remaining,
        "retry_after": retry_after,
        "reset_epoch": reset_epoch,
        "window": f"{window_seconds}s",
    }


def get_rate_limiting_best_practices() -> List[str]:
    """Return client best practices from Rate_Limiting.md."""
    return [
        "Check X-RateLimit-Remaining before each request",
        "Implement exponential backoff on 429 responses",
        "Cache results client-side to reduce API calls",
        "Batch requests where possible",
        "Use Retry-After header to know exactly when to retry",
    ]
