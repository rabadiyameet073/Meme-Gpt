"""Tests for Changelog & Version History from 17_Appendix/Changelog.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.changelog_service import (
    get_all_releases,
    get_release_by_version,
    get_latest_release,
    search_changelog,
    get_changelog_summary,
    evaluate_version_upgrade,
)

client = TestClient(app)


def test_get_all_releases():
    all_releases = get_all_releases()
    assert all_releases["total_releases"] == 4

    released = get_all_releases(status="RELEASED")
    assert released["total_releases"] == 1
    assert released["releases"][0]["version"] == "v1.0.0"

    planned = get_all_releases(status="PLANNED")
    assert planned["total_releases"] == 3


def test_get_release_by_version():
    v1 = get_release_by_version("v1.0.0")
    assert v1 is not None
    assert v1["status"] == "RELEASED"
    assert len(v1["sections"]["features"]) == 10
    assert len(v1["sections"]["architecture"]) == 5
    assert len(v1["sections"]["deployment"]) == 4

    v1_no_v = get_release_by_version("1.0.0")
    assert v1_no_v is not None
    assert v1_no_v["version"] == "v1.0.0"

    v11 = get_release_by_version("v1.1.0")
    assert v11 is not None
    assert v11["status"] == "PLANNED"
    assert any("Expo" in p for p in v11["sections"]["planned"])

    assert get_release_by_version("v9.9.9") is None


def test_get_latest_release():
    latest = get_latest_release()
    assert latest["latest_version"] == "v1.0.0"
    assert latest["release_date"] == "2026-01-15"


def test_search_changelog():
    res_groq = search_changelog("Groq")
    assert res_groq["total_matching_releases"] >= 1

    res_fastapi = search_changelog("FastAPI")
    assert res_fastapi["total_matching_releases"] >= 1

    res_expo = search_changelog("Expo")
    assert res_expo["total_matching_releases"] >= 1


def test_get_changelog_summary():
    summary = get_changelog_summary()
    assert summary["total_tracked_releases"] == 4
    assert summary["released_versions_count"] == 1
    assert summary["planned_versions_count"] == 3
    assert summary["initial_release_features_count"] == 10
    assert summary["future_roadmap_milestones_count"] == 16


def test_evaluate_version_upgrade():
    minor_upgrade = evaluate_version_upgrade("v1.0.0", "v1.1.0")
    assert minor_upgrade["is_major_breaking_upgrade"] is False
    assert minor_upgrade["upgrade_type"] == "MINOR"
    assert minor_upgrade["intervening_releases_count"] == 1

    major_upgrade = evaluate_version_upgrade("v1.0.0", "v2.0.0")
    assert major_upgrade["is_major_breaking_upgrade"] is True
    assert major_upgrade["upgrade_type"] == "MAJOR"
    assert major_upgrade["intervening_releases_count"] == 3
    assert "v1.1.0" in major_upgrade["intervening_releases"]
    assert "v1.2.0" in major_upgrade["intervening_releases"]
    assert "v2.0.0" in major_upgrade["intervening_releases"]


def test_appendix_changelog_api_endpoints():
    res_all = client.get("/api/v1/appendix/changelog")
    assert res_all.status_code == 200
    assert res_all.json()["total_releases"] == 4

    res_filter = client.get("/api/v1/appendix/changelog?status=PLANNED")
    assert res_filter.status_code == 200
    assert res_filter.json()["total_releases"] == 3

    res_latest = client.get("/api/v1/appendix/changelog/latest")
    assert res_latest.status_code == 200
    assert res_latest.json()["latest_version"] == "v1.0.0"

    res_sum = client.get("/api/v1/appendix/changelog/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["total_tracked_releases"] == 4

    res_search = client.get("/api/v1/appendix/changelog/search?q=Dark%20mode")
    assert res_search.status_code == 200
    assert res_search.json()["total_matching_releases"] >= 1

    res_single = client.get("/api/v1/appendix/changelog/v1.0.0")
    assert res_single.status_code == 200
    assert res_single.json()["release"]["version"] == "v1.0.0"

    res_404 = client.get("/api/v1/appendix/changelog/v9.9.9")
    assert res_404.status_code == 404

    res_upgrade = client.post(
        "/api/v1/appendix/changelog/upgrade-path",
        json={"current_version": "v1.0.0", "target_version": "v1.2.0"},
    )
    assert res_upgrade.status_code == 200
    assert res_upgrade.json()["upgrade_type"] == "MINOR"
    assert res_upgrade.json()["intervening_releases_count"] == 2
