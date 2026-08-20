"""Tests for Share Feature from 08_Features/Share_Feature.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.share_service import (
    generate_share_url,
    parse_share_url,
    get_share_analytics_weights,
    generate_opengraph_metadata,
)

client = TestClient(app)


def test_generate_and_parse_share_url():
    # URL without query ref
    url1 = generate_share_url("this-is-fine")
    assert url1 == "https://memegpt.com/meme/this-is-fine"
    parsed1 = parse_share_url(url1)
    assert parsed1["slug"] == "this-is-fine"
    assert parsed1["ref_query_id"] is None

    # URL with query ref
    url2 = generate_share_url("drake-pointing", query_id="q_xyz789")
    assert url2 == "https://memegpt.com/meme/drake-pointing?ref=q_xyz789"
    parsed2 = parse_share_url(url2)
    assert parsed2["slug"] == "drake-pointing"
    assert parsed2["ref_query_id"] == "q_xyz789"


def test_share_analytics_weights():
    weights = get_share_analytics_weights()
    assert weights["share"] == 3.0
    assert weights["copy_link"] == 1.0
    assert weights["copy_image"] == 1.0
    assert weights["share_cancelled"] == 0.0


def test_generate_opengraph_metadata():
    sample_meme = {
        "id": "meme_123",
        "slug": "this-is-fine",
        "name": "This is Fine",
        "explanation": "Dog sitting in burning room",
        "formats": {"image": "https://cdn.memegpt.com/images/this-is-fine.png"},
    }

    og = generate_opengraph_metadata(sample_meme, query_id="q_ref123")
    assert og["og:title"] == "This is Fine — MemeGPT"
    assert og["og:description"] == "Dog sitting in burning room"
    assert og["og:url"] == "https://memegpt.com/meme/this-is-fine?ref=q_ref123"
    assert og["og:image"] == "https://cdn.memegpt.com/images/this-is-fine.png"
    assert og["twitter:card"] == "summary_large_image"


def test_share_api_endpoints():
    res_url = client.get("/api/v1/share/url/this-is-fine?ref=q_test456")
    assert res_url.status_code == 200
    assert res_url.json()["share_url"] == "https://memegpt.com/meme/this-is-fine?ref=q_test456"

    res_parse = client.get("/api/v1/share/parse?url=https://memegpt.com/meme/distracted-bf?ref=q_999")
    assert res_parse.status_code == 200
    assert res_parse.json()["slug"] == "distracted-bf"
    assert res_parse.json()["ref_query_id"] == "q_999"

    res_weights = client.get("/api/v1/share/analytics-weights")
    assert res_weights.status_code == 200
    assert res_weights.json()["weights"]["share"] == 3.0
