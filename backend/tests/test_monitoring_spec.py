"""Tests for Monitoring, Telemetry, and Alerting from 12_Deployment/Monitoring.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.monitoring_service import (
    get_monitoring_stack,
    get_uptimerobot_config,
    get_sentry_config_spec,
    get_key_metrics_dashboard,
    get_monitoring_best_practices,
    get_standard_health_response,
    evaluate_live_metrics_and_alerts,
)

client = TestClient(app)


def test_monitoring_stack():
    res = get_monitoring_stack()
    assert res["total_tools"] == 4
    tools = [t["tool"] for t in res["stack"]]
    assert "UptimeRobot" in tools
    assert "Sentry" in tools
    assert "Umami" in tools
    assert "Railway Logs" in tools


def test_uptimerobot_config():
    res = get_uptimerobot_config()
    assert res["total_monitors"] == 3
    monitors = [m["monitor"] for m in res["monitors"]]
    assert "API Health" in monitors
    assert "Web App" in monitors
    assert "Search Endpoint" in monitors


def test_sentry_config_spec():
    spec = get_sentry_config_spec()
    assert "sdk_init" in spec
    assert spec["sdk_init"]["send_default_pii"] is False
    assert spec["sdk_init"]["traces_sample_rate"] == 0.1
    assert len(spec["alert_rules"]) == 4


def test_key_metrics_dashboard():
    dash = get_key_metrics_dashboard()
    assert dash["total_metrics"] == 7
    metrics = [m["metric"] for m in dash["dashboard"]]
    assert "Uptime" in metrics
    assert "Error rate" in metrics
    assert "P50 latency" in metrics
    assert "P95 latency" in metrics
    assert "Cache hit rate" in metrics
    assert "Search volume" in metrics
    assert "Daily active users" in metrics


def test_monitoring_best_practices():
    res = get_monitoring_best_practices()
    assert res["total_practices"] == 5
    titles = [p["title"] for p in res["practices"]]
    assert "Monitor externally" in titles
    assert "Set send_default_pii=False" in titles
    assert "Sample traces at 10%" in titles
    assert "Alert on error rate, not individual errors" in titles
    assert "Check health endpoint every 5 min" in titles


def test_standard_health_response():
    resp = get_standard_health_response()
    assert resp["status"] == "ok"
    assert resp["version"] == "1.0.0"
    assert "uptime_seconds" in resp
    assert resp["models"]["text_model"] == "loaded"
    assert resp["services"]["database"] == "connected"


def test_evaluate_live_metrics_and_alerts():
    # Healthy case
    healthy = evaluate_live_metrics_and_alerts(uptime=99.9, error_rate=0.5, p50_latency=0.45, p95_latency=1.8, cache_hit_rate=78.0)
    assert healthy["status"] == "HEALTHY"
    assert healthy["all_sla_targets_met"] is True
    assert healthy["total_violations"] == 0

    # Violation case
    degraded = evaluate_live_metrics_and_alerts(uptime=98.0, error_rate=7.5, p50_latency=2.5, p95_latency=6.0, cache_hit_rate=20.0)
    assert degraded["status"] == "ALERT_TRIGGERED"
    assert degraded["all_sla_targets_met"] is False
    assert degraded["total_violations"] == 5


def test_monitoring_api_endpoints():
    res_stack = client.get("/api/v1/deployment/monitoring/stack")
    assert res_stack.status_code == 200
    assert res_stack.json()["total_tools"] == 4

    res_ur = client.get("/api/v1/deployment/monitoring/uptimerobot")
    assert res_ur.status_code == 200
    assert res_ur.json()["total_monitors"] == 3

    res_sentry = client.get("/api/v1/deployment/monitoring/sentry")
    assert res_sentry.status_code == 200
    assert "alert_rules" in res_sentry.json()

    res_dash = client.get("/api/v1/deployment/monitoring/metrics-dashboard")
    assert res_dash.status_code == 200
    assert res_dash.json()["total_metrics"] == 7

    res_prac = client.get("/api/v1/deployment/monitoring/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 5

    res_schema = client.get("/api/v1/deployment/monitoring/health-schema")
    assert res_schema.status_code == 200
    assert res_schema.json()["schema"]["status"] == "ok"

    res_eval = client.post(
        "/api/v1/deployment/monitoring/evaluate-metrics",
        json={"uptime": 99.8, "error_rate": 1.2, "p50_latency": 0.5, "p95_latency": 1.9, "cache_hit_rate": 82.0},
    )
    assert res_eval.status_code == 200
    assert res_eval.json()["status"] == "HEALTHY"
