"""Deployment Section Manifest and Global Subsystem Health Service for MemeGPT.
Specification: 12_Deployment/README.md

Covers:
- Section 12 Documentation Manifest & Directory Mapping
- Consolidated Deployment Posture Summary across Hosting, CI/CD, Infrastructure, and Telemetry
- Live Deployment Subsystem Health Diagnostics
- Section Navigation (Previous: 11_Security, Next: 13_Project_Management)
"""

from typing import Any, Dict, List
from app.services.ci_cd_service import evaluate_ci_cd_pipeline_health
from app.services.deployment_overview_service import evaluate_deployment_readiness
from app.services.infrastructure_service import evaluate_infrastructure_capacity_and_health
from app.services.monitoring_service import evaluate_live_metrics_and_alerts


# ── 1. Section 12 Documentation Manifest ───────────────────────────────────────

DEPLOYMENT_SECTION_MANIFEST = [
    {
        "file": "CI_CD_Pipeline.md",
        "title": "CI/CD Pipeline & GitHub Actions",
        "description": "GitHub Actions workflows (ci.yml, deploy.yml, cron.yml), pipeline SLA timings (CI ~3.5 min, CD ~4 min), and automated post-deploy smoke tests.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment/ci-cd",
    },
    {
        "file": "Deployment_Overview.md",
        "title": "Deployment Overview (Complete Guide)",
        "description": "Multi-cloud architecture (Vercel, Railway, Qdrant, Supabase, Redis, R2), production Dockerfile, step-by-step CLI commands, and cost analysis.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment/overview",
    },
    {
        "file": "Infrastructure.md",
        "title": "Infrastructure Map & Service Inventory",
        "description": "4-tier infrastructure topology (Edge, App, Data, External), 13-service inventory ($0-$7/mo), and TLS/gRPC networking latency benchmarks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment/infrastructure",
    },
    {
        "file": "Monitoring.md",
        "title": "Monitoring, Telemetry & Alerting",
        "description": "4-tool monitoring stack (UptimeRobot, Sentry, Umami, Railway Logs), Sentry alert rules, key metrics SLA dashboard, and standard /health schema.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment/monitoring",
    },
    {
        "file": "Rollback_Strategy.md",
        "title": "Rollback Strategy & Disaster Recovery",
        "description": "Fast-recovery rollback procedures for frontend, backend, database migrations, and ML model Docker image reverts.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment/rollback",
    },
    {
        "file": "Scaling.md",
        "title": "Scaling Strategy & Capacity Planning",
        "description": "Horizontal and vertical auto-scaling rules, connection pool tuning, and cache scaling thresholds.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment/scaling",
    },
    {
        "file": "README.md",
        "title": "Deployment Section Manifest",
        "description": "Section index, documentation navigation, consolidated deployment posture, and global diagnostic health checks.",
        "status": "COMPLETED",
        "route_prefix": "/api/v1/deployment",
    },
]


def get_deployment_section_manifest() -> Dict[str, Any]:
    """Return Section 12 documentation inventory and metadata."""
    completed = sum(1 for doc in DEPLOYMENT_SECTION_MANIFEST if doc["status"] == "COMPLETED")
    return {
        "section_id": "12",
        "section_name": "Deployment",
        "total_documents": len(DEPLOYMENT_SECTION_MANIFEST),
        "completed_documents": completed,
        "completion_percentage": round((completed / len(DEPLOYMENT_SECTION_MANIFEST)) * 100, 1),
        "navigation": {
            "previous_section": "11_Security",
            "previous_readme": "md files/documentation/11_Security/README.md",
            "next_section": "13_Project_Management",
            "next_readme": "md files/documentation/13_Project_Management/README.md",
        },
        "documents": DEPLOYMENT_SECTION_MANIFEST,
    }


# ── 2. Consolidated Deployment Posture Summary ─────────────────────────────────

def get_deployment_posture_summary() -> Dict[str, Any]:
    """Return consolidated posture across all deployment domains."""
    return {
        "hosting_topology": {
            "frontend": "Vercel Edge Global CDN (300+ PoPs)",
            "backend": "Railway FastAPI Container (US-East)",
            "databases": "Supabase PostgreSQL + Qdrant Vector DB (US-East)",
            "cache": "Upstash Serverless Redis (US-East)",
            "media_cdn": "Cloudflare R2 S3-Compatible Object Storage",
        },
        "automation_and_ci_cd": {
            "ci_pipeline": "GitHub Actions on all PRs (~3.5 min)",
            "cd_pipeline": "GitHub Actions on merge to main (~4 min)",
            "cron_maintenance": "Weekly Sunday 3 AM UTC popularity recalculation",
            "smoke_tests": "Automated post-deploy health check probes",
        },
        "cost_and_capacity": {
            "mvp_monthly_burn": "$0–$7",
            "scaled_10k_dau_estimate": "~$42/mo",
            "capacity_alert_threshold": "80% free tier consumption",
        },
        "monitoring_and_telemetry": {
            "uptime_monitoring": "UptimeRobot 5-min intervals (keep-alive + uptime)",
            "error_tracking": "Sentry with 10% trace sampling & zero PII",
            "analytics": "Self-hosted Umami privacy analytics",
            "sla_targets": "Uptime >99.5%, Error rate <2%, P95 <3.0s, Cache hit >60%",
        },
    }


# ── 3. Subsystem Health Diagnostics ────────────────────────────────────────────

def get_deployment_subsystem_health() -> Dict[str, Any]:
    """Run real-time diagnostics across all deployment subsystems."""
    cicd = evaluate_ci_cd_pipeline_health()
    readiness = evaluate_deployment_readiness()
    infra = evaluate_infrastructure_capacity_and_health()
    metrics = evaluate_live_metrics_and_alerts()

    all_healthy = (
        cicd.get("status") == "HEALTHY"
        and readiness.get("status") in ("READY", "HEALTHY")
        and infra.get("status") == "HEALTHY"
        and metrics.get("status") == "HEALTHY"
    )

    return {
        "status": "HEALTHY" if all_healthy else "DEGRADED",
        "subsystems": {
            "ci_cd_pipeline": {
                "status": cicd.get("status"),
                "workflows_verified": cicd.get("total_workflows_verified"),
            },
            "deployment_readiness": {
                "status": readiness.get("status"),
                "readiness_score": readiness.get("readiness_score"),
            },
            "infrastructure": {
                "status": infra.get("status"),
                "traffic_encrypted": infra.get("all_traffic_encrypted"),
                "service_count": infra.get("service_count"),
            },
            "monitoring_metrics": {
                "status": metrics.get("status"),
                "all_sla_met": metrics.get("all_sla_targets_met"),
            },
        },
    }
