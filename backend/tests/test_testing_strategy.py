"""Tests for Testing Strategy & Section 10 Manifest from 10_Testing/README.md & Testing_Strategy.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.testing_strategy_service import (
    get_testing_section_manifest,
    get_testing_pyramid,
    get_testing_best_practices,
    get_testing_system_health,
)

client = TestClient(app)


def test_testing_section_manifest():
    manifest = get_testing_section_manifest()
    assert manifest["section_id"] == "10_Testing"
    assert manifest["total_documents"] == 7
    doc_files = [d["filename"] for d in manifest["documents"]]
    assert "AI_Evaluation.md" in doc_files
    assert "Backend_Tests.md" in doc_files
    assert "Frontend_Tests.md" in doc_files
    assert "Load_Tests.md" in doc_files
    assert "Performance_Tests.md" in doc_files
    assert "README.md" in doc_files
    assert "Testing_Strategy.md" in doc_files


def test_testing_pyramid():
    pyr = get_testing_pyramid()
    assert pyr["total_layers"] == 6
    layers = [p["layer"] for p in pyr["pyramid"]]
    assert "Unit Tests" in layers
    assert "Integration Tests" in layers
    assert "Performance Tests" in layers
    assert "Load Tests (Locust)" in layers
    assert "ML Evaluation" in layers


def test_testing_best_practices():
    practices = get_testing_best_practices()
    assert len(practices) == 6
    assert any("happy path" in p["title"].lower() for p in practices)
    assert any("mock" in p["title"].lower() for p in practices)
    assert any("staging" in p["title"].lower() for p in practices)


def test_testing_system_health():
    health = get_testing_system_health()
    assert health["status"] == "healthy"
    assert health["total_modules"] >= 5
    assert health["checks"]["ai_evaluation"]["status"] == "healthy"
    assert health["checks"]["backend_tests"]["status"] == "healthy"
    assert health["checks"]["frontend_tests"]["status"] == "healthy"
    assert health["checks"]["load_tests"]["status"] == "healthy"
    assert health["checks"]["performance_tests"]["status"] == "healthy"


def test_testing_strategy_api_endpoints():
    res_m = client.get("/api/v1/test/manifest")
    assert res_m.status_code == 200
    assert res_m.json()["total_documents"] == 7

    res_p = client.get("/api/v1/test/pyramid")
    assert res_p.status_code == 200
    assert res_p.json()["total_layers"] == 6

    res_bp = client.get("/api/v1/test/practices")
    assert res_bp.status_code == 200
    assert len(res_bp.json()["practices"]) == 6

    res_h = client.get("/api/v1/test/health")
    assert res_h.status_code == 200
    assert res_h.json()["status"] == "healthy"
