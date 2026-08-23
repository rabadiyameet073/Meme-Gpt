"""Tests for Roadmap & Milestones from 13_Project_Management/Roadmap.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.roadmap_service import (
    get_roadmap_phases,
    get_roadmap_phase_by_id,
    get_roadmap_gantt_chart,
    get_success_metrics_by_phase,
    evaluate_phase_readiness,
)

client = TestClient(app)


def test_get_roadmap_phases():
    res = get_roadmap_phases()
    assert res["total_phases"] == 4
    assert len(res["phases"]) == 4
    names = [p["name"] for p in res["phases"]]
    assert "Phase 1: MVP" in names
    assert "Phase 2: Growth" in names
    assert "Phase 3: Scale" in names
    assert "Phase 4: Expand" in names


def test_get_roadmap_phase_by_id():
    # Phase 1
    p1 = get_roadmap_phase_by_id(1)
    assert p1 is not None
    assert p1["name"] == "Phase 1: MVP"
    assert p1["status"] == "COMPLETED"
    assert p1["total_features"] == 10
    assert p1["completed_features"] == 10
    assert p1["progress_percentage"] == 100.0

    # Phase 2
    p2 = get_roadmap_phase_by_id(2)
    assert p2 is not None
    assert p2["name"] == "Phase 2: Growth"
    assert p2["total_features"] == 7
    priorities = [f["priority"] for f in p2["features"]]
    assert "P0" in priorities

    # Invalid phase
    assert get_roadmap_phase_by_id(5) is None


def test_get_roadmap_gantt_chart():
    gantt = get_roadmap_gantt_chart()
    assert "title" in gantt
    assert len(gantt["sections"]) == 4
    section_names = [s["section"] for s in gantt["sections"]]
    assert "Phase 1 — MVP" in section_names
    assert "Phase 2 — Growth" in section_names


def test_get_success_metrics_by_phase():
    res = get_success_metrics_by_phase()
    assert res["total_phases"] == 4
    p1_metrics = next(p for p in res["phases_metrics"] if p["phase_id"] == 1)
    assert p1_metrics["metrics"]["dau_target"] == "1,000 DAU"


def test_evaluate_phase_readiness():
    # Phase 1 is 100% complete
    r1 = evaluate_phase_readiness(1)
    assert r1["success"] is True
    assert r1["is_ready_for_next_phase"] is True
    assert r1["status"] == "PHASE_COMPLETE"

    # Phase 2 is in development
    r2 = evaluate_phase_readiness(2)
    assert r2["success"] is True
    assert r2["is_ready_for_next_phase"] is False
    assert r2["status"] == "PHASE_IN_DEVELOPMENT"


def test_roadmap_api_endpoints():
    res_phases = client.get("/api/v1/project-management/roadmap/phases")
    assert res_phases.status_code == 200
    assert res_phases.json()["total_phases"] == 4

    res_p1 = client.get("/api/v1/project-management/roadmap/phases/1")
    assert res_p1.status_code == 200
    assert res_p1.json()["phase"]["name"] == "Phase 1: MVP"

    res_gantt = client.get("/api/v1/project-management/roadmap/gantt")
    assert res_gantt.status_code == 200
    assert "sections" in res_gantt.json()

    res_metrics = client.get("/api/v1/project-management/roadmap/metrics")
    assert res_metrics.status_code == 200
    assert len(res_metrics.json()["phases_metrics"]) == 4

    res_readiness = client.get("/api/v1/project-management/roadmap/readiness/1")
    assert res_readiness.status_code == 200
    assert res_readiness.json()["is_ready_for_next_phase"] is True
