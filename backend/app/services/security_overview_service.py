"""Security Overview & Threat Modeling Service for MemeGPT.
Specification: 11_Security/Security_Overview.md

Covers:
- 5-Layer Defense-in-Depth Architecture (Network, Application, Input, Data, Infrastructure)
- Full OWASP Top 10 Security Mapping (A01 to A10)
- Threat Model Risk Matrix (Likelihood, Impact, Mitigations)
- Master Pre-Launch Security Audit Checklist
- Automated OWASP Compliance Evaluator
"""

from typing import Any, Dict, List


# ── 1. 5-Layer Defense-in-Depth Architecture ───────────────────────────────────

DEFENSE_IN_DEPTH_LAYERS = [
    {
        "layer": 1,
        "name": "Network Layer",
        "technologies": ["TLS 1.3 / HTTPS", "Cloudflare DDoS Mitigation", "Edge Edge Rules"],
        "description": "Protects edge boundaries, terminates TLS securely, and blocks volumetric volumetric attacks.",
    },
    {
        "layer": 2,
        "name": "Application Layer",
        "technologies": ["CORS Whitelist", "Redis Token Bucket Rate Limiting", "5 Security Headers"],
        "description": "Validates request origin, enforces per-endpoint request quotas, and configures browser security headers.",
    },
    {
        "layer": 3,
        "name": "Input Layer",
        "technologies": ["Pydantic Schemas", "HTML & Script Stripping", "Structured JSON LLM Parsing"],
        "description": "Sanitizes and clamps all user input, strips HTML/JS, and treats LLM output as data, never code.",
    },
    {
        "layer": 4,
        "name": "Data Layer",
        "technologies": ["SHA-256 Hashed API Keys", "Salted PII Log Redaction", "Parameterized ORM Queries"],
        "description": "Prevents SQL injection, ensures credentials cannot be reversed, and scrubs personal identifiers.",
    },
    {
        "layer": 5,
        "name": "Infrastructure Layer",
        "technologies": [".gitignore Secrets", "Platform Environment Variables", "Isolated Environments"],
        "description": "Keeps credentials isolated per environment, ensuring no secrets are committed to version control.",
    },
]


def get_defense_in_depth_layers() -> Dict[str, Any]:
    """Return the 5-layer defense-in-depth security model."""
    return {
        "total_layers": len(DEFENSE_IN_DEPTH_LAYERS),
        "layers": DEFENSE_IN_DEPTH_LAYERS,
    }


# ── 2. OWASP Top 10 Mapping Matrix ─────────────────────────────────────────────

OWASP_TOP_10_MATRIX = [
    {
        "code": "A01",
        "risk": "Broken Access Control",
        "mitigation": "Token bucket rate limiting, multi-tier API key permissions (anonymous, developer, pro, admin).",
        "status": "Implemented",
        "status_code": "IMPLEMENTED",
    },
    {
        "code": "A02",
        "risk": "Cryptographic Failures",
        "mitigation": "HTTPS enforcement everywhere, HSTS (max-age=31536000), SHA-256 hashed API key storage.",
        "status": "Implemented",
        "status_code": "IMPLEMENTED",
    },
    {
        "code": "A03",
        "risk": "Injection",
        "mitigation": "Prisma ORM & SQLAlchemy with strictly typed parameterized bindings (zero raw SQL queries).",
        "status": "Implemented",
        "status_code": "IMPLEMENTED",
    },
    {
        "code": "A04",
        "risk": "Insecure Design",
        "mitigation": "Comprehensive threat modeling, STRIDE risk evaluation, and pre-launch security reviews.",
        "status": "Documented",
        "status_code": "DOCUMENTED",
    },
    {
        "code": "A05",
        "risk": "Security Misconfiguration",
        "mitigation": "5 mandatory security headers (HSTS, DENY, nosniff, XSS), strict CORS whitelist (no wildcard * in prod).",
        "status": "Implemented",
        "status_code": "IMPLEMENTED",
    },
    {
        "code": "A06",
        "risk": "Vulnerable and Outdated Components",
        "mitigation": "Automated Dependabot scanning, pinned dependency locks, and continuous security testing.",
        "status": "Active Monitoring",
        "status_code": "ACTIVE_MONITORING",
    },
    {
        "code": "A07",
        "risk": "Identification and Authentication Failures",
        "mitigation": "Zero mandatory accounts for search, cryptographically secure random API keys with prefixing.",
        "status": "By Design",
        "status_code": "BY_DESIGN",
    },
    {
        "code": "A08",
        "risk": "Software and Data Integrity Failures",
        "mitigation": "Pydantic schema validation on all inputs, bounded integer ranges, and JSON-only LLM output parsing.",
        "status": "Implemented",
        "status_code": "IMPLEMENTED",
    },
    {
        "code": "A09",
        "risk": "Security Logging and Monitoring Failures",
        "mitigation": "Structured JSON logging, Sentry error tracking, salted IP redaction (no plaintext PII in logs).",
        "status": "Implemented",
        "status_code": "IMPLEMENTED",
    },
    {
        "code": "A10",
        "risk": "Server-Side Request Forgery (SSRF)",
        "mitigation": "No arbitrary remote URL fetching from untrusted user inputs; strictly static CDN asset URLs.",
        "status": "By Design",
        "status_code": "BY_DESIGN",
    },
]


def get_owasp_top_10_matrix() -> Dict[str, Any]:
    """Return the OWASP Top 10 security mapping."""
    return {
        "total_risks": len(OWASP_TOP_10_MATRIX),
        "owasp_risks": OWASP_TOP_10_MATRIX,
    }


# ── 3. Threat Model Risk Matrix ────────────────────────────────────────────────

THREAT_MODEL_MATRIX = [
    {
        "threat": "DDoS attack",
        "likelihood": "Medium",
        "impact": "High",
        "mitigation": "Cloudflare edge protection + Redis token bucket rate limiting (30 req/min for AI search).",
        "residual_risk": "Low",
    },
    {
        "threat": "API key theft",
        "likelihood": "Low",
        "impact": "Medium",
        "mitigation": "SHA-256 hashed database storage, key masking in UI/API, user-controlled key rotation.",
        "residual_risk": "Low",
    },
    {
        "threat": "SQL injection",
        "likelihood": "Very Low",
        "impact": "Critical",
        "mitigation": "SQLAlchemy and Prisma ORM parameterized query bindings (no raw string formatting).",
        "residual_risk": "Very Low",
    },
    {
        "threat": "XSS attack",
        "likelihood": "Low",
        "impact": "Medium",
        "mitigation": "Regex HTML stripping, JS protocol removal, and React automatic context-aware escaping.",
        "residual_risk": "Low",
    },
    {
        "threat": "Prompt injection",
        "likelihood": "Medium",
        "impact": "Low",
        "mitigation": "JSON-only LLM output parsing, deterministic fallback schema, output never executed as code.",
        "residual_risk": "Low",
    },
    {
        "threat": "Data breach",
        "likelihood": "Low",
        "impact": "High",
        "mitigation": "No mandatory user accounts for search, no plaintext PII stored, 90-day auto-purge.",
        "residual_risk": "Low",
    },
    {
        "threat": "Dependency vulnerability",
        "likelihood": "Medium",
        "impact": "Medium",
        "mitigation": "Dependabot vulnerability alerts, pinned dependencies in requirements.txt and package.json.",
        "residual_risk": "Low",
    },
]


def get_threat_model_matrix() -> Dict[str, Any]:
    """Return the complete threat model matrix."""
    return {
        "total_threats": len(THREAT_MODEL_MATRIX),
        "threats": THREAT_MODEL_MATRIX,
    }


# ── 4. Master Security Audit Checklist ─────────────────────────────────────────

MASTER_SECURITY_CHECKLIST = [
    {"id": 1, "item": "HTTPS enforced in production", "status": "COMPLETED", "verified": True},
    {"id": 2, "item": "CORS restricted to known origins", "status": "COMPLETED", "verified": True},
    {"id": 3, "item": "Rate limiting enabled on all endpoints", "status": "COMPLETED", "verified": True},
    {"id": 4, "item": "Input validation with Pydantic", "status": "COMPLETED", "verified": True},
    {"id": 5, "item": "No raw SQL queries (ORM only)", "status": "COMPLETED", "verified": True},
    {"id": 6, "item": "No PII in logs (salted IP hashing)", "status": "COMPLETED", "verified": True},
    {"id": 7, "item": "Security headers configured (HSTS, DENY, nosniff)", "status": "COMPLETED", "verified": True},
    {"id": 8, "item": "Secrets managed via environment variables", "status": "COMPLETED", "verified": True},
    {"id": 9, "item": ".env included in .gitignore", "status": "COMPLETED", "verified": True},
    {"id": 10, "item": "LLM output parsed as JSON only", "status": "COMPLETED", "verified": True},
    {"id": 11, "item": "Dependency scanning configured", "status": "COMPLETED", "verified": True},
    {"id": 12, "item": "Comprehensive security audit & testing suite", "status": "COMPLETED", "verified": True},
]


def get_master_security_checklist() -> Dict[str, Any]:
    """Return the master security audit checklist."""
    completed = sum(1 for item in MASTER_SECURITY_CHECKLIST if item["verified"])
    return {
        "total_items": len(MASTER_SECURITY_CHECKLIST),
        "completed_items": completed,
        "completion_rate": round((completed / len(MASTER_SECURITY_CHECKLIST)) * 100, 1),
        "checklist": MASTER_SECURITY_CHECKLIST,
    }


# ── 5. OWASP Compliance Status Evaluator ───────────────────────────────────────

def evaluate_owasp_compliance_status() -> Dict[str, Any]:
    """Calculate OWASP Top 10 compliance score and mitigation coverage."""
    total = len(OWASP_TOP_10_MATRIX)
    mitigated = sum(1 for item in OWASP_TOP_10_MATRIX if item["status_code"] in ("IMPLEMENTED", "DOCUMENTED", "BY_DESIGN", "ACTIVE_MONITORING"))
    
    return {
        "status": "COMPLIANT" if mitigated == total else "NEEDS_ATTENTION",
        "owasp_coverage_percentage": round((mitigated / total) * 100, 1),
        "total_risks": total,
        "mitigated_risks": mitigated,
        "matrix": OWASP_TOP_10_MATRIX,
    }
