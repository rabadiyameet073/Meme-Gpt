"""Tests for Infrastructure Service & Endpoints from 12_Deployment/Infrastructure.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.infrastructure_service import (
    get_infrastructure_topology,
    get_service_inventory,
    get_networking_matrix,
    get_infrastructure_best_practices,
    evaluate_infrastructure_capacity_and_health,
)

client = TestClient(app)


def test_infrastructure_topology():
    topo = get_infrastructure_topology()
    assert "layers" in topo
    assert len(topo["layers"]) == 4
    layer_names = [l["layer"] for l in topo["layers"]]
    assert "Edge Layer (Global)" in layer_names
    assert "Application Layer (US-East)" in layer_names
    assert "Data Layer (US-East)" in layer_names
    assert "External Services" in layer_names


def test_service_inventory():
    inv = get_service_inventory()
    assert inv["total_services"] == 13
    assert inv["total_monthly_cost"] == "$0–$7"
    services = [s["service"] for s in inv["inventory"]]
    assert "Frontend hosting" in services
    assert "Backend hosting" in services
    assert "PostgreSQL" in services
    assert "Vector DB" in services
    assert "Cache" in services
    assert "Object storage" in services
    assert "LLM inference" in services
    assert "Error tracking" in services
    assert "Analytics" in services
    assert "Uptime monitoring" in services
    assert "CI/CD" in services
    assert "DNS" in services
    assert "Domain" in services


def test_networking_matrix():
    matrix = get_networking_matrix()
    assert matrix["total_connections"] == 7
    for conn in matrix["connections"]:
        assert conn["encrypted"] is True
        assert "latency" in conn


def test_infrastructure_best_practices():
    res = get_infrastructure_best_practices()
    assert res["total_practices"] == 5
    titles = [p["title"] for p in res["practices"]]
    assert "Co-locate everything in US-East" in titles
    assert "Use free tiers aggressively" in titles
    assert "Monitor all services" in titles
    assert "Plan upgrades at 80% capacity" in titles
    assert "No single points of failure" in titles


def test_infrastructure_capacity_and_health():
    health = evaluate_infrastructure_capacity_and_health()
    assert health["status"] == "HEALTHY"
    assert health["all_traffic_encrypted"] is True
    assert health["capacity_alert_threshold"] == "80%"
    assert health["service_count"] == 13


def test_infrastructure_api_endpoints():
    res_topo = client.get("/api/v1/deployment/infrastructure/topology")
    assert res_topo.status_code == 200
    assert len(res_topo.json()["layers"]) == 4

    res_inv = client.get("/api/v1/deployment/infrastructure/inventory")
    assert res_inv.status_code == 200
    assert res_inv.json()["total_services"] == 13

    res_net = client.get("/api/v1/deployment/infrastructure/networking")
    assert res_net.status_code == 200
    assert res_net.json()["total_connections"] == 7

    res_prac = client.get("/api/v1/deployment/infrastructure/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 5

    res_hlth = client.get("/api/v1/deployment/infrastructure/health")
    assert res_hlth.status_code == 200
    assert res_hlth.json()["status"] == "HEALTHY"
