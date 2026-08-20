"""Tests for AI Evaluation from 10_Testing/AI_Evaluation.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.ai_evaluation_service import (
    get_evaluation_metrics_catalog,
    get_benchmark_test_cases,
    get_ai_failure_analysis_checklist,
    run_offline_search_evaluation,
    evaluate_ab_test_decision,
    calculate_ndcg_at_5,
)

client = TestClient(app)


def test_ai_evaluation_metrics_catalog():
    cat = get_evaluation_metrics_catalog()
    assert cat["total_metrics"] == 7
    names = [m["name"] for m in cat["metrics"]]
    assert "Precision@5" in names
    assert "Recall@10" in names
    assert "MRR" in names
    assert "NDCG@5" in names
    assert "CTR" in names
    assert "Download Rate" in names
    assert "Thumbs Up Rate" in names


def test_ndcg_calculation():
    relevant = ["m1", "m2", "m3"]
    # Perfect ranking: top 3 are relevant
    perfect_preds = ["m1", "m2", "m3", "other1", "other2"]
    ndcg_perfect = calculate_ndcg_at_5(perfect_preds, relevant)
    assert ndcg_perfect == 1.0

    # No relevance
    zero_preds = ["other1", "other2", "other3", "other4", "other5"]
    ndcg_zero = calculate_ndcg_at_5(zero_preds, relevant)
    assert ndcg_zero == 0.0


def test_run_offline_search_evaluation():
    eval_res = run_offline_search_evaluation()
    assert eval_res["total_test_cases"] == 5
    summary = eval_res["summary"]
    assert "precision_at_5" in summary
    assert "recall_at_10" in summary
    assert "mrr" in summary
    assert "ndcg_at_5" in summary
    assert summary["precision_at_5"] > 0.0


def test_evaluate_ab_test_decision():
    control = {
        "ctr": 0.30,
        "download_rate": 0.15,
        "precision_at_5": 0.72,
        "latency_p95_ms": 110.0,
    }

    # Successful variant: +6% CTR, +4% downloads, +3% P@5, low latency
    good_variant = {
        "ctr": 0.36,
        "download_rate": 0.19,
        "precision_at_5": 0.75,
        "latency_p95_ms": 112.0,
    }
    res_good = evaluate_ab_test_decision(control, good_variant, sample_size=1500)
    assert res_good["ship_decision"] == "SHIP_TO_PRODUCTION"

    # Regressed variant: Lower CTR and high latency
    bad_variant = {
        "ctr": 0.28,
        "download_rate": 0.14,
        "precision_at_5": 0.70,
        "latency_p95_ms": 250.0,
    }
    res_bad = evaluate_ab_test_decision(control, bad_variant, sample_size=1500)
    assert res_bad["ship_decision"] == "REJECT_OR_CONTINUE"


def test_testing_ai_api_endpoints():
    res_metrics = client.get("/api/v1/test/ai/metrics")
    assert res_metrics.status_code == 200
    assert res_metrics.json()["total_metrics"] == 7

    res_bench = client.get("/api/v1/test/ai/benchmark-dataset")
    assert res_bench.status_code == 200
    assert len(res_bench.json()["test_cases"]) == 5

    res_eval = client.post("/api/v1/test/ai/evaluate-offline", json={})
    assert res_eval.status_code == 200
    assert res_eval.json()["total_test_cases"] == 5

    res_ab = client.post("/api/v1/test/ai/evaluate-ab-test", json={
        "control": {"ctr": 0.30, "download_rate": 0.15, "precision_at_5": 0.72, "latency_p95_ms": 100.0},
        "variant": {"ctr": 0.36, "download_rate": 0.19, "precision_at_5": 0.76, "latency_p95_ms": 102.0},
        "sample_size": 2000
    })
    assert res_ab.status_code == 200
    assert res_ab.json()["ship_decision"] == "SHIP_TO_PRODUCTION"
