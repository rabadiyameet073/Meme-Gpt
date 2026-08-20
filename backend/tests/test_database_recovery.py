"""Tests for Database Recovery Procedures and Scenarios from 06_Database/Recovery.md."""

from app.services.recovery_service import (
    get_recovery_scenarios_catalog,
    get_recovery_checklist,
    execute_recovery_dry_run,
    verify_post_recovery_system_state,
)


def test_get_recovery_scenarios_catalog():
    catalog = get_recovery_scenarios_catalog()
    assert "scenarios" in catalog
    scenarios = catalog["scenarios"]

    # Scenario 1: Supabase Database Corrupted
    assert "1" in scenarios
    assert "Supabase Database Corrupted" in scenarios["1"]["title"]
    assert "~5 minutes" in scenarios["1"]["recovery_time"]
    assert "Up to 24 hours" in scenarios["1"]["data_loss"]

    # Scenario 2: Qdrant Index Lost
    assert "2" in scenarios
    assert "Qdrant Index Lost" in scenarios["2"]["title"]
    assert "~30 minutes" in scenarios["2"]["recovery_time"]
    assert scenarios["2"]["data_loss"] == "None (regenerated from source)"

    # Scenario 3: R2 Media Files Lost
    assert "3" in scenarios
    assert "R2 Media Files Lost" in scenarios["3"]["title"]
    assert "~1 hour" in scenarios["3"]["recovery_time"]

    # Scenario 4: Full Disaster Recovery
    assert "4" in scenarios
    assert "Full Disaster Recovery" in scenarios["4"]["title"]
    assert "~2 hours" in scenarios["4"]["recovery_time"]


def test_get_recovery_checklist():
    checklist = get_recovery_checklist()
    assert len(checklist) == 7
    assert any("database restored" in item.lower() for item in checklist)
    assert any("qdrant collection" in item.lower() for item in checklist)
    assert any("cdn images" in item.lower() for item in checklist)
    assert any("health endpoint" in item.lower() for item in checklist)


def test_execute_recovery_dry_runs():
    for sc_id in [1, 2, 3, 4]:
        res = execute_recovery_dry_run(sc_id)
        assert res["status"] == "dry_run_completed"
        assert res["scenario_id"] == sc_id
        assert res["steps_executed"] >= 2
        for step in res["step_details"]:
            assert step["status"] == "simulated_success"

    invalid_res = execute_recovery_dry_run(99)
    assert invalid_res["status"] == "error"


def test_verify_post_recovery_system_state():
    state = verify_post_recovery_system_state()
    assert state["status"] in ["healthy", "degraded"]
    assert state["all_checks_passed"] is True
