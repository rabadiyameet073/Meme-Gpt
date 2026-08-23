"""Tests for Load Tests Management from 10_Testing/Load_Tests.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.load_testing_service import (
    get_locust_task_weights,
    get_performance_targets,
    get_load_test_scenarios,
    get_load_testing_best_practices,
    evaluate_load_test_results,
)

client = TestClient(app)


def test_locust_task_weights():
    tasks = get_locust_task_weights()
    assert tasks["total_tasks"] == 5
    assert tasks["total_weight"] == 21
    task_map = {t["task_name"]: t["weight"] for t in tasks["tasks"]}
    assert task_map["search_meme"] == 10
    assert task_map["view_trending"] == 5
    assert task_map["view_meme_detail"] == 3
    assert task_map["submit_feedback"] == 2
    assert task_map["health_check"] == 1


def test_load_test_scenarios():
    scenarios = get_load_test_scenarios()
    assert len(scenarios) == 5
    names = [s["name"] for s in scenarios]
    assert "Smoke test" in names
    assert "Normal load" in names
    assert "Peak load" in names
    assert "Stress test" in names
    assert "Endurance" in names


def test_performance_targets():
    targets = get_performance_targets()
    assert targets["total_metrics"] == 5
    metric_names = [t["metric"] for t in targets["targets"]]
    assert "P50 response time" in metric_names
    assert "P95 response time" in metric_names
    assert "Error rate" in metric_names
    assert "Throughput" in metric_names
    assert "Concurrent users" in metric_names


def test_evaluate_load_test_results():
    # Passing run
    res_pass = evaluate_load_test_results(
        p50_ms=450.0,
        p95_ms=1800.0,
        error_rate=0.002,
        throughput_rps=22.5,
        concurrent_users=50,
    )
    assert res_pass["status"] == "PASS"
    assert res_pass["metrics"]["p50_response_time"]["status"] == "PASS"

    # Failing run (severe latency and high errors)
    res_fail = evaluate_load_test_results(
        p50_ms=2500.0,
        p95_ms=5500.0,
        error_rate=0.08,
        throughput_rps=3.0,
        concurrent_users=50,
    )
    assert res_fail["status"] == "CRITICAL_FAIL"
    assert res_fail["metrics"]["p50_response_time"]["status"] == "FAIL"


def test_load_testing_api_endpoints():
    res_scen = client.get("/api/v1/test/load/scenarios")
    assert res_scen.status_code == 200
    assert len(res_scen.json()["scenarios"]) == 5

    res_tgt = client.get("/api/v1/test/load/targets")
    assert res_tgt.status_code == 200
    assert res_tgt.json()["total_metrics"] == 5

    res_tasks = client.get("/api/v1/test/load/tasks")
    assert res_tasks.status_code == 200
    assert res_tasks.json()["total_tasks"] == 5

    res_eval = client.post("/api/v1/test/load/evaluate", json={
        "p50_ms": 600.0,
        "p95_ms": 2100.0,
        "error_rate": 0.004,
        "throughput_rps": 18.0,
        "concurrent_users": 50,
    })
    assert res_eval.status_code == 200
    assert res_eval.json()["status"] == "PASS"
