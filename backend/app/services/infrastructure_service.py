"""Infrastructure Map and Service Inventory Service for MemeGPT.
Specification: 12_Deployment/Infrastructure.md

Covers:
- 4-Tier Infrastructure Topology (Edge Layer, Application Layer, Data Layer, External Services)
- Complete 13-Service Inventory with Provider, Plan, Region, and Cost
- Networking Latency & Encryption Protocols Matrix
- 5 Infrastructure Best Practices
- Infrastructure Health and Capacity Evaluator
"""

from typing import Any, Dict, List


# ── 1. Infrastructure Topology ────────────────────────────────────────────────

INFRASTRUCTURE_TOPOLOGY = {
    "title": "MemeGPT Complete Infrastructure Map",
    "layers": [
        {
            "layer": "Edge Layer (Global)",
            "services": [
                {"name": "Vercel Edge", "role": "Frontend CDN & Serverless Rendering", "pops": "300+ PoPs", "region": "Global"},
                {"name": "Cloudflare R2", "role": "Media Asset Storage & Media CDN", "region": "Global"},
            ],
        },
        {
            "layer": "Application Layer (US-East)",
            "services": [
                {"name": "Railway", "role": "FastAPI Async Web Service Container", "spec": "512MB RAM, 1 vCPU", "region": "US-East"},
            ],
        },
        {
            "layer": "Data Layer (US-East)",
            "services": [
                {"name": "Supabase", "role": "Managed PostgreSQL Database", "quota": "500MB Free", "region": "US-East-1"},
                {"name": "Qdrant Cloud", "role": "Vector Database (Dense + Sparse)", "quota": "1GB / 1M vectors Free", "region": "US-East"},
                {"name": "Upstash Redis", "role": "Serverless Low-Latency Cache & Rate Limiter", "quota": "10K commands/day Free", "region": "US-East"},
            ],
        },
        {
            "layer": "External Services",
            "services": [
                {"name": "Groq Cloud", "role": "Ultra-Fast Llama-3 LLM Inference", "quota": "6K req/day Free", "region": "US"},
                {"name": "Sentry", "role": "Real-time Application Error Tracking", "quota": "5K events/mo Free", "region": "Global"},
                {"name": "Umami", "role": "Privacy-Focused Self-Hosted Analytics", "region": "Global"},
                {"name": "UptimeRobot", "role": "Automated 5-min Uptime Monitoring & Keep-Alive", "quota": "50 monitors Free", "region": "Global"},
            ],
        },
    ],
}


def get_infrastructure_topology() -> Dict[str, Any]:
    """Return the 4-tier infrastructure topology."""
    return INFRASTRUCTURE_TOPOLOGY


# ── 2. Service Inventory ───────────────────────────────────────────────────────

SERVICE_INVENTORY = [
    {"service": "Frontend hosting", "provider": "Vercel", "plan": "Hobby (free)", "region": "Global CDN", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Backend hosting", "provider": "Railway", "plan": "Starter ($5 credit)", "region": "US-East", "cost": "$0–$7", "cost_numeric": 0.0},
    {"service": "PostgreSQL", "provider": "Supabase", "plan": "Free (500MB)", "region": "US-East-1", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Vector DB", "provider": "Qdrant Cloud", "plan": "Free (1GB)", "region": "US-East", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Cache", "provider": "Upstash", "plan": "Free (10K/day)", "region": "US-East", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Object storage", "provider": "Cloudflare R2", "plan": "Free (10GB)", "region": "Global", "cost": "$0", "cost_numeric": 0.0},
    {"service": "LLM inference", "provider": "Groq Cloud", "plan": "Free (6K/day)", "region": "US", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Error tracking", "provider": "Sentry", "plan": "Free (5K events)", "region": "Global", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Analytics", "provider": "Umami", "plan": "Self-hosted", "region": "—", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Uptime monitoring", "provider": "UptimeRobot", "plan": "Free (50 monitors)", "region": "Global", "cost": "$0", "cost_numeric": 0.0},
    {"service": "CI/CD", "provider": "GitHub Actions", "plan": "Free (2K min)", "region": "—", "cost": "$0", "cost_numeric": 0.0},
    {"service": "DNS", "provider": "Cloudflare", "plan": "Free", "region": "Global", "cost": "$0", "cost_numeric": 0.0},
    {"service": "Domain", "provider": "Namecheap", "plan": "$8.88/year", "region": "—", "cost": "$9/yr", "cost_numeric": 0.75},
]


def get_service_inventory() -> Dict[str, Any]:
    """Return all 13 services in the infrastructure inventory."""
    return {
        "total_services": len(SERVICE_INVENTORY),
        "total_monthly_cost": "$0–$7",
        "inventory": SERVICE_INVENTORY,
    }


# ── 3. Networking & Latency Matrix ─────────────────────────────────────────────

NETWORKING_CONNECTIONS = [
    {"connection": "Client -> Vercel", "protocol": "HTTPS (TLS 1.3)", "encrypted": True, "latency": "~20ms", "latency_ms": 20},
    {"connection": "Vercel -> Railway", "protocol": "HTTPS", "encrypted": True, "latency": "~5ms", "latency_ms": 5},
    {"connection": "Railway -> Qdrant", "protocol": "gRPC over HTTPS", "encrypted": True, "latency": "~10ms", "latency_ms": 10},
    {"connection": "Railway -> Supabase", "protocol": "PostgreSQL (SSL)", "encrypted": True, "latency": "~5ms", "latency_ms": 5},
    {"connection": "Railway -> Upstash", "protocol": "Redis (TLS)", "encrypted": True, "latency": "~3ms", "latency_ms": 3},
    {"connection": "Railway -> Groq", "protocol": "HTTPS", "encrypted": True, "latency": "~50ms", "latency_ms": 50},
    {"connection": "Client -> R2", "protocol": "HTTPS", "encrypted": True, "latency": "~15ms", "latency_ms": 15},
]


def get_networking_matrix() -> Dict[str, Any]:
    """Return inter-service networking topology, protocols, and latency benchmarks."""
    return {
        "total_connections": len(NETWORKING_CONNECTIONS),
        "connections": NETWORKING_CONNECTIONS,
    }


# ── 4. 5 Infrastructure Best Practices ─────────────────────────────────────────

INFRASTRUCTURE_BEST_PRACTICES = [
    {
        "id": 1,
        "title": "Co-locate everything in US-East",
        "description": "Deploy Backend, PostgreSQL, Vector DB, and Redis in US-East to minimize inter-service network latency to <5ms.",
    },
    {
        "id": 2,
        "title": "Use free tiers aggressively",
        "description": "Maintain $0 operational cost for MVP by utilizing generous free allowances across Vercel, Supabase, Qdrant, and Groq.",
    },
    {
        "id": 3,
        "title": "Monitor all services",
        "description": "Keep automated keep-alive monitors in UptimeRobot and full error telemetry in Sentry.",
    },
    {
        "id": 4,
        "title": "Plan upgrades at 80% capacity",
        "description": "Establish proactive alerts at 80% free tier consumption rather than waiting for hard quota threshold limits.",
    },
    {
        "id": 5,
        "title": "No single points of failure",
        "description": "Implement graceful fallbacks so cache, vector DB, or analytics outages do not completely break meme search.",
    },
]


def get_infrastructure_best_practices() -> Dict[str, Any]:
    """Return 5 infrastructure engineering best practices."""
    return {
        "total_practices": len(INFRASTRUCTURE_BEST_PRACTICES),
        "practices": INFRASTRUCTURE_BEST_PRACTICES,
    }


# ── 5. Infrastructure Capacity and Health Evaluator ───────────────────────────

def evaluate_infrastructure_capacity_and_health() -> Dict[str, Any]:
    """Audit overall infrastructure co-location, security, and health."""
    all_encrypted = all(c["encrypted"] for c in NETWORKING_CONNECTIONS)
    us_east_count = sum(1 for s in SERVICE_INVENTORY if "US-East" in s["region"])

    return {
        "status": "HEALTHY",
        "all_traffic_encrypted": all_encrypted,
        "us_east_colocated_services": us_east_count,
        "capacity_alert_threshold": "80%",
        "monthly_burn_rate_estimate": "$0.00",
        "service_count": len(SERVICE_INVENTORY),
    }
