"""Testing Strategy & Section 10 Manifest Service for MemeGPT.
Specification: 10_Testing/README.md & 10_Testing/Testing_Strategy.md
"""

import logging
from typing import Any, Dict, List

from app.services.ai_evaluation_service import get_evaluation_metrics_catalog
from app.services.backend_tests_service import get_coverage_targets
from app.services.frontend_tests_service import get_frontend_test_stack
from app.services.load_testing_service import get_load_test_scenarios
from app.services.performance_tests_service import get_component_benchmarks

logger = logging.getLogger("memegpt.services.testing_strategy")

SECTION_10_DOCUMENTS = [
    {
        "filename": "AI_Evaluation.md",
        "title": "AI Evaluation Framework",
        "description": "Information Retrieval metrics (P@5, Recall@10, MRR, NDCG@5), benchmark dataset, and A/B test decision criteria",
        "path": "10_Testing/AI_Evaluation.md",
    },
    {
        "filename": "Backend_Tests.md",
        "title": "Backend Pytest Suite",
        "description": "FastAPI integration tests, matcher tests, rule scoring, 384-dim embeddings, and database CRUD",
        "path": "10_Testing/Backend_Tests.md",
    },
    {
        "filename": "Frontend_Tests.md",
        "title": "Frontend Testing",
        "description": "Vitest + React Testing Library + jsdom + MSW component and hook unit testing suite",
        "path": "10_Testing/Frontend_Tests.md",
    },
    {
        "filename": "Load_Tests.md",
        "title": "Load Testing",
        "description": "Locust load testing suite with 5 weighted tasks and 5 standard load scenarios",
        "path": "10_Testing/Load_Tests.md",
    },
    {
        "filename": "Performance_Tests.md",
        "title": "Performance Tests",
        "description": "7 component latency SLAs (MiniLM <100ms, emotion <150ms, pipeline <1.5s) and regression timers",
        "path": "10_Testing/Performance_Tests.md",
    },
    {
        "filename": "README.md",
        "title": "Testing Section Manifest",
        "description": "Overview and master index of all MemeGPT testing frameworks and documentation",
        "path": "10_Testing/README.md",
    },
    {
        "filename": "Testing_Strategy.md",
        "title": "Testing Strategy Guide",
        "description": "Testing pyramid, multi-layer test distribution, CI/CD pipeline, and 6 core best practices",
        "path": "10_Testing/Testing_Strategy.md",
    },
]

TESTING_PYRAMID = [
    {
        "layer": "E2E Tests",
        "count": 5,
        "speed": "<10s each",
        "scope": "Browser + API full user flow integration",
        "color": "#EF4444",
    },
    {
        "layer": "Integration Tests",
        "count": 15,
        "speed": "<3s each",
        "scope": "API endpoints, full ML pipeline, and database queries",
        "color": "#F59E0B",
    },
    {
        "layer": "Unit Tests",
        "count": "30+",
        "speed": "<1s each",
        "scope": "Services, models, rule engine, algorithms, and utilities",
        "color": "#22C55E",
    },
    {
        "layer": "Performance Tests",
        "count": 5,
        "speed": "<10s each",
        "scope": "P50/P95 latency, cache hit speed, and concurrency",
        "color": "#3B82F6",
    },
    {
        "layer": "Load Tests (Locust)",
        "count": "1 suite",
        "speed": "5m - 30m run",
        "scope": "Simulated concurrent traffic against staging",
        "color": "#8B5CF6",
    },
    {
        "layer": "ML Evaluation",
        "count": "1 suite",
        "speed": "30min",
        "scope": "Weekly offline precision, recall, MRR, and NDCG@5",
        "color": "#EC4899",
    },
]

TESTING_BEST_PRACTICES = [
    {
        "number": 1,
        "title": "Test happy path AND edge cases",
        "description": "Always test empty queries, max-length 2000-char input, emoji-only strings, and special characters",
    },
    {
        "number": 2,
        "title": "Mock external services for unit tests",
        "description": "Do not make real calls to external Groq API or remote Qdrant cluster in fast unit test runs",
    },
    {
        "number": 3,
        "title": "Use real services for integration tests",
        "description": "Verify actual HTTP responses, SQL queries, and serialization behavior",
    },
    {
        "number": 4,
        "title": "Run performance tests against staging",
        "description": "Never run load or stress tests on production systems",
    },
    {
        "number": 5,
        "title": "Track ML metrics weekly",
        "description": "Continuously evaluate Precision@5, Recall@10, MRR, and NDCG@5 to catch quality regressions",
    },
    {
        "number": 6,
        "title": "Use pytest-asyncio for async tests",
        "description": "MemeGPT backend endpoints and pipelines are fully asynchronous",
    },
]


def get_testing_section_manifest() -> Dict[str, Any]:
    """Return Section 10 Testing master manifest."""
    return {
        "section_id": "10_Testing",
        "title": "10 — Testing",
        "description": "Testing documentation and frameworks for MemeGPT.",
        "total_documents": len(SECTION_10_DOCUMENTS),
        "documents": SECTION_10_DOCUMENTS,
        "previous_section": "09_Development",
        "next_section": "11_Security",
    }


def get_testing_pyramid() -> Dict[str, Any]:
    """Return the multi-layered testing pyramid."""
    return {
        "total_layers": len(TESTING_PYRAMID),
        "pyramid": TESTING_PYRAMID,
    }


def get_testing_best_practices() -> List[Dict[str, Any]]:
    """Return the 6 testing best practices."""
    return TESTING_BEST_PRACTICES


def get_testing_system_health() -> Dict[str, Any]:
    """Diagnostic running health checks across all Section 10 testing services."""
    checks = {}

    try:
        ai_metrics = get_evaluation_metrics_catalog()
        checks["ai_evaluation"] = {"status": "healthy", "metrics_count": ai_metrics.get("total_metrics", 0)}
    except Exception as e:
        checks["ai_evaluation"] = {"status": "unhealthy", "error": str(e)}

    try:
        cov = get_coverage_targets()
        checks["backend_tests"] = {"status": "healthy", "modules_targeted": len(cov.get("modules", []))}
    except Exception as e:
        checks["backend_tests"] = {"status": "unhealthy", "error": str(e)}

    try:
        fe = get_frontend_test_stack()
        checks["frontend_tests"] = {"status": "healthy", "stack_tools": fe.get("total_tools", 0)}
    except Exception as e:
        checks["frontend_tests"] = {"status": "unhealthy", "error": str(e)}

    try:
        load = get_load_test_scenarios()
        checks["load_tests"] = {"status": "healthy", "scenarios_count": len(load)}
    except Exception as e:
        checks["load_tests"] = {"status": "unhealthy", "error": str(e)}

    try:
        perf = get_component_benchmarks()
        checks["performance_tests"] = {"status": "healthy", "benchmarks_count": perf.get("total_components", 0)}
    except Exception as e:
        checks["performance_tests"] = {"status": "unhealthy", "error": str(e)}

    all_healthy = all(v.get("status") == "healthy" for v in checks.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "total_modules": len(checks),
    }
