"""Security Section Manifest and Global Subsystem Health Service for MemeGPT.
Specification: 11_Security/README.md

Covers:
- Section 11 Documentation Manifest & Directory Mapping
- Consolidated Security Posture Summary across all Security Domains
- Live Subsystem Health Diagnostics (API Security, Data Privacy, Input Validation, Rate Limiting)
- Section Navigation (Previous: 10_Testing, Next: 12_Deployment)
"""

from typing import Any, Dict, List
from app.services.api_security_service import evaluate_security_compliance
from app.services.data_privacy_service import evaluate_privacy_compliance
from app.services.input_validation_service import evaluate_input_validation_health
from app.services.rate_limiting_security_service import evaluate_rate_limiting_security_health


# ── 1. Section 11 Documentation Manifest ───────────────────────────────────────

SECURITY_SECTION_MANIFEST = [
    {
        "file": "API_Security.md",
        "title": "API Security",
        "description": "HTTPS enforcement, CORS whitelist policy, security headers, secret management matrix & rules, and pre-launch security checklist.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/security",
    },
    {
        "file": "Data_Privacy.md",
        "title": "Data Privacy & GDPR",
        "description": "GDPR compliance, data subject access/erasure endpoints, cookie policy, 6-category data classification, and third-party DPAs.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/privacy",
    },
    {
        "file": "Input_Validation.md",
        "title": "Input Validation & Threat Defense",
        "description": "6 attack vectors & engineering defenses (SQLi, XSS, Prompt Injection, ReDoS, Buffer Overflow, SSRF), HTML sanitization, and prompt injection defense.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/validation",
    },
    {
        "file": "Rate_Limiting_Security.md",
        "title": "Rate Limiting Security",
        "description": "Token bucket sliding window algorithm, 5 per-endpoint rate limit policies, 4 DDoS mitigation layers, and rate limiting headers.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/rate-limiting",
    },
    {
        "file": "Security_Overview.md",
        "title": "Security Overview & Threat Model",
        "description": "Comprehensive threat modeling, STRIDE analysis, defense-in-depth architecture, and incident response runbooks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/security",
    },
    {
        "file": "README.md",
        "title": "Security Section Manifest",
        "description": "Index, section navigation, unified security posture summary, and global diagnostic health checks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/security",
    },
]


def get_security_section_manifest() -> Dict[str, Any]:
    """Return Section 11 documentation inventory and metadata."""
    completed = sum(1 for doc in SECURITY_SECTION_MANIFEST if doc["status"] == "COMPLETED")
    return {
        "section_id": "11",
        "section_name": "Security",
        "total_documents": len(SECURITY_SECTION_MANIFEST),
        "completed_documents": completed,
        "completion_percentage": round((completed / len(SECURITY_SECTION_MANIFEST)) * 100, 1),
        "navigation": {
            "previous_section": "10_Testing",
            "previous_readme": "md files/documentation/10_Testing/README.md",
            "next_section": "12_Deployment",
            "next_readme": "md files/documentation/12_Deployment/README.md",
        },
        "documents": SECURITY_SECTION_MANIFEST,
    }


# ── 2. Consolidated Security Posture Summary ───────────────────────────────────

def get_security_posture_summary() -> Dict[str, Any]:
    """Return unified security posture across all engineering defense layers."""
    return {
        "transport_security": {
            "protocol": "TLS 1.3 / HTTPS",
            "hsts": "max-age=31536000; includeSubDomains",
            "redirect": "301 Permanent Redirect in production",
        },
        "browser_security": {
            "cors_policy": "Strict origin whitelist (no wildcard '*' in prod)",
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "x_xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
        },
        "application_security": {
            "input_validation": "Pydantic max_length=2000 & regex enums",
            "html_sanitization": "Tag stripping, JS protocol removal, null byte deletion",
            "prompt_injection_defense": "Structured JSON output parsing; data never executed as code",
        },
        "data_privacy": {
            "gdpr_compliance": "Article 15 (Access), Article 17 (Erasure), Article 20 (Portability)",
            "cookies": "0 third-party, 0 advertising, 0 analytics",
            "retention": "90-day automated purge of internal interaction logs",
        },
        "ddos_and_rate_limiting": {
            "algorithm": "Redis token bucket / sliding window",
            "search_quota": "30 req/min",
            "trending_quota": "60 req/min",
            "feedback_quota": "120 req/min",
            "health_check": "Exempt (unlimited)",
        },
        "secret_management": {
            "storage": "Platform environment variables (Vercel/Railway)",
            "repo_protection": ".env strictly gitignored",
            "logging_rule": "Secrets and raw authorization tokens redacted",
            "response_rule": "API keys masked (e.g. mgpt_****n4o5p6)",
        },
    }


# ── 3. Subsystem Health Diagnostics ────────────────────────────────────────────

def get_security_subsystem_health() -> Dict[str, Any]:
    """Execute live diagnostic audits across all security subsystems."""
    api_sec = evaluate_security_compliance()
    privacy = evaluate_privacy_compliance()
    validation = evaluate_input_validation_health()
    rate_lim = evaluate_rate_limiting_security_health()

    all_healthy = (
        api_sec.get("status") == "COMPLIANT"
        and privacy.get("status") == "COMPLIANT"
        and validation.get("status") == "HEALTHY"
        and rate_lim.get("status") == "COMPLIANT"
    )

    return {
        "status": "HEALTHY" if all_healthy else "DEGRADED",
        "subsystems": {
            "api_security": {
                "status": api_sec.get("status"),
                "compliance_score": api_sec.get("compliance_percentage"),
            },
            "data_privacy": {
                "status": privacy.get("status"),
                "compliance_score": privacy.get("compliance_score"),
            },
            "input_validation": {
                "status": validation.get("status"),
                "xss_active": validation.get("xss_sanitization_active"),
                "llm_fallback_active": validation.get("llm_json_fallback_active"),
            },
            "rate_limiting": {
                "status": rate_lim.get("status"),
                "health_exempt": rate_lim.get("health_check_exempt"),
                "search_limited": rate_lim.get("ai_search_protection_active"),
            },
        },
    }
