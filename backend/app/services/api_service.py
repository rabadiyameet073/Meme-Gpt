"""API Overview service for MemeGPT — endpoints, environments, formats, headers, and rate limits.
Specification: 07_APIs/API_Overview.md
"""

from typing import Any


def get_api_environments() -> dict[str, str]:
    """Return environment URLs from 07_APIs/API_Overview.md."""
    return {
        "production": "https://api.memegpt.com",
        "staging": "https://api-staging.memegpt.com",
        "development": "http://localhost:8000",
    }


def get_api_overview_catalog() -> dict[str, Any]:
    """Return complete endpoint catalog from 07_APIs/API_Overview.md."""
    return {
        "version": "v1",
        "prefix": "/api/v1",
        "environments": get_api_environments(),
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/v1/search",
                "description": "AI-powered meme search",
                "rate_limit": "30/min",
                "docs": "Search_API.md",
            },
            {
                "method": "GET",
                "path": "/api/v1/memes/{slug}",
                "description": "Meme detail by slug",
                "rate_limit": "60/min",
                "docs": "Meme_API.md",
            },
            {
                "method": "GET",
                "path": "/api/v1/memes/{slug}/download",
                "description": "Download meme file",
                "rate_limit": "60/min",
                "docs": "Meme_API.md",
            },
            {
                "method": "GET",
                "path": "/api/v1/trending",
                "description": "Trending memes",
                "rate_limit": "60/min",
                "docs": "Meme_API.md",
            },
            {
                "method": "POST",
                "path": "/api/v1/feedback",
                "description": "Record user interaction",
                "rate_limit": "120/min",
                "docs": "Meme_API.md",
            },
            {
                "method": "GET",
                "path": "/health",
                "description": "Service health check",
                "rate_limit": "None",
                "docs": "Health_Check.md",
            },
        ],
    }


def format_api_success_response(data: Any) -> dict[str, Any]:
    """Format standardized API success response envelope."""
    return {
        "success": True,
        "data": data,
    }


def format_api_error_response(error_code: str, message: str) -> dict[str, Any]:
    """Format standardized API error response envelope."""
    return {
        "success": False,
        "error": error_code,
        "message": message,
    }


def get_http_status_codes_catalog() -> list[dict[str, Any]]:
    """Return HTTP status codes used in MemeGPT from 07_APIs/API_Overview.md."""
    return [
        {"status": 200, "description": "Success", "when": "Success"},
        {"status": 301, "description": "Moved Permanently", "when": "Download redirect to CDN"},
        {"status": 400, "description": "Bad Request", "when": "Invalid request"},
        {"status": 404, "description": "Not Found", "when": "Meme not found"},
        {"status": 422, "description": "Unprocessable Entity", "when": "Validation error"},
        {"status": 429, "description": "Too Many Requests", "when": "Rate limit exceeded"},
        {"status": 500, "description": "Internal Server Error", "when": "Internal server error"},
        {"status": 503, "description": "Service Unavailable", "when": "Service unavailable"},
    ]


def get_endpoint_rate_limits() -> dict[str, int]:
    """Return request rate limits per minute by endpoint."""
    return {
        "/api/v1/search": 30,
        "/api/v1/memes/{slug}": 60,
        "/api/v1/memes/{slug}/download": 60,
        "/api/v1/trending": 60,
        "/api/v1/feedback": 120,
    }


def get_api_section_manifest() -> dict[str, Any]:
    """Return Section 07 APIs documentation manifest from 07_APIs/README.md."""
    return {
        "section": "07_APIs",
        "title": "APIs",
        "description": "REST API documentation for MemeGPT.",
        "documents": [
            {
                "name": "API_Overview.md",
                "path": "07_APIs/API_Overview.md",
                "description": "API design, authentication, versioning",
            },
            {
                "name": "Search_API.md",
                "path": "07_APIs/Search_API.md",
                "description": "POST /api/v1/search — core search endpoint",
            },
            {
                "name": "Meme_API.md",
                "path": "07_APIs/Meme_API.md",
                "description": "GET /api/v1/memes/{slug} — meme detail",
            },
            {
                "name": "Trending_API.md",
                "path": "07_APIs/Trending_API.md",
                "description": "GET /api/v1/trending — trending memes",
            },
            {
                "name": "Feedback_API.md",
                "path": "07_APIs/Feedback_API.md",
                "description": "POST /api/v1/feedback — user interaction tracking",
            },
            {
                "name": "Rate_Limiting.md",
                "path": "07_APIs/Rate_Limiting.md",
                "description": "Rate limiting policy, implementation, headers",
            },
            {
                "name": "Authentication.md",
                "path": "07_APIs/Authentication.md",
                "description": "API authentication, API keys, and JWT sessions",
            },
            {
                "name": "Webhooks.md",
                "path": "07_APIs/Webhooks.md",
                "description": "Webhook notifications and integrations",
            },
            {
                "name": "README.md",
                "path": "07_APIs/README.md",
                "description": "Section 07 navigation and table of contents",
            },
        ],
        "previous_section": "06_Database",
        "next_section": "08_Features",
    }


def verify_api_routes_registration(app: Any) -> dict[str, Any]:
    """Verify that all core REST API endpoints defined in Section 07 documentation are mounted."""
    registered_paths = set()
    for route in getattr(app, "routes", []):
        if hasattr(route, "path"):
            registered_paths.add(route.path)

    expected_routes = [
        "/api/v1/search",
        "/api/v1/memes",
        "/api/v1/memes/{slug_or_id}",
        "/api/v1/memes/{slug_or_id}/download",
        "/api/v1/trending",
        "/api/v1/feedback",
        "/health",
    ]

    coverage = {}
    for r in expected_routes:
        # Path matching considering route patterns
        is_mounted = any(r == p or (r.replace("{slug_or_id}", "{slug}") == p) for p in registered_paths)
        coverage[r] = is_mounted

    all_mounted = all(coverage.values())
    return {
        "all_mounted": all_mounted,
        "total_expected": len(expected_routes),
        "total_registered_routes": len(registered_paths),
        "coverage": coverage,
    }
