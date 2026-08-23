"""Tests for FAQ Knowledge Base & Specifications from 15_FAQs/General_FAQ.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.faq_service import (
    get_all_faqs,
    get_faq_by_id,
    search_faqs,
    get_faq_categories_summary,
    get_ai_models_catalog,
    get_graceful_degradation_matrix,
)

client = TestClient(app)


def test_get_all_faqs():
    all_faqs = get_all_faqs()
    assert all_faqs["total_faqs"] == 21

    gen_faqs = get_all_faqs(category="general")
    assert gen_faqs["total_faqs"] == 8

    tech_faqs = get_all_faqs(category="technical")
    assert tech_faqs["total_faqs"] == 8

    api_faqs = get_all_faqs(category="api")
    assert api_faqs["total_faqs"] == 5


def test_get_faq_by_id():
    f1 = get_faq_by_id("FAQ_GEN_1")
    assert f1 is not None
    assert "MemeGPT" in f1["question"]

    f_tech = get_faq_by_id("faq_tech_2")
    assert f_tech is not None
    assert "FastAPI" in f_tech["question"]

    assert get_faq_by_id("FAQ_NON_EXISTENT") is None


def test_search_faqs():
    res_fastapi = search_faqs("FastAPI")
    assert res_fastapi["total_matches"] >= 1
    assert any("FastAPI" in m["answer"] or "FastAPI" in m["question"] for m in res_fastapi["results"])

    res_groq = search_faqs("Groq")
    assert res_groq["total_matches"] >= 1

    res_discord = search_faqs("Discord")
    assert res_discord["total_matches"] >= 1


def test_faq_categories_summary():
    cats = get_faq_categories_summary()
    assert cats["total_faqs"] == 21
    assert cats["total_categories"] == 3
    assert cats["category_counts"]["general"] == 8
    assert cats["category_counts"]["technical"] == 8
    assert cats["category_counts"]["api"] == 5


def test_ai_models_catalog():
    models = get_ai_models_catalog()
    assert models["total_models"] == 6
    names = [m["model"] for m in models["models"]]
    assert "MiniLM-L6-v2" in names
    assert "DistilRoBERTa" in names
    assert "Llama 3.1 8B (Groq)" in names
    assert "BLIP" in names
    assert "CLIP ViT-B/32" in names
    assert "Tesseract" in names


def test_graceful_degradation_matrix():
    matrix = get_graceful_degradation_matrix()
    assert matrix["total_scenarios"] == 4
    subsystems = [s["subsystem"] for s in matrix["matrix"]]
    assert "Groq LLM API" in subsystems
    assert "Qdrant Vector DB" in subsystems
    assert "Redis Cache" in subsystems
    assert "Total External Outage" in subsystems


def test_faq_api_endpoints():
    res_list = client.get("/api/v1/faqs")
    assert res_list.status_code == 200
    assert res_list.json()["total_faqs"] == 21

    res_filter = client.get("/api/v1/faqs?category=api")
    assert res_filter.status_code == 200
    assert res_filter.json()["total_faqs"] == 5

    res_search = client.get("/api/v1/faqs/search?q=Pinecone")
    assert res_search.status_code == 200
    assert res_search.json()["total_matches"] >= 1

    res_cats = client.get("/api/v1/faqs/categories")
    assert res_cats.status_code == 200
    assert res_cats.json()["total_categories"] == 3

    res_models = client.get("/api/v1/faqs/models")
    assert res_models.status_code == 200
    assert res_models.json()["total_models"] == 6

    res_deg = client.get("/api/v1/faqs/degradation")
    assert res_deg.status_code == 200
    assert res_deg.json()["total_scenarios"] == 4

    res_single = client.get("/api/v1/faqs/FAQ_GEN_3")
    assert res_single.status_code == 200
    assert res_single.json()["faq"]["id"] == "FAQ_GEN_3"

    res_404 = client.get("/api/v1/faqs/FAQ_UNKNOWN")
    assert res_404.status_code == 404
