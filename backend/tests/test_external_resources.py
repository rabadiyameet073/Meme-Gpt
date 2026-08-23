"""Tests for External Resources and Citations from 16_References/External_Resources.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.external_resources_service import (
    get_official_documentation,
    get_research_papers,
    get_meme_data_sources,
    get_community_resources,
    search_external_resources,
    get_external_resources_summary,
)

client = TestClient(app)


def test_official_documentation():
    all_docs = get_official_documentation()
    assert all_docs["total_documentation_links"] == 25

    fw_docs = get_official_documentation(category="frameworks_libraries")
    assert fw_docs["total_documentation_links"] == 7

    ai_docs = get_official_documentation(category="ai_ml")
    assert ai_docs["total_documentation_links"] == 7

    infra_docs = get_official_documentation(category="infrastructure")
    assert infra_docs["total_documentation_links"] == 7

    dev_docs = get_official_documentation(category="development_tools")
    assert dev_docs["total_documentation_links"] == 4


def test_research_papers():
    res = get_research_papers()
    assert res["total_papers"] == 6
    names = [p["paper"] for p in res["papers"]]
    assert any("Sentence-BERT" in n for n in names)
    assert any("CLIP" in n for n in names)
    assert any("BLIP" in n for n in names)
    assert any("MTEB" in n for n in names)
    assert any("Word2Vec" in n for n in names)
    assert any("Attention Is All You Need" in n for n in names)


def test_meme_data_sources():
    res = get_meme_data_sources()
    assert res["total_sources"] == 4
    sources = [s["source"] for s in res["sources"]]
    assert "Imgflip" in sources
    assert "Reddit (r/memes)" in sources
    assert "Tenor (Google)" in sources
    assert "Know Your Meme" in sources


def test_community_resources():
    res = get_community_resources()
    assert res["total_resources"] == 5
    names = [c["name"] for c in res["resources"]]
    assert "FastAPI Discord" in names
    assert "r/FastAPI" in names
    assert "HuggingFace Forums" in names
    assert "Qdrant Discord" in names
    assert "Supabase Discord" in names


def test_search_external_resources():
    res_clip = search_external_resources("CLIP")
    assert res_clip["total_matches"] >= 2  # Documentation card + Research paper

    res_qdrant = search_external_resources("Qdrant")
    assert res_qdrant["total_matches"] >= 2  # Documentation + Discord

    res_imgflip = search_external_resources("Imgflip")
    assert res_imgflip["total_matches"] >= 1


def test_external_resources_summary():
    summary = get_external_resources_summary()
    assert summary["total_official_documentation"] == 25
    assert summary["total_research_papers"] == 6
    assert summary["total_meme_sources"] == 4
    assert summary["total_community_channels"] == 5
    assert summary["grand_total_external_resources"] == 40


def test_references_api_endpoints():
    res_doc = client.get("/api/v1/references/resources/documentation")
    assert res_doc.status_code == 200
    assert res_doc.json()["total_documentation_links"] == 25

    res_doc_cat = client.get("/api/v1/references/resources/documentation?category=ai_ml")
    assert res_doc_cat.status_code == 200
    assert res_doc_cat.json()["total_documentation_links"] == 7

    res_pap = client.get("/api/v1/references/resources/papers")
    assert res_pap.status_code == 200
    assert res_pap.json()["total_papers"] == 6

    res_src = client.get("/api/v1/references/resources/meme-sources")
    assert res_src.status_code == 200
    assert res_src.json()["total_sources"] == 4

    res_com = client.get("/api/v1/references/resources/community")
    assert res_com.status_code == 200
    assert res_com.json()["total_resources"] == 5

    res_search = client.get("/api/v1/references/resources/search?q=FastAPI")
    assert res_search.status_code == 200
    assert res_search.json()["total_matches"] >= 3

    res_sum = client.get("/api/v1/references/resources/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["grand_total_external_resources"] == 40
