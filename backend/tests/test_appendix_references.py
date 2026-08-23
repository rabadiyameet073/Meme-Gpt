"""Tests for External References & Citations from 17_Appendix/References.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.appendix_references_service import (
    get_all_quick_references,
    get_quick_reference_by_title,
    search_quick_references,
    get_quick_references_summary,
    validate_reference_links,
)

client = TestClient(app)


def test_get_all_quick_references():
    all_refs = get_all_quick_references()
    assert all_refs["total_references"] == 14
    ids = [r["id"] for r in all_refs["references"]]
    assert "fastapi" in ids
    assert "qdrant" in ids
    assert "minilm" in ids
    assert "clip" in ids
    assert "cloudflare_r2" in ids


def test_quick_references_category_filtering():
    core = get_all_quick_references(category="core_documentation")
    assert core["total_references"] == 5
    assert all(r["category"] == "core_documentation" for r in core["references"])

    ai = get_all_quick_references(category="ai_ml_models")
    assert ai["total_references"] == 5
    assert all(r["category"] == "ai_ml_models" for r in ai["references"])

    infra = get_all_quick_references(category="infrastructure")
    assert infra["total_references"] == 4
    assert all(r["category"] == "infrastructure" for r in infra["references"])


def test_get_quick_reference_by_title():
    ref_fastapi = get_quick_reference_by_title("fastapi")
    assert ref_fastapi is not None
    assert ref_fastapi["url"] == "https://fastapi.tiangolo.com"
    assert ref_fastapi["category"] == "core_documentation"

    ref_clip = get_quick_reference_by_title("CLIP ViT-B/32")
    assert ref_clip is not None
    assert "huggingface.co/openai/clip-vit-base-patch32" in ref_clip["url"]

    assert get_quick_reference_by_title("non_existent_doc_xyz") is None


def test_search_quick_references():
    res_hf = search_quick_references("huggingface")
    assert res_hf["total_matches"] >= 4

    res_groq = search_quick_references("Groq")
    assert res_groq["total_matches"] >= 1

    res_r2 = search_quick_references("egress")
    assert res_r2["total_matches"] >= 1
    assert any(r["id"] == "cloudflare_r2" for r in res_r2["matches"])


def test_get_quick_references_summary():
    summary = get_quick_references_summary()
    assert summary["total_references"] == 14
    assert summary["categories_count"] == 3
    assert summary["category_breakdown"]["core_documentation"] == 5
    assert summary["category_breakdown"]["ai_ml_models"] == 5
    assert summary["category_breakdown"]["infrastructure"] == 4


def test_validate_reference_links():
    val = validate_reference_links()
    assert val["total_links_validated"] == 14
    assert val["valid_count"] == 14
    assert val["invalid_count"] == 0


def test_appendix_references_api_endpoints():
    res_all = client.get("/api/v1/appendix/references")
    assert res_all.status_code == 200
    assert res_all.json()["total_references"] == 14

    res_cat = client.get("/api/v1/appendix/references?category=infrastructure")
    assert res_cat.status_code == 200
    assert res_cat.json()["total_references"] == 4

    res_sum = client.get("/api/v1/appendix/references/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["total_references"] == 14

    res_search = client.get("/api/v1/appendix/references/search?q=Qdrant")
    assert res_search.status_code == 200
    assert res_search.json()["total_matches"] >= 1

    res_val = client.get("/api/v1/appendix/references/validate")
    assert res_val.status_code == 200
    assert res_val.json()["valid_count"] == 14

    res_item = client.get("/api/v1/appendix/references/qdrant")
    assert res_item.status_code == 200
    assert res_item.json()["reference"]["id"] == "qdrant"

    res_404 = client.get("/api/v1/appendix/references/non_existent_id")
    assert res_404.status_code == 404
