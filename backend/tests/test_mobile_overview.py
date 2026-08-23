"""Tests for Mobile Application Specifications from 15_Mobile/Mobile_Overview.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.mobile_service import (
    get_mobile_tech_stack,
    get_mobile_architecture,
    get_platform_differences,
    get_build_and_release_workflows,
    get_app_size_budget,
    get_mobile_features_catalog,
    simulate_mobile_offline_sync,
    evaluate_mobile_app_readiness,
)

client = TestClient(app)


def test_mobile_tech_stack():
    res = get_mobile_tech_stack()
    assert res["total_technologies"] == 5
    names = [t["technology"] for t in res["stack"]]
    assert "React Native" in names
    assert "Expo" in names
    assert "Expo Router" in names
    assert "EAS Build" in names
    assert "Hermes" in names


def test_mobile_architecture():
    res = get_mobile_architecture()
    assert res["total_screens"] == 4
    screens = [s["screen"] for s in res["screens"]]
    assert "SearchScreen" in screens
    assert "TrendingScreen" in screens
    assert "LibraryScreen" in screens
    assert "SettingsScreen" in screens

    assert res["total_native_apis"] == 4
    apis = [a["module"] for a in res["native_apis"]]
    assert "expo-sharing" in apis
    assert "expo-media-library" in apis
    assert "expo-haptics" in apis
    assert "expo-clipboard" in apis


def test_platform_differences():
    res = get_platform_differences()
    assert res["total_differences"] == 6
    features = [d["feature"] for d in res["differences"]]
    assert "Share sheet" in features
    assert "Save to camera roll" in features
    assert "Haptic feedback" in features
    assert "Push notifications" in features
    assert "App binary size" in features
    assert "Minimum supported OS" in features


def test_build_and_release_workflows():
    res = get_build_and_release_workflows()
    assert "development" in res
    assert "npx expo start" in res["development"]["start_server"]
    assert "production_eas_build" in res
    assert "eas build --platform ios" in res["production_eas_build"]["build_ios"]
    assert "store_submission" in res
    assert "eas submit --platform android" in res["store_submission"]["submit_android"]


def test_app_size_budget():
    res = get_app_size_budget()
    assert res["total_size_mb"] == 29.0
    assert res["target_maximum_mb"] == 35.0
    assert res["budget_status"] == "WITHIN_BUDGET"


def test_mobile_features_catalog():
    res = get_mobile_features_catalog()
    assert res["total_features"] == 7
    assert res["priority_breakdown"]["P0_critical"] == 2
    assert res["priority_breakdown"]["P1_high"] == 4
    assert res["priority_breakdown"]["P2_medium"] == 1


def test_simulate_mobile_offline_sync():
    # Cache under 50
    items_30 = [{"id": f"meme_{i}", "name": f"Meme {i}"} for i in range(30)]
    res_under = simulate_mobile_offline_sync(items_30, max_cache_size=50)
    assert res_under["retained_memes_count"] == 30
    assert res_under["evicted_memes_count"] == 0
    assert res_under["cache_status"] == "CACHE_OPTIMAL"

    # Cache exceeding 50 (e.g. 70 items)
    items_70 = [{"id": f"meme_{i}", "name": f"Meme {i}"} for i in range(70)]
    res_over = simulate_mobile_offline_sync(items_70, max_cache_size=50)
    assert res_over["retained_memes_count"] == 50
    assert res_over["evicted_memes_count"] == 20
    assert res_over["cache_status"] == "CACHE_TRIMMED_LRU"
    assert res_over["retained_memes"][0]["id"] == "meme_20"


def test_evaluate_mobile_app_readiness():
    res = evaluate_mobile_app_readiness()
    assert res["status"] == "READY"
    assert res["ready_for_phase_2"] is True
    assert all(res["checks"].values())


def test_mobile_api_endpoints():
    res_stack = client.get("/api/v1/mobile/stack")
    assert res_stack.status_code == 200
    assert res_stack.json()["total_technologies"] == 5

    res_arch = client.get("/api/v1/mobile/architecture")
    assert res_arch.status_code == 200
    assert res_arch.json()["total_screens"] == 4

    res_plat = client.get("/api/v1/mobile/platforms")
    assert res_plat.status_code == 200
    assert res_plat.json()["total_differences"] == 6

    res_bld = client.get("/api/v1/mobile/build-release")
    assert res_bld.status_code == 200
    assert "production_eas_build" in res_bld.json()

    res_sz = client.get("/api/v1/mobile/size-budget")
    assert res_sz.status_code == 200
    assert res_sz.json()["total_size_mb"] == 29.0

    res_feat = client.get("/api/v1/mobile/features")
    assert res_feat.status_code == 200
    assert res_feat.json()["total_features"] == 7

    res_sync = client.post(
        "/api/v1/mobile/offline-sync",
        json={
            "cached_memes": [{"id": f"m_{i}"} for i in range(60)],
            "max_cache_size": 50,
        },
    )
    assert res_sync.status_code == 200
    assert res_sync.json()["retained_memes_count"] == 50

    res_rdy = client.get("/api/v1/mobile/readiness")
    assert res_rdy.status_code == 200
    assert res_rdy.json()["ready_for_phase_2"] is True
