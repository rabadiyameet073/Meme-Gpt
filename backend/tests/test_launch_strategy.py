"""Tests for Launch Strategy from 16_SEO_Marketing/Launch_Strategy.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.launch_strategy_service import (
    get_launch_timeline,
    get_launch_channels,
    get_pre_launch_checklist,
    get_launch_day_schedule,
    get_launch_kpis,
    get_post_launch_priorities,
    evaluate_launch_readiness,
)

client = TestClient(app)


def test_launch_timeline():
    timeline = get_launch_timeline()
    assert len(timeline["phases"]) == 3
    phase_names = [p["phase"] for p in timeline["phases"]]
    assert "Pre-Launch (Week -2)" in phase_names
    assert "Launch Week" in phase_names
    assert "Post-Launch (Week +1 to +4)" in phase_names


def test_launch_channels():
    channels = get_launch_channels()
    assert channels["total_channels"] == 7
    names = [c["channel"] for c in channels["channels"]]
    assert "Product Hunt" in names
    assert "Reddit" in names
    assert "Twitter / X" in names
    assert "Hacker News" in names
    assert "Dev.to" in names
    assert "LinkedIn" in names
    assert "Instagram Reels" in names


def test_pre_launch_checklist():
    all_items = get_pre_launch_checklist()
    assert all_items["total_items"] == 18

    tech_items = get_pre_launch_checklist(category="technical")
    assert tech_items["total_items"] == 8

    content_items = get_pre_launch_checklist(category="content")
    assert content_items["total_items"] == 6

    seo_items = get_pre_launch_checklist(category="seo")
    assert seo_items["total_items"] == 4


def test_launch_day_schedule():
    schedule = get_launch_day_schedule()
    assert schedule["total_milestones"] == 10
    milestones = schedule["schedule"]
    assert milestones[0]["time"] == "08:00 AM"
    assert "Product Hunt" in milestones[0]["action"]
    assert milestones[-1]["time"] == "10:00 PM"
    assert "Sentry" in milestones[-1]["action"]


def test_launch_kpis():
    kpis = get_launch_kpis()
    assert kpis["total_kpis"] == 7
    metrics = [k["metric"] for k in kpis["kpis"]]
    assert "Unique visitors" in metrics
    assert "Searches performed" in metrics
    assert "Downloads & copies" in metrics
    assert "App Store downloads" in metrics
    assert "Product Hunt upvotes" in metrics
    assert "System error rate" in metrics
    assert "P95 response time" in metrics


def test_post_launch_priorities():
    priorities = get_post_launch_priorities()
    assert priorities["total_priorities"] == 5
    items = priorities["priorities"]
    assert items[0]["rank"] == 1
    assert "bugs" in items[0]["priority"].lower()
    assert items[1]["rank"] == 2
    assert "feature requests" in items[1]["priority"].lower()


def test_evaluate_launch_readiness():
    # All items ready
    full_eval = evaluate_launch_readiness()
    assert full_eval["launch_verdict"] == "READY_TO_LAUNCH"
    assert full_eval["readiness_percentage"] == "100.0%"
    assert full_eval["critical_gates"]["technical_readiness"] == "PASSED"
    assert full_eval["critical_gates"]["content_readiness"] == "PASSED"
    assert full_eval["critical_gates"]["seo_readiness"] == "PASSED"

    # Partial items ready
    partial_eval = evaluate_launch_readiness(checked_items=["CHK_TECH_BUGS", "CHK_TECH_PERF"])
    assert partial_eval["launch_verdict"] == "BLOCKED_GATES_OPEN"
    assert partial_eval["verified_checklist_items"] == 2
    assert partial_eval["remaining_items"] == 16


def test_marketing_launch_api_endpoints():
    res_timeline = client.get("/api/v1/marketing/launch/timeline")
    assert res_timeline.status_code == 200
    assert len(res_timeline.json()["phases"]) == 3

    res_channels = client.get("/api/v1/marketing/launch/channels")
    assert res_channels.status_code == 200
    assert res_channels.json()["total_channels"] == 7

    res_check = client.get("/api/v1/marketing/launch/checklist?category=seo")
    assert res_check.status_code == 200
    assert res_check.json()["total_items"] == 4

    res_sched = client.get("/api/v1/marketing/launch/schedule")
    assert res_sched.status_code == 200
    assert res_sched.json()["total_milestones"] == 10

    res_kpis = client.get("/api/v1/marketing/launch/kpis")
    assert res_kpis.status_code == 200
    assert res_kpis.json()["total_kpis"] == 7

    res_prior = client.get("/api/v1/marketing/launch/priorities")
    assert res_prior.status_code == 200
    assert res_prior.json()["total_priorities"] == 5

    res_eval = client.post(
        "/api/v1/marketing/launch/evaluate-readiness",
        json={"checked_items": ["CHK_TECH_BUGS", "CHK_TECH_PERF", "CHK_TECH_RATE_LIMIT"]},
    )
    assert res_eval.status_code == 200
    assert res_eval.json()["verified_checklist_items"] == 3
