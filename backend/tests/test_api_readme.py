"""Tests for APIs Section README from 07_APIs/README.md."""

from app.main import app
from app.services.api_service import (
    get_api_section_manifest,
    verify_api_routes_registration,
)


def test_api_section_manifest():
    manifest = get_api_section_manifest()
    assert manifest["section"] == "07_APIs"
    assert manifest["title"] == "APIs"
    assert manifest["previous_section"] == "06_Database"
    assert manifest["next_section"] == "08_Features"

    doc_names = {d["name"] for d in manifest["documents"]}
    expected_docs = {
        "API_Overview.md",
        "Search_API.md",
        "Meme_API.md",
        "Trending_API.md",
        "Feedback_API.md",
        "Rate_Limiting.md",
        "Authentication.md",
        "Webhooks.md",
        "README.md",
    }
    assert expected_docs.issubset(doc_names)


def test_verify_api_routes_registration():
    result = verify_api_routes_registration(app)
    assert result["total_expected"] == 7
    assert result["all_mounted"] is True
    assert result["coverage"]["/api/v1/search"] is True
    assert result["coverage"]["/api/v1/trending"] is True
    assert result["coverage"]["/api/v1/feedback"] is True
    assert result["coverage"]["/health"] is True
