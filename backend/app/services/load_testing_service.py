"""Load Testing Management Service for MemeGPT.
Specification: 10_Testing/Load_Tests.md
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger("memegpt.services.load_testing")

LOCUST_TASK_WEIGHTS = [
    {
        "task_name": "search_meme",
        "endpoint": "/api/v1/search",
        "method": "POST",
        "weight": 10,
        "payload": {"query": "Monday morning feeling", "format_preference": "gif", "limit": 5},
        "description": "Primary semantic search query simulation",
    },
    {
        "task_name": "view_trending",
        "endpoint": "/api/v1/trending?category=all&limit=20",
        "method": "GET",
        "weight": 5,
        "description": "Category trending memes feed query",
    },
    {
        "task_name": "view_meme_detail",
        "endpoint": "/api/v1/memes/this-is-fine",
        "method": "GET",
        "weight": 3,
        "description": "Individual meme metadata and analytics retrieval",
    },
    {
        "task_name": "submit_feedback",
        "endpoint": "/api/v1/feedback",
        "method": "POST",
        "weight": 2,
        "payload": {"query_id": "q_loadtest", "meme_id": "meme_042", "action": "download"},
        "description": "User interaction feedback and telemetry ingestion",
    },
    {
        "task_name": "health_check",
        "endpoint": "/health",
        "method": "GET",
        "weight": 1,
        "description": "Basic readiness probe ping",
    },
]

PERFORMANCE_TARGETS = [
    {
        "metric": "P50 response time",
        "target": "<1.0s",
        "target_ms": 1000,
        "failure_threshold": ">2.0s",
        "failure_threshold_ms": 2000,
    },
    {
        "metric": "P95 response time",
        "target": "<3.0s",
        "target_ms": 3000,
        "failure_threshold": ">5.0s",
        "failure_threshold_ms": 5000,
    },
    {
        "metric": "Error rate",
        "target": "<1%",
        "target_ratio": 0.01,
        "failure_threshold": ">5%",
        "failure_threshold_ratio": 0.05,
    },
    {
        "metric": "Throughput",
        "target": ">10 req/s",
        "target_rps": 10.0,
        "failure_threshold": "<5 req/s",
        "failure_threshold_rps": 5.0,
    },
    {
        "metric": "Concurrent users",
        "target": "50 users",
        "target_users": 50,
        "failure_threshold": "N/A",
    },
]

LOAD_TEST_SCENARIOS = [
    {
        "name": "Smoke test",
        "users": 5,
        "spawn_rate": 1,
        "duration": "1 min",
        "purpose": "Verify basic functionality before full load test",
    },
    {
        "name": "Normal load",
        "users": 25,
        "spawn_rate": 2,
        "duration": "5 min",
        "purpose": "Simulate typical daily production traffic",
    },
    {
        "name": "Peak load",
        "users": 50,
        "spawn_rate": 5,
        "duration": "10 min",
        "purpose": "Simulate viral traffic surge or trending peak",
    },
    {
        "name": "Stress test",
        "users": 100,
        "spawn_rate": 10,
        "duration": "15 min",
        "purpose": "Identify system breaking point and bottleneck limits",
    },
    {
        "name": "Endurance",
        "users": 25,
        "spawn_rate": 2,
        "duration": "30 min",
        "purpose": "Check for memory leaks, connection exhaustion, and sustained stability",
    },
]

LOAD_TEST_BEST_PRACTICES = [
    {"rule": 1, "title": "Never load test production", "description": "Always execute load simulations against staging environment"},
    {"rule": 2, "title": "Start small, scale up", "description": "Progressively increase load: 5 -> 25 -> 50 -> 100 users"},
    {"rule": 3, "title": "Monitor server resources", "description": "Track CPU, RAM, and network I/O during execution"},
    {"rule": 4, "title": "Cache warmup first", "description": "Warm Redis cache with initial sample queries before measuring peak benchmarks"},
    {"rule": 5, "title": "Save results", "description": "Use --csv flag to archive CSV result logs for trend analysis"},
]


def get_locust_task_weights() -> Dict[str, Any]:
    """Return Locust simulated user action task distribution."""
    total_weight = sum(t["weight"] for t in LOCUST_TASK_WEIGHTS)
    return {
        "total_tasks": len(LOCUST_TASK_WEIGHTS),
        "total_weight": total_weight,
        "tasks": LOCUST_TASK_WEIGHTS,
    }


def get_performance_targets() -> Dict[str, Any]:
    """Return performance targets and failure thresholds."""
    return {
        "total_metrics": len(PERFORMANCE_TARGETS),
        "targets": PERFORMANCE_TARGETS,
    }


def get_load_test_scenarios() -> List[Dict[str, Any]]:
    """Return the 5 standard load testing scenarios."""
    return LOAD_TEST_SCENARIOS


def get_load_testing_best_practices() -> List[Dict[str, Any]]:
    """Return the 5 load testing best practices."""
    return LOAD_TEST_BEST_PRACTICES


def evaluate_load_test_results(
    p50_ms: float,
    p95_ms: float,
    error_rate: float,
    throughput_rps: float,
    concurrent_users: int = 50,
) -> Dict[str, Any]:
    """Evaluate observed load test metrics against SLA targets and failure thresholds."""
    p50_passed = p50_ms < 1000.0
    p50_failed = p50_ms > 2000.0

    p95_passed = p95_ms < 3000.0
    p95_failed = p95_ms > 5000.0

    err_passed = error_rate < 0.01
    err_failed = error_rate > 0.05

    tput_passed = throughput_rps >= 10.0
    tput_failed = throughput_rps < 5.0

    overall_status = "PASS"
    if p50_failed or p95_failed or err_failed or tput_failed:
        overall_status = "CRITICAL_FAIL"
    elif not (p50_passed and p95_passed and err_passed and tput_passed):
        overall_status = "DEGRADED_WARNING"

    return {
        "status": overall_status,
        "concurrent_users": concurrent_users,
        "metrics": {
            "p50_response_time": {
                "observed_ms": p50_ms,
                "target": "<1000ms",
                "status": "PASS" if p50_passed else ("FAIL" if p50_failed else "WARNING"),
            },
            "p95_response_time": {
                "observed_ms": p95_ms,
                "target": "<3000ms",
                "status": "PASS" if p95_passed else ("FAIL" if p95_failed else "WARNING"),
            },
            "error_rate": {
                "observed_ratio": error_rate,
                "target": "<1%",
                "status": "PASS" if err_passed else ("FAIL" if err_failed else "WARNING"),
            },
            "throughput": {
                "observed_rps": throughput_rps,
                "target": ">=10 req/s",
                "status": "PASS" if tput_passed else ("FAIL" if tput_failed else "WARNING"),
            },
        },
    }
