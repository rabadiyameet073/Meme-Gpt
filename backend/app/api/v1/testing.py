"""Testing API Router for MemeGPT.
Specification: 10_Testing/AI_Evaluation.md
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.ai_evaluation_service import (
    get_evaluation_metrics_catalog,
    get_benchmark_test_cases,
    get_ai_failure_analysis_checklist,
    run_offline_search_evaluation,
    evaluate_ab_test_decision,
)
from app.services.backend_tests_service import (
    get_backend_test_suite_structure,
    get_test_execution_commands,
    get_coverage_targets,
    get_backend_tests_inventory,
)
from app.services.frontend_tests_service import (
    get_frontend_test_stack,
    get_frontend_test_commands,
    get_frontend_coverage_targets,
    get_frontend_test_inventory,
)
from app.services.load_testing_service import (
    get_locust_task_weights,
    get_performance_targets,
    get_load_test_scenarios,
    get_load_testing_best_practices,
    evaluate_load_test_results,
)
from app.services.performance_tests_service import (
    get_component_benchmarks,
    get_performance_suite_commands,
    benchmark_system_components,
)
from app.services.testing_strategy_service import (
    get_testing_section_manifest,
    get_testing_pyramid,
    get_testing_best_practices,
    get_testing_system_health,
)

logger = logging.getLogger("memegpt.api.testing")
router = APIRouter(prefix="/test", tags=["Testing & AI Evaluation"])





class OfflineEvaluationRequest(BaseModel):
    predictions: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Optional mapping of query -> list of predicted meme IDs for evaluation",
    )
    test_cases_file: Optional[str] = Field(
        default=None,
        description="Optional custom JSON test cases path",
    )
    use_live_matcher: bool = Field(
        default=False,
        description="Whether to run live match_memes engine on each test query",
    )


class OnlineMetricsCalculationRequest(BaseModel):
    clicks: int = Field(default=0, description="Total click count")
    impressions: int = Field(default=0, description="Total search impression count")
    downloads: int = Field(default=0, description="Total download count")
    thumbs_up: int = Field(default=0, description="Total positive feedback count")
    thumbs_down: int = Field(default=0, description="Total negative feedback count")


class ABTestEvaluationRequest(BaseModel):
    control: Dict[str, float] = Field(..., description="Control variant metrics (ctr, download_rate, precision_at_5, latency_p95_ms)")
    variant: Dict[str, float] = Field(..., description="Test variant metrics (ctr, download_rate, precision_at_5, latency_p95_ms)")
    sample_size: int = Field(default=1000, description="Total sample query count")


class LoadTestEvaluationRequest(BaseModel):
    p50_ms: float = Field(..., description="Observed P50 response time in ms")
    p95_ms: float = Field(..., description="Observed P95 response time in ms")
    error_rate: float = Field(..., description="Observed error rate ratio (e.g. 0.005 for 0.5%)")
    throughput_rps: float = Field(..., description="Observed throughput in requests per second")
    concurrent_users: int = Field(default=50, description="Concurrent simulated users")


@router.get("/ai/metrics", summary="Get AI evaluation metrics catalog")
def get_metrics():
    """Retrieve full catalog of 7 AI retrieval quality and user engagement metrics."""
    return {
        "success": True,
        **get_evaluation_metrics_catalog(),
        "failure_analysis_checklist": get_ai_failure_analysis_checklist(),
    }


@router.get("/ai/benchmark-dataset", summary="Get curated benchmark test cases")
def get_benchmarks():
    """Retrieve ground-truth dataset with annotated relevant and irrelevant memes."""
    return {
        "success": True,
        "test_cases": get_benchmark_test_cases(),
        "total_test_cases": len(get_benchmark_test_cases()),
    }


@router.post("/ai/evaluate-offline", summary="Run offline IR search quality evaluation")
def evaluate_offline(body: OfflineEvaluationRequest):
    """Calculate Precision@5, Recall@10, MRR, and NDCG@5 against benchmark dataset."""
    res = run_offline_search_evaluation(
        predictions_by_query=body.predictions,
        test_cases_file=body.test_cases_file,
        use_live_matcher=body.use_live_matcher,
    )
    return {
        "success": True,
        **res,
    }


@router.post("/ai/online-metrics", summary="Compute online engagement metrics (CTR, Download Rate, Thumbs Up)")
def compute_online_metrics(body: OnlineMetricsCalculationRequest):
    """Calculate online CTR, Download Rate, and Thumbs Up Rate with SLA targets."""
    from app.services.ai_evaluation_service import (
        calculate_ctr,
        calculate_download_rate,
        calculate_thumbs_up_rate,
    )
    ctr = calculate_ctr(body.clicks, body.impressions)
    dl_rate = calculate_download_rate(body.downloads, body.clicks)
    thumbs_rate = calculate_thumbs_up_rate(body.thumbs_up, body.thumbs_down)

    return {
        "success": True,
        "metrics": {
            "ctr": ctr,
            "ctr_meets_target": ctr >= 0.30,
            "download_rate": dl_rate,
            "download_rate_meets_target": dl_rate >= 0.15,
            "thumbs_up_rate": thumbs_rate,
            "thumbs_up_rate_meets_target": thumbs_rate >= 0.80,
        },
    }


@router.post("/ai/evaluate-ab-test", summary="Evaluate A/B experiment decision criteria")
def evaluate_ab_test(body: ABTestEvaluationRequest):
    """Evaluate if variant meets shipping criteria (+5% CTR, +3% Download Rate, latency safety)."""
    res = evaluate_ab_test_decision(
        control=body.control,
        variant=body.variant,
        sample_size=body.sample_size,
    )
    return {
        "success": True,
        **res,
    }


@router.get("/backend/structure", summary="Get Backend test suite directory structure")
def get_structure():
    """Retrieve standard directory layout of backend pytest suite."""
    return {
        "success": True,
        **get_backend_test_suite_structure(),
    }


@router.get("/backend/commands", summary="Get Backend test execution commands")
def get_commands():
    """Retrieve standard pytest commands and flags."""
    return {
        "success": True,
        "commands": get_test_execution_commands(),
    }


@router.get("/backend/coverage-targets", summary="Get Backend coverage targets")
def get_coverage():
    """Retrieve module-level coverage targets (>80% overall)."""
    return {
        "success": True,
        **get_coverage_targets(),
    }


@router.get("/backend/inventory", summary="Inspect active backend test files")
def get_inventory():
    """Discover all active test files in backend/tests directory."""
    return {
        "success": True,
        **get_backend_tests_inventory(),
    }


@router.get("/frontend/stack", summary="Get Frontend test technology stack")
def get_fe_stack():
    """Retrieve frontend test tools stack (Vitest, RTL, jsdom, MSW)."""
    return {
        "success": True,
        **get_frontend_test_stack(),
    }


@router.get("/frontend/commands", summary="Get Frontend test execution commands")
def get_fe_commands():
    """Retrieve npm scripts for frontend testing."""
    return {
        "success": True,
        "commands": get_frontend_test_commands(),
    }


@router.get("/frontend/coverage-targets", summary="Get Frontend coverage targets")
def get_fe_coverage():
    """Retrieve component-level coverage targets (>70% overall)."""
    return {
        "success": True,
        **get_frontend_coverage_targets(),
    }


@router.get("/frontend/inventory", summary="Inspect active frontend test files")
def get_fe_inventory():
    """Discover all active test files in frontend/src/tests directory."""
    return {
        "success": True,
        **get_frontend_test_inventory(),
    }


@router.get("/load/scenarios", summary="Get 5 load test scenarios")
def get_scenarios():
    """Retrieve Smoke, Normal, Peak, Stress, and Endurance load scenarios."""
    return {
        "success": True,
        "scenarios": get_load_test_scenarios(),
    }


@router.get("/load/targets", summary="Get load testing performance targets")
def get_load_targets():
    """Retrieve SLA targets and failure thresholds."""
    return {
        "success": True,
        **get_performance_targets(),
        "best_practices": get_load_testing_best_practices(),
    }


@router.get("/load/tasks", summary="Get Locust simulated user task weights")
def get_load_tasks():
    """Retrieve Locust weighted task distribution."""
    return {
        "success": True,
        **get_locust_task_weights(),
    }


@router.post("/load/evaluate", summary="Evaluate load test run against SLA criteria")
def evaluate_load_test(body: LoadTestEvaluationRequest):
    """Evaluate observed P50, P95, error rate, and throughput against production SLA."""
    res = evaluate_load_test_results(
        p50_ms=body.p50_ms,
        p95_ms=body.p95_ms,
        error_rate=body.error_rate,
        throughput_rps=body.throughput_rps,
        concurrent_users=body.concurrent_users,
    )
    return {
        "success": True,
        **res,
    }


@router.get("/performance/benchmarks", summary="Get 7 component latency benchmarks")
def get_benchmarks_sla():
    """Retrieve latency SLAs for MiniLM, Emotion detection, Groq, Qdrant, Re-ranking, Redis, and Pipeline."""
    return {
        "success": True,
        **get_component_benchmarks(),
    }


@router.get("/performance/commands", summary="Get performance testing commands")
def get_perf_commands():
    """Retrieve standard commands for running performance tests with timing metrics."""
    return {
        "success": True,
        "commands": get_performance_suite_commands(),
    }


@router.post("/performance/run-live-benchmark", summary="Run live in-process micro-benchmarks")
def run_live_benchmark():
    """Execute real-time micro-benchmark across embeddings, emotion detection, rule engine, and re-ranking."""
    res = benchmark_system_components()
    return {
        "success": True,
        **res,
    }


@router.get("/manifest", summary="Get Section 10 Testing master manifest")
def get_manifest():
    """Retrieve full catalog and metadata of all Section 10 testing documentation and test suites."""
    return {
        "success": True,
        **get_testing_section_manifest(),
    }


@router.get("/pyramid", summary="Get MemeGPT multi-layer testing pyramid")
def get_pyramid():
    """Retrieve testing pyramid distribution (Unit, Integration, Performance, Load, ML Eval)."""
    return {
        "success": True,
        **get_testing_pyramid(),
    }


@router.get("/practices", summary="Get 6 core testing best practices")
def get_practices():
    """Retrieve testing best practices (happy path, mocking, staging, ML tracking)."""
    return {
        "success": True,
        "practices": get_testing_best_practices(),
    }


@router.get("/health", summary="Run diagnostic health checks across all testing subsystems")
def get_health_status():
    """Run diagnostics on AI evaluation, backend tests, frontend tests, load tests, and performance benchmarks."""
    res = get_testing_system_health()
    return {
        "success": True,
        **res,
    }





