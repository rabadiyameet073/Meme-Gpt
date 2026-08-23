"""Tests for Scaling Strategy & Capacity Planning from 12_Deployment/Scaling.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.scaling_service import (
    get_scaling_phases,
    get_scaling_triggers,
    get_cost_projections,
    get_component_scaling_strategies,
    get_scaling_best_practices,
    calculate_projected_cost,
    evaluate_scaling_triggers,
)

client = TestClient(app)


def test_scaling_phases():
    res = get_scaling_phases()
    assert res["total_phases"] == 4
    phases = [p["phase"] for p in res["phases"]]
    assert "Phase 1: MVP" in phases
    assert "Phase 2: Growth" in phases
    assert "Phase 3: Scale" in phases
    assert "Phase 4: Enterprise" in phases


def test_scaling_triggers():
    res = get_scaling_triggers()
    assert res["total_triggers"] == 6
    metrics = [t["metric"] for t in res["triggers"]]
    assert "Qdrant vectors" in metrics
    assert "Redis commands" in metrics
    assert "API response time P95" in metrics
    assert "Database size" in metrics
    assert "CDN bandwidth" in metrics
    assert "Concurrent users" in metrics


def test_cost_projections():
    res = get_cost_projections()
    assert res["total_tiers"] == 6
    projections = res["projections"]
    tier_100 = next(p for p in projections if p["dau"] == 100)
    assert tier_100["total"] == 0

    tier_10k = next(p for p in projections if p["dau"] == 10000)
    assert tier_10k["total"] == 42
    assert tier_10k["database"] == 25
    assert tier_10k["cache"] == 10

    tier_100k = next(p for p in projections if p["dau"] == 100000)
    assert tier_100k["total"] == 195


def test_component_scaling_strategies():
    strategies = get_component_scaling_strategies()
    assert "backend" in strategies
    assert "database" in strategies
    assert "vector_db" in strategies
    assert "cache" in strategies
    assert "gunicorn" in strategies["backend"]["scaled"]


def test_scaling_best_practices():
    res = get_scaling_best_practices()
    assert res["total_practices"] == 5
    titles = [p["title"] for p in res["practices"]]
    assert "Optimize before scaling" in titles
    assert "Scale vertically first" in titles
    assert "Monitor before acting" in titles
    assert "Cache aggressively" in titles
    assert "Free tier is your friend" in titles


def test_calculate_projected_cost():
    # 500 DAU -> $0
    c_500 = calculate_projected_cost(500)
    assert c_500["total_cost_numeric"] == 0
    assert c_500["lifecycle_phase"] == "Phase 1: MVP"

    # 10,000 DAU -> $42
    c_10k = calculate_projected_cost(10000)
    assert c_10k["total_cost_numeric"] == 42
    assert c_10k["lifecycle_phase"] == "Phase 2: Growth"

    # 100,000 DAU -> $195
    c_100k = calculate_projected_cost(100000)
    assert c_100k["total_cost_numeric"] == 195
    assert c_100k["lifecycle_phase"] == "Phase 3: Scale"


def test_evaluate_scaling_triggers():
    # Nominal case
    nominal = evaluate_scaling_triggers(
        vector_count=10000,
        daily_redis_commands=5000,
        p95_latency_seconds=1.2,
        db_size_mb=100.0,
        cdn_bandwidth_gb=5.0,
        concurrent_users=10,
    )
    assert nominal["status"] == "NOMINAL_CAPACITY"
    assert nominal["scaling_required"] is False
    assert nominal["total_triggered_actions"] == 0

    # High load case
    scaled = evaluate_scaling_triggers(
        vector_count=600000,
        daily_redis_commands=15000,
        p95_latency_seconds=3.5,
        db_size_mb=600.0,
        cdn_bandwidth_gb=15.0,
        concurrent_users=75,
    )
    assert scaled["status"] == "SCALING_REQUIRED"
    assert scaled["scaling_required"] is True
    assert scaled["total_triggered_actions"] == 6


def test_scaling_api_endpoints():
    res_phases = client.get("/api/v1/deployment/scaling/phases")
    assert res_phases.status_code == 200
    assert res_phases.json()["total_phases"] == 4

    res_trig = client.get("/api/v1/deployment/scaling/triggers")
    assert res_trig.status_code == 200
    assert res_trig.json()["total_triggers"] == 6

    res_costs = client.get("/api/v1/deployment/scaling/cost-projections")
    assert res_costs.status_code == 200
    assert res_costs.json()["total_tiers"] == 6

    res_strat = client.get("/api/v1/deployment/scaling/strategies")
    assert res_strat.status_code == 200
    assert "backend" in res_strat.json()

    res_prac = client.get("/api/v1/deployment/scaling/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 5

    res_calc = client.get("/api/v1/deployment/scaling/estimate-cost?dau=10000")
    assert res_calc.status_code == 200
    assert res_calc.json()["total_cost_numeric"] == 42

    res_eval = client.post(
        "/api/v1/deployment/scaling/evaluate-triggers",
        json={
            "vector_count": 10000,
            "daily_redis_commands": 5000,
            "p95_latency_seconds": 1.2,
            "db_size_mb": 100.0,
            "cdn_bandwidth_gb": 5.0,
            "concurrent_users": 10,
        },
    )
    assert res_eval.status_code == 200
    assert res_eval.json()["status"] == "NOMINAL_CAPACITY"
