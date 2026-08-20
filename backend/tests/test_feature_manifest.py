"""Tests for Features Section Manifest from 08_Features/README.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.feature_manifest_service import (
    get_features_section_manifest,
    get_feature_by_id,
    verify_feature_system_health,
)

client = TestClient(app)


def test_features_section_manifest():
    manifest = get_features_section_manifest()
    assert manifest["section_id"] == "08_Features"
    assert len(manifest["features"]) >= 4

    feature_ids = [f["id"] for f in manifest["features"]]
    assert "smart_search" in feature_ids
    assert "multi_format" in feature_ids
    assert "favorites_collections" in feature_ids
    assert "copy_download" in feature_ids
    assert "chat_refinement" in feature_ids


def test_get_feature_by_id_and_health():
    feat = get_feature_by_id("smart_search")
    assert feat is not None
    assert feat["name"] == "Smart Meme Search"
    assert feat["document"] == "Smart_Meme_Search.md"

    feat_dash = get_feature_by_id("copy-download")
    assert feat_dash is not None
    assert feat_dash["id"] == "copy_download"

    health = verify_feature_system_health()
    assert health["all_healthy"] is True
    assert health["total_features"] > 0


def test_features_api_endpoints():
    res = client.get("/api/v1/features")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["features"]) >= 4

    res_single = client.get("/api/v1/features/multi_format")
    assert res_single.status_code == 200
    assert res_single.json()["feature"]["name"] == "Multi-Format Support"

    res_health = client.get("/api/v1/features/health")
    assert res_health.status_code == 200
    assert res_health.json()["all_healthy"] is True
