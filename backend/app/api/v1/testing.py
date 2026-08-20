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

logger = logging.getLogger("memegpt.api.testing")
router = APIRouter(prefix="/test", tags=["Testing & AI Evaluation"])


class OfflineEvaluationRequest(BaseModel):
    predictions: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Optional mapping of query -> list of predicted meme IDs for evaluation",
    )


class ABTestEvaluationRequest(BaseModel):
    control: Dict[str, float] = Field(..., description="Control variant metrics (ctr, download_rate, precision_at_5, latency_p95_ms)")
    variant: Dict[str, float] = Field(..., description="Test variant metrics (ctr, download_rate, precision_at_5, latency_p95_ms)")
    sample_size: int = Field(default=1000, description="Total sample query count")


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
    res = run_offline_search_evaluation(predictions_by_query=body.predictions)
    return {
        "success": True,
        **res,
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
