"""Scaling Strategy & Capacity Planning Service for MemeGPT.
Specification: 12_Deployment/Scaling.md

Covers:
- 4 Scaling Phases (MVP 0-1K DAU $0, Growth 1-10K DAU $42, Scale 10-100K DAU $200, Enterprise 100K+ DAU $500)
- 6 Scaling Triggers Matrix with Metric Thresholds & Actions
- Multi-Tier Cost Projections (100 DAU to 100K DAU)
- Component Horizontal Scaling Strategies (FastAPI workers, PgBouncer, Qdrant sharding, Upstash Redis)
- 5 Scaling Best Practices
- Dynamic DAU Cost Calculator and Trigger Threshold Evaluator
"""

from typing import Any, Dict, List, Optional


# ── 1. 4 Scaling Phases ────────────────────────────────────────────────────────

SCALING_PHASES = [
    {
        "phase": "Phase 1: MVP",
        "dau_range": "0–1,000 DAU",
        "monthly_cost": "$0/month",
        "cost_numeric": 0.0,
        "description": "100% free tier architecture across Vercel, Railway, Supabase, Qdrant, and Groq.",
    },
    {
        "phase": "Phase 2: Growth",
        "dau_range": "1,000–10,000 DAU",
        "monthly_cost": "~$42/month",
        "cost_numeric": 42.0,
        "description": "Starter Railway backend ($7), Supabase Pro database ($25), Upstash paid cache ($10).",
    },
    {
        "phase": "Phase 3: Scale",
        "dau_range": "10,000–100,000 DAU",
        "monthly_cost": "~$200/month",
        "cost_numeric": 200.0,
        "description": "Multi-worker backend containers, Qdrant paid cluster, DB read replicas, dedicated Redis.",
    },
    {
        "phase": "Phase 4: Enterprise",
        "dau_range": "100,000+ DAU",
        "monthly_cost": "~$500/month",
        "cost_numeric": 500.0,
        "description": "Multi-region Kubernetes clusters, global distributed database replicas, custom ML serving.",
    },
]


def get_scaling_phases() -> Dict[str, Any]:
    """Return the 4 scaling lifecycle phases."""
    return {
        "total_phases": len(SCALING_PHASES),
        "phases": SCALING_PHASES,
    }


# ── 2. 6 Scaling Triggers Matrix ───────────────────────────────────────────────

SCALING_TRIGGERS = [
    {
        "id": 1,
        "metric": "Qdrant vectors",
        "current_baseline": "10K",
        "trigger_threshold": ">500K",
        "action": "Upgrade to paid Qdrant cluster",
        "criticality": "HIGH",
    },
    {
        "id": 2,
        "metric": "Redis commands",
        "current_baseline": "5K/day",
        "trigger_threshold": ">10K/day",
        "action": "Upgrade Upstash plan ($10/mo)",
        "criticality": "MEDIUM",
    },
    {
        "id": 3,
        "metric": "API response time P95",
        "current_baseline": "1.2s",
        "trigger_threshold": ">3.0s",
        "action": "Add second API worker / container replica",
        "criticality": "HIGH",
    },
    {
        "id": 4,
        "metric": "Database size",
        "current_baseline": "100MB",
        "trigger_threshold": ">500MB",
        "action": "Upgrade Supabase plan ($25/mo)",
        "criticality": "HIGH",
    },
    {
        "id": 5,
        "metric": "CDN bandwidth",
        "current_baseline": "5GB/mo",
        "trigger_threshold": ">10GB/mo",
        "action": "Cloudflare R2 bandwidth expansion",
        "criticality": "LOW",
    },
    {
        "id": 6,
        "metric": "Concurrent users",
        "current_baseline": "10",
        "trigger_threshold": ">50",
        "action": "Scale FastAPI backend horizontally (Gunicorn 4 workers)",
        "criticality": "HIGH",
    },
]


def get_scaling_triggers() -> Dict[str, Any]:
    """Return the 6 scaling triggers with thresholds and actions."""
    return {
        "total_triggers": len(SCALING_TRIGGERS),
        "triggers": SCALING_TRIGGERS,
    }


# ── 3. Multi-Tier Cost Projections ─────────────────────────────────────────────

COST_PROJECTIONS = [
    {"dau": 100, "dau_label": "100", "backend": 0, "database": 0, "vector_db": 0, "cache": 0, "cdn": 0, "total": 0},
    {"dau": 1000, "dau_label": "1,000", "backend": 0, "database": 0, "vector_db": 0, "cache": 0, "cdn": 0, "total": 0},
    {"dau": 5000, "dau_label": "5,000", "backend": 7, "database": 0, "vector_db": 0, "cache": 0, "cdn": 0, "total": 7},
    {"dau": 10000, "dau_label": "10,000", "backend": 7, "database": 25, "vector_db": 0, "cache": 10, "cdn": 0, "total": 42},
    {"dau": 50000, "dau_label": "50,000", "backend": 25, "database": 25, "vector_db": 25, "cache": 20, "cdn": 0, "total": 95},
    {"dau": 100000, "dau_label": "100,000", "backend": 50, "database": 50, "vector_db": 50, "cache": 30, "cdn": 15, "total": 195},
]


def get_cost_projections() -> Dict[str, Any]:
    """Return multi-tier cost projections matrix across 100 to 100K DAU."""
    return {
        "total_tiers": len(COST_PROJECTIONS),
        "projections": COST_PROJECTIONS,
    }


# ── 4. Component Horizontal Scaling Strategies ────────────────────────────────

COMPONENT_SCALING_STRATEGIES = {
    "backend": {
        "framework": "FastAPI + Uvicorn / Gunicorn",
        "mvp": "uvicorn app.main:app --workers 1 (512MB RAM)",
        "scaled": "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker (~2GB RAM)",
        "memory_budget_per_worker": {
            "miniLM_embedding_model": "80MB",
            "emotion_classifier_model": "250MB",
            "python_runtime_overhead": "50MB",
            "total_per_worker": "~380MB RAM",
        },
    },
    "database": {
        "mvp": "Single Supabase PostgreSQL instance (Read + Write)",
        "growth": "Connection pooling via built-in PgBouncer",
        "scale": "Read replicas for search_logs & feedback analytics queries",
    },
    "vector_db": {
        "mvp": "Qdrant Cloud Free Tier (1GB, 1M vectors, 10K memes = ~50MB)",
        "growth": "Qdrant Cloud Free Tier (plenty of headroom)",
        "scale": "Qdrant Paid Cluster with multi-node sharding & HNSW index tuning",
    },
    "cache": {
        "mvp": "Upstash Redis Free (10K commands/day)",
        "growth": "Upstash Paid ($10/mo, 10M commands/day)",
        "scale": "Dedicated Redis cluster instance with cluster replication",
    },
}


def get_component_scaling_strategies() -> Dict[str, Any]:
    """Return horizontal and vertical scaling strategies across all 4 components."""
    return COMPONENT_SCALING_STRATEGIES


# ── 5. 5 Scaling Best Practices ────────────────────────────────────────────────

SCALING_BEST_PRACTICES = [
    {
        "id": 1,
        "title": "Optimize before scaling",
        "description": "Apply caching, query optimization, and lazy model loading before provisioning larger servers.",
    },
    {
        "id": 2,
        "title": "Scale vertically first",
        "description": "Increasing container RAM or CPU is simpler and cheaper than managing multi-node synchronization.",
    },
    {
        "id": 3,
        "title": "Monitor before acting",
        "description": "Trigger upgrades based on real Sentry/Uptime data rather than speculative assumptions.",
    },
    {
        "id": 4,
        "title": "Cache aggressively",
        "description": "Maintaining a >60% Redis cache hit rate reduces backend LLM and database load by more than half.",
    },
    {
        "id": 5,
        "title": "Free tier is your friend",
        "description": "MemeGPT can operate with $0 monthly infrastructure expenses for up to ~5K Daily Active Users.",
    },
]


def get_scaling_best_practices() -> Dict[str, Any]:
    """Return 5 scaling engineering best practices."""
    return {
        "total_practices": len(SCALING_BEST_PRACTICES),
        "practices": SCALING_BEST_PRACTICES,
    }


# ── 6. Dynamic DAU Cost Calculator ─────────────────────────────────────────────

def calculate_projected_cost(dau: int = 1000) -> Dict[str, Any]:
    """Calculate exact infrastructure cost breakdown for any given DAU count."""
    dau = max(0, dau)

    if dau <= 1000:
        backend = 0
        db = 0
        vector = 0
        cache = 0
        cdn = 0
        phase = "Phase 1: MVP"
    elif dau <= 5000:
        backend = 7
        db = 0
        vector = 0
        cache = 0
        cdn = 0
        phase = "Phase 1.5: Early Traction"
    elif dau <= 10000:
        backend = 7
        db = 25
        vector = 0
        cache = 10
        cdn = 0
        phase = "Phase 2: Growth"
    elif dau <= 50000:
        backend = 25
        db = 25
        vector = 25
        cache = 20
        cdn = 0
        phase = "Phase 2.5: Mid Scale"
    elif dau <= 100000:
        backend = 50
        db = 50
        vector = 50
        cache = 30
        cdn = 15
        phase = "Phase 3: Scale"
    else:
        # 100K+ enterprise interpolation
        multiplier = dau / 100000.0
        backend = int(50 * multiplier)
        db = int(50 * multiplier)
        vector = int(50 * multiplier)
        cache = int(30 * multiplier)
        cdn = int(15 * multiplier)
        phase = "Phase 4: Enterprise"

    total = backend + db + vector + cache + cdn

    return {
        "dau": dau,
        "lifecycle_phase": phase,
        "breakdown": {
            "backend_hosting": f"${backend}",
            "database_postgresql": f"${db}",
            "vector_database": f"${vector}",
            "cache_redis": f"${cache}",
            "cdn_and_storage": f"${cdn}",
        },
        "total_monthly_cost": f"${total}",
        "total_cost_numeric": total,
        "cost_per_dau": f"${round(total / dau, 4)}" if dau > 0 else "$0.00",
    }


# ── 7. Scaling Trigger Evaluator ───────────────────────────────────────────────

def evaluate_scaling_triggers(
    vector_count: int = 10000,
    daily_redis_commands: int = 5000,
    p95_latency_seconds: float = 1.2,
    db_size_mb: float = 100.0,
    cdn_bandwidth_gb: float = 5.0,
    concurrent_users: int = 10,
) -> Dict[str, Any]:
    """Evaluate telemetry values against established scaling trigger thresholds."""
    triggered = []

    if vector_count > 500000:
        triggered.append({"metric": "Qdrant vectors", "value": vector_count, "action": "Upgrade to paid Qdrant cluster"})
    if daily_redis_commands > 10000:
        triggered.append({"metric": "Redis commands", "value": daily_redis_commands, "action": "Upgrade Upstash plan ($10/mo)"})
    if p95_latency_seconds > 3.0:
        triggered.append({"metric": "P95 latency", "value": f"{p95_latency_seconds}s", "action": "Add second API worker / container replica"})
    if db_size_mb > 500.0:
        triggered.append({"metric": "Database size", "value": f"{db_size_mb}MB", "action": "Upgrade Supabase plan ($25/mo)"})
    if cdn_bandwidth_gb > 10.0:
        triggered.append({"metric": "CDN bandwidth", "value": f"{cdn_bandwidth_gb}GB", "action": "Cloudflare R2 bandwidth expansion"})
    if concurrent_users > 50:
        triggered.append({"metric": "Concurrent users", "value": concurrent_users, "action": "Scale FastAPI backend horizontally (Gunicorn 4 workers)"})

    return {
        "status": "SCALING_REQUIRED" if len(triggered) > 0 else "NOMINAL_CAPACITY",
        "scaling_required": len(triggered) > 0,
        "total_triggered_actions": len(triggered),
        "triggered_actions": triggered,
    }
