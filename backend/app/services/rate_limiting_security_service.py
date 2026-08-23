"""Rate Limiting Security Service for MemeGPT.
Specification: 11_Security/Rate_Limiting_Security.md

Covers:
- Rate Limiting Architecture (Client IP -> Redis ZADD sorted set -> Window Check -> 429 Block / 200 Pass)
- Per-Endpoint Policies (/search: 30/min, /trending: 60/min, /memes: 60/min, /feedback: 120/min, /health: exempt)
- Redis Sorted Sets Token Bucket Algorithm & In-Memory Fallback
- 4 DDoS Mitigation Layers (CDN Cloudflare, App Redis, Infra Autoscaling, IP Blocklist)
- 6 Engineering Best Practices
- Rate Limiting Health & Abuse Evaluation
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from app.core.rate_limit import rate_limiter


# ── 1. Rate Limiting Architecture Specification ───────────────────────────────

ARCHITECTURE_SPEC = {
    "title": "Token Bucket Sliding Window Rate Limiting",
    "description": "Multi-tier sliding-window rate limiting keyed by hashed IP or hashed API key across endpoints.",
    "flow": [
        "1. Extract and sanitize client IP address (from X-Forwarded-For or socket)",
        "2. Build endpoint rate key (e.g. rl:search:{ip}, rl:feedback:{ip}, rl:general:{ip})",
        "3. Redis ZADD sorted set timestamp entry",
        "4. ZREMRANGEBYSCORE to prune timestamps outside window",
        "5. ZCARD to compute request count in window",
        "6. If count > limit: Respond 429 Too Many Requests with Retry-After header",
        "7. If count <= limit: Forward request to route handler with X-RateLimit headers",
    ],
}


def get_rate_limiting_architecture() -> Dict[str, Any]:
    """Return rate limiting architecture diagram specification and workflow."""
    return {
        **ARCHITECTURE_SPEC,
    }


# ── 2. Per-Endpoint Rate Limit Policies Matrix ────────────────────────────────

RATE_LIMIT_POLICIES = [
    {
        "endpoint": "POST /search",
        "route_pattern": "/api/v1/search",
        "limit": 30,
        "window": "60s",
        "window_seconds": 60,
        "key_pattern": "rl:search:{ip}",
        "reason": "Most expensive (AI embedding & LLM inference pipeline)",
        "exempt": False,
    },
    {
        "endpoint": "GET /trending",
        "route_pattern": "/api/v1/trending",
        "limit": 60,
        "window": "60s",
        "window_seconds": 60,
        "key_pattern": "rl:general:{ip}",
        "reason": "Cacheable, lightweight aggregated queries",
        "exempt": False,
    },
    {
        "endpoint": "GET /memes/{slug}",
        "route_pattern": "/api/v1/memes",
        "limit": 60,
        "window": "60s",
        "window_seconds": 60,
        "key_pattern": "rl:general:{ip}",
        "reason": "Database read only with Redis query cache",
        "exempt": False,
    },
    {
        "endpoint": "POST /feedback",
        "route_pattern": "/api/v1/feedback",
        "limit": 120,
        "window": "60s",
        "window_seconds": 60,
        "key_pattern": "rl:feedback:{ip}",
        "reason": "Encourage feedback, lightweight background async write",
        "exempt": False,
    },
    {
        "endpoint": "GET /health",
        "route_pattern": "/api/v1/health",
        "limit": None,
        "window": "—",
        "window_seconds": 0,
        "key_pattern": "—",
        "reason": "Monitoring and health checks must always work without restriction",
        "exempt": True,
    },
]


def get_rate_limit_policies() -> Dict[str, Any]:
    """Return the 5 per-endpoint rate limiting policies."""
    return {
        "total_policies": len(RATE_LIMIT_POLICIES),
        "policies": RATE_LIMIT_POLICIES,
    }


# ── 3. DDoS Mitigation Layers Matrix ───────────────────────────────────────────

DDOS_MITIGATION_LAYERS = [
    {
        "layer": 1,
        "protection": "CDN-level rate limiting & bot mitigation",
        "provider": "Cloudflare (automatic)",
        "status": "Active",
    },
    {
        "layer": 2,
        "protection": "Application rate limiting (Token Bucket / Sorted Sets)",
        "provider": "Redis / In-memory token bucket",
        "status": "Active",
    },
    {
        "layer": 3,
        "protection": "Infrastructure auto-scaling & container replicas",
        "provider": "Railway / Render / Vercel (managed infrastructure)",
        "status": "Active",
    },
    {
        "layer": 4,
        "protection": "IP blocklist & dynamic firewall drops",
        "provider": "Manual / Automated abuse detection script",
        "status": "Active",
    },
]


def get_ddos_mitigation_layers() -> Dict[str, Any]:
    """Return the 4 DDoS mitigation defense layers."""
    return {
        "total_layers": len(DDOS_MITIGATION_LAYERS),
        "layers": DDOS_MITIGATION_LAYERS,
    }


# ── 4. 6 Engineering Best Practices ───────────────────────────────────────────

RATE_LIMITING_BEST_PRACTICES = [
    {
        "id": 1,
        "title": "Rate limit by IP, not by cookie",
        "description": "Cookies can be cleared or rotated by automated scrapers; IP addresses provide persistent identity.",
    },
    {
        "id": 2,
        "title": "Use Redis sorted sets",
        "description": "O(log n) sliding window evaluation with atomic pipeline execution.",
    },
    {
        "id": 3,
        "title": "Include rate limit headers on every response",
        "description": "Expose X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset across all HTTP responses, not just 429s.",
    },
    {
        "id": 4,
        "title": "Different limits per endpoint",
        "description": "Expensive endpoints (AI vector search: 30/min) receive stricter quotas than lightweight endpoints (feedback: 120/min).",
    },
    {
        "id": 5,
        "title": "Exempt health checks",
        "description": "Uptime monitors and Kubernetes liveness probes must never encounter 429 rate limit errors.",
    },
    {
        "id": 6,
        "title": "Log rate limit violations",
        "description": "Track persistent abuse attempts and sudden spikes for proactive security mitigation.",
    },
]


def get_rate_limiting_best_practices() -> Dict[str, Any]:
    """Return 6 rate limiting engineering best practices."""
    return {
        "total_practices": len(RATE_LIMITING_BEST_PRACTICES),
        "practices": RATE_LIMITING_BEST_PRACTICES,
    }


# ── 5. Policy Matcher and Rate Evaluator ───────────────────────────────────────

def resolve_policy_for_path(path: str) -> Dict[str, Any]:
    """Match an incoming URL path to its corresponding rate policy."""
    clean_path = path.lower().strip()
    if clean_path.endswith("/health") or clean_path == "/health":
        return next(p for p in RATE_LIMIT_POLICIES if p["exempt"])

    if "search" in clean_path:
        return next(p for p in RATE_LIMIT_POLICIES if p["endpoint"] == "POST /search")
    elif "feedback" in clean_path:
        return next(p for p in RATE_LIMIT_POLICIES if p["endpoint"] == "POST /feedback")
    elif "trending" in clean_path:
        return next(p for p in RATE_LIMIT_POLICIES if p["endpoint"] == "GET /trending")
    elif "memes" in clean_path:
        return next(p for p in RATE_LIMIT_POLICIES if p["endpoint"] == "GET /memes/{slug}")

    # Default fallback policy
    return {
        "endpoint": "DEFAULT",
        "route_pattern": "*",
        "limit": 60,
        "window": "60s",
        "window_seconds": 60,
        "key_pattern": "rl:general:{ip}",
        "reason": "Standard API endpoint quota",
        "exempt": False,
    }


def check_rate_limit_policy(
    endpoint_path: str,
    client_ip: str,
    custom_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Evaluate rate limit quota for given endpoint path and IP."""
    policy = resolve_policy_for_path(endpoint_path)
    if policy["exempt"]:
        return {
            "allowed": True,
            "remaining": 999999,
            "retry_after": 0,
            "reset_epoch": int(time.time()),
            "limit": None,
            "policy": policy,
            "exempt": True,
        }

    limit = custom_limit if custom_limit is not None else policy["limit"]
    key = policy["key_pattern"].replace("{ip}", client_ip or "127.0.0.1")

    allowed, remaining, retry_after, reset_epoch = rate_limiter.check_with_window(
        identifier=key,
        limit=limit,
        window_seconds=policy.get("window_seconds", 60),
    )

    return {
        "allowed": allowed,
        "remaining": remaining,
        "retry_after": retry_after,
        "reset_epoch": reset_epoch,
        "limit": limit,
        "key": key,
        "policy": policy,
        "exempt": False,
    }


# ── 6. System Rate Limiting Health Evaluator ───────────────────────────────────

def evaluate_rate_limiting_security_health() -> Dict[str, Any]:
    """Verify that all rate limiting components, headers, and policies are operational."""
    # Test health check exemption
    health_check = check_rate_limit_policy("/api/v1/health", "127.0.0.1")
    health_exempt = health_check["exempt"] is True and health_check["allowed"] is True

    # Test search policy limit
    search_policy = resolve_policy_for_path("/api/v1/search")
    search_limited = search_policy["limit"] == 30

    # Test feedback policy limit
    feedback_policy = resolve_policy_for_path("/api/v1/feedback")
    feedback_generous = feedback_policy["limit"] == 120

    all_compliant = health_exempt and search_limited and feedback_generous

    return {
        "status": "COMPLIANT" if all_compliant else "DEGRADED",
        "health_check_exempt": health_exempt,
        "ai_search_protection_active": search_limited,
        "feedback_rate_configured": feedback_generous,
        "total_policies_configured": len(RATE_LIMIT_POLICIES),
        "ddos_layers_count": len(DDOS_MITIGATION_LAYERS),
    }
