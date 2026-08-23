"""Monitoring, Telemetry, and Alerting Service for MemeGPT.
Specification: 12_Deployment/Monitoring.md

Covers:
- 4-Component Monitoring Stack (UptimeRobot, Sentry, Umami, Railway Logs)
- UptimeRobot Keep-Alive and Synthetic Monitoring Configuration
- Sentry SDK Setup & Alert Rules Matrix
- Key Metrics Dashboard with Targets & Alert Thresholds
- Standard Health Check Response Schema
- 5 Monitoring Best Practices
- Automated Metrics & SLA Threshold Evaluator
"""

import time
from typing import Any, Dict, List, Optional

START_TIME = time.time()


# ── 1. Monitoring Stack ────────────────────────────────────────────────────────

MONITORING_STACK = [
    {
        "tool": "UptimeRobot",
        "purpose": "External uptime & keep-alive monitoring",
        "free_tier": "50 monitors (5-min intervals)",
        "what_it_tracks": "/health endpoint, web landing page, search API endpoint",
    },
    {
        "tool": "Sentry",
        "purpose": "Application error tracking & performance tracing",
        "free_tier": "5K events / month",
        "what_it_tracks": "Unhandled exceptions, stack traces, transaction latency",
    },
    {
        "tool": "Umami",
        "purpose": "Privacy-friendly self-hosted web analytics",
        "free_tier": "Self-hosted (free)",
        "what_it_tracks": "Page views, search usage, referrers, device breakdown",
    },
    {
        "tool": "Railway Logs",
        "purpose": "Centralized application container logs",
        "free_tier": "Included in starter credit",
        "what_it_tracks": "stdout/stderr from FastAPI, Uvicorn access logs",
    },
]


def get_monitoring_stack() -> Dict[str, Any]:
    """Return the 4-component monitoring stack catalog."""
    return {
        "total_tools": len(MONITORING_STACK),
        "stack": MONITORING_STACK,
    }


# ── 2. UptimeRobot Configuration ───────────────────────────────────────────────

UPTIMEROBOT_MONITORS = [
    {"monitor": "API Health", "url": "https://api.memegpt.com/health", "method": "GET", "check_interval": "5 min", "alert_channels": ["Email", "Slack"]},
    {"monitor": "Web App", "url": "https://memegpt.com", "method": "GET", "check_interval": "5 min", "alert_channels": ["Email"]},
    {"monitor": "Search Endpoint", "url": "https://api.memegpt.com/api/v1/search", "method": "POST", "check_interval": "15 min", "alert_channels": ["Email", "Slack"]},
]


def get_uptimerobot_config() -> Dict[str, Any]:
    """Return UptimeRobot synthetic monitor definitions."""
    return {
        "total_monitors": len(UPTIMEROBOT_MONITORS),
        "monitors": UPTIMEROBOT_MONITORS,
    }


# ── 3. Sentry Setup & Alert Rules ──────────────────────────────────────────────

SENTRY_CONFIG_SPEC = {
    "sdk_init": {
        "dsn": "os.environ.get('SENTRY_DSN', '')",
        "environment": "os.environ.get('APP_ENV', 'development')",
        "traces_sample_rate": 0.1,
        "profiles_sample_rate": 0.1,
        "send_default_pii": False,
    },
    "alert_rules": [
        {"condition": "Error rate spike", "threshold": ">5% in 5 min", "action": "Email + Slack notification", "severity": "CRITICAL"},
        {"condition": "New error type", "threshold": "First occurrence", "action": "Email notification", "severity": "WARNING"},
        {"condition": "P95 latency degradation", "threshold": ">3s for 10 min", "action": "Email notification", "severity": "WARNING"},
        {"condition": "Unhandled exception", "threshold": "Any unhandled exception", "action": "Sentry auto-captures with stack trace", "severity": "ERROR"},
    ],
}


def get_sentry_config_spec() -> Dict[str, Any]:
    """Return Sentry SDK configuration and alert rules."""
    return SENTRY_CONFIG_SPEC


# ── 4. Key Metrics Dashboard ───────────────────────────────────────────────────

METRICS_DASHBOARD = [
    {"metric": "Uptime", "source": "UptimeRobot", "target": ">99.5%", "alert_if": "<99%", "unit": "%"},
    {"metric": "Error rate", "source": "Sentry", "target": "<2%", "alert_if": ">5%", "unit": "%"},
    {"metric": "P50 latency", "source": "Application logs", "target": "<1.0s", "alert_if": ">2.0s", "unit": "s"},
    {"metric": "P95 latency", "source": "Application logs", "target": "<3.0s", "alert_if": ">5.0s", "unit": "s"},
    {"metric": "Cache hit rate", "source": "Redis metrics", "target": ">60%", "alert_if": "<30%", "unit": "%"},
    {"metric": "Search volume", "source": "Application logs", "target": "Trending positive", "alert_if": "Sudden drop to 0", "unit": "req/hr"},
    {"metric": "Daily active users", "source": "Umami", "target": "Trending positive", "alert_if": "N/A", "unit": "users/day"},
]


def get_key_metrics_dashboard() -> Dict[str, Any]:
    """Return key metrics dashboard specification with targets and alert triggers."""
    return {
        "total_metrics": len(METRICS_DASHBOARD),
        "dashboard": METRICS_DASHBOARD,
    }


# ── 5. 5 Monitoring Best Practices ─────────────────────────────────────────────

MONITORING_BEST_PRACTICES = [
    {
        "id": 1,
        "title": "Monitor externally",
        "description": "UptimeRobot executes pings from external edge nodes to detect real-world accessibility issues.",
    },
    {
        "id": 2,
        "title": "Set send_default_pii=False",
        "description": "Never transmit user IP addresses, raw passwords, or personal credentials to Sentry.",
    },
    {
        "id": 3,
        "title": "Sample traces at 10%",
        "description": "Keep performance profiling overhead low and preserve free tier event quotas.",
    },
    {
        "id": 4,
        "title": "Alert on error rate, not individual errors",
        "description": "Filter transient network noise by triggering alerts when error rates exceed 5% over 5 minutes.",
    },
    {
        "id": 5,
        "title": "Check health endpoint every 5 min",
        "description": "Prevents cold start sleep on free containers and provides continuous uptime telemetry.",
    },
]


def get_monitoring_best_practices() -> Dict[str, Any]:
    """Return 5 monitoring engineering best practices."""
    return {
        "total_practices": len(MONITORING_BEST_PRACTICES),
        "practices": MONITORING_BEST_PRACTICES,
    }


# ── 6. Standard Health Check Response ──────────────────────────────────────────

def get_standard_health_response() -> Dict[str, Any]:
    """Return standardized health response schema specified in lines 73-90."""
    uptime_sec = int(time.time() - START_TIME)
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": uptime_sec,
        "models": {
            "text_model": "loaded",
            "emotion": "loaded",
        },
        "services": {
            "redis": "connected",
            "qdrant": "connected",
            "database": "connected",
        },
    }


# ── 7. Live Metrics & Alert Evaluator ──────────────────────────────────────────

def evaluate_live_metrics_and_alerts(
    uptime: float = 99.9,
    error_rate: float = 0.5,
    p50_latency: float = 0.45,
    p95_latency: float = 1.8,
    cache_hit_rate: float = 78.0,
) -> Dict[str, Any]:
    """Evaluate telemetry values against established SLA alert thresholds."""
    violations = []

    if uptime < 99.0:
        violations.append(f"Uptime ({uptime}%) is below critical threshold of 99%")
    if error_rate > 5.0:
        violations.append(f"Error rate ({error_rate}%) exceeds alert threshold of 5%")
    if p50_latency > 2.0:
        violations.append(f"P50 latency ({p50_latency}s) exceeds alert threshold of 2.0s")
    if p95_latency > 5.0:
        violations.append(f"P95 latency ({p95_latency}s) exceeds alert threshold of 5.0s")
    if cache_hit_rate < 30.0:
        violations.append(f"Cache hit rate ({cache_hit_rate}%) is below minimum threshold of 30%")

    is_healthy = len(violations) == 0

    return {
        "status": "HEALTHY" if is_healthy else "ALERT_TRIGGERED",
        "all_sla_targets_met": is_healthy,
        "total_violations": len(violations),
        "violations": violations,
        "metrics_evaluated": {
            "uptime": f"{uptime}%",
            "error_rate": f"{error_rate}%",
            "p50_latency": f"{p50_latency}s",
            "p95_latency": f"{p95_latency}s",
            "cache_hit_rate": f"{cache_hit_rate}%",
        },
    }
