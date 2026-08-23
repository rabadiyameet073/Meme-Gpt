"""Tests for Performance Tests Management from 10_Testing/Performance_Tests.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.performance_tests_service import (
    get_component_benchmarks,
    get_performance_suite_commands,
    benchmark_system_components,
)

client = TestClient(app)


def test_component_benchmarks():
    bm = get_component_benchmarks()
    assert bm["total_components"] == 7
    comp_names = [b["component"] for b in bm["benchmarks"]]
    assert "MiniLM embedding" in comp_names
    assert "Emotion detection" in comp_names
    assert "Groq API call" in comp_names
    assert "Qdrant search" in comp_names
    assert "Re-ranking" in comp_names
    assert "Redis GET" in comp_names
    assert "Full pipeline" in comp_names


def test_performance_suite_commands():
    cmds = get_performance_suite_commands()
    assert len(cmds) == 2
    cmd_strs = [c["command"] for c in cmds]
    assert any("--durations=10" in c for c in cmd_strs)
    assert any("--tb=short" in c for c in cmd_strs)


def test_benchmark_system_components():
    res = benchmark_system_components()
    assert res["status"] in ("PASS", "WARNING")
    assert "embedding_ms" in res["benchmarks"]
    assert "emotion_detection_ms" in res["benchmarks"]
    assert "rule_engine_ms" in res["benchmarks"]
    assert "rerank_batch_ms" in res["benchmarks"]


def test_performance_testing_api_endpoints():
    res_bm = client.get("/api/v1/test/performance/benchmarks")
    assert res_bm.status_code == 200
    assert res_bm.json()["total_components"] == 7

    res_cmd = client.get("/api/v1/test/performance/commands")
    assert res_cmd.status_code == 200
    assert len(res_cmd.json()["commands"]) == 2

    res_run = client.post("/api/v1/test/performance/run-live-benchmark")
    assert res_run.status_code == 200
    assert "benchmarks" in res_run.json()
