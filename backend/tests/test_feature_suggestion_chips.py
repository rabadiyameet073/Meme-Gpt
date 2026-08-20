"""Tests for Suggestion Chips feature from 08_Features/Suggestion_Chips.md."""

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.services.suggestion_chips_service import (
    get_static_suggestion_chips,
    get_dynamic_time_based_chips,
    get_active_suggestion_chips,
)

client = TestClient(app)


def test_static_suggestion_chips_catalog():
    chips = get_static_suggestion_chips()
    assert len(chips) == 8

    labels = [c["label"] for c in chips]
    assert "🤦 Monday vibe" in labels
    assert "😤 Frustration" in labels
    assert "🎉 Win" in labels
    assert "💻 Programmer life" in labels
    assert "🏠 WFH" in labels
    assert "😴 Tired" in labels
    assert "🔥 Savage" in labels
    assert "💀 Dead" in labels


def test_dynamic_time_based_chips():
    # Monday 8 AM
    mon_morning = datetime(2026, 8, 3, 8, 0, tzinfo=timezone.utc)  # Aug 3, 2026 is Monday
    mon_chips = get_dynamic_time_based_chips(mon_morning)
    assert len(mon_chips) == 3
    assert any("Monday morning" in c["label"] for c in mon_chips)

    # Friday 4 PM
    fri_afternoon = datetime(2026, 8, 7, 16, 0, tzinfo=timezone.utc)  # Aug 7, 2026 is Friday
    fri_chips = get_dynamic_time_based_chips(fri_afternoon)
    assert len(fri_chips) == 3
    assert any("Friday feeling" in c["label"] for c in fri_chips)

    # Saturday 12 PM
    sat_noon = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)  # Aug 8, 2026 is Saturday
    sat_chips = get_dynamic_time_based_chips(sat_noon)
    assert len(sat_chips) == 3
    assert any("Weekend vibes" in c["label"] for c in sat_chips)


def test_get_active_suggestion_chips_limits():
    # Test capping at 8 max
    active_8 = get_active_suggestion_chips(limit=8)
    assert len(active_8) <= 8
    assert len(active_8) >= 5

    # Test limit capping at minimum 5
    active_5 = get_active_suggestion_chips(limit=3)
    assert len(active_5) == 5


def test_chips_api_endpoints():
    res_sugg = client.get("/api/v1/chips/suggestions?limit=6")
    assert res_sugg.status_code == 200
    data = res_sugg.json()
    assert data["success"] is True
    assert len(data["chips"]) == 6

    res_cat = client.get("/api/v1/chips/catalog")
    assert res_cat.status_code == 200
    assert len(res_cat.json()["static_chips"]) == 8
    assert len(res_cat.json()["time_based_rules"]) == 4
