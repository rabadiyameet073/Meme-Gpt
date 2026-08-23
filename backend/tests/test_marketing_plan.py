"""Tests for Marketing Plan & Growth Funnel from 16_SEO_Marketing/Marketing_Plan.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.marketing_plan_service import (
    get_marketing_funnel,
    get_channel_strategy,
    get_reddit_targets,
    get_product_hunt_playbook,
    get_content_calendar,
    simulate_viral_growth,
)

client = TestClient(app)


def test_marketing_funnel():
    funnel = get_marketing_funnel()
    assert funnel["total_phases"] == 4
    assert funnel["target_dau_milestone"] == 50000

    phases = funnel["phases"]
    assert phases[0]["phase"] == 1
    assert phases[0]["target_dau"] == 100
    assert phases[1]["phase"] == 2
    assert phases[1]["target_dau"] == 1000
    assert phases[2]["phase"] == 3
    assert phases[2]["target_dau"] == 5000
    assert phases[3]["phase"] == 4
    assert phases[3]["target_dau"] == 50000


def test_channel_strategy():
    strategy = get_channel_strategy()
    assert strategy["total_channels"] == 5
    assert "$0" in strategy["total_budget"]

    channels = strategy["channels"]
    total_pct = sum(c["expected_traffic_percentage"] for c in channels)
    assert total_pct == 100

    names = [c["channel"] for c in channels]
    assert "SEO" in names
    assert "App Store (ASO)" in names
    assert "Word of mouth" in names
    assert "Content marketing" in names
    assert "Developer API" in names


def test_reddit_targets():
    reddit = get_reddit_targets()
    assert reddit["total_subreddits"] == 5
    assert "22.85M" in reddit["aggregate_audience_reach"]

    subs = [s["subreddit"] for s in reddit["subreddits"]]
    assert "r/SideProject" in subs
    assert "r/InternetIsBeautiful" in subs
    assert "r/webdev" in subs
    assert "r/ProgrammerHumor" in subs
    assert "r/artificial" in subs


def test_product_hunt_playbook():
    ph = get_product_hunt_playbook()
    assert ph["target_launch_day"] == "Tuesday"
    assert len(ph["submission_assets"]) == 4
    assert "Top 5" in ph["target_ranking"]
    assert "1 hour" in ph["community_response_sla"]


def test_content_calendar():
    calendar = get_content_calendar()
    assert calendar["total_content_drops"] == 6
    weeks = [c["week"] for c in calendar["schedule"]]
    assert "Week 1" in weeks
    assert "Week 2" in weeks
    assert "Week 3" in weeks
    assert "Week 4" in weeks


def test_simulate_viral_growth():
    sim = simulate_viral_growth(initial_dau=100, viral_k_factor=1.15, days=30)
    assert sim["initial_dau"] == 100
    assert sim["viral_k_factor"] == 1.15
    assert sim["final_projected_dau"] > 100
    assert len(sim["trajectory_milestones"]) == 5


def test_marketing_plan_api_endpoints():
    res_funnel = client.get("/api/v1/marketing/plan/funnel")
    assert res_funnel.status_code == 200
    assert res_funnel.json()["total_phases"] == 4

    res_channels = client.get("/api/v1/marketing/plan/channels")
    assert res_channels.status_code == 200
    assert res_channels.json()["total_channels"] == 5

    res_reddit = client.get("/api/v1/marketing/plan/reddit")
    assert res_reddit.status_code == 200
    assert res_reddit.json()["total_subreddits"] == 5

    res_ph = client.get("/api/v1/marketing/plan/product-hunt")
    assert res_ph.status_code == 200
    assert res_ph.json()["target_launch_day"] == "Tuesday"

    res_cal = client.get("/api/v1/marketing/plan/content-calendar")
    assert res_cal.status_code == 200
    assert res_cal.json()["total_content_drops"] == 6

    res_growth = client.post(
        "/api/v1/marketing/plan/simulate-growth",
        json={"initial_dau": 200, "viral_k_factor": 1.20, "days": 30},
    )
    assert res_growth.status_code == 200
    assert res_growth.json()["final_projected_dau"] > 200
