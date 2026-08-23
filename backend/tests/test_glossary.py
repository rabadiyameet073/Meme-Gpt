"""Tests for Glossary & Technical Terminology from 17_Appendix/Glossary.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.glossary_service import (
    get_all_glossary_terms,
    get_glossary_term_by_name,
    search_glossary,
    get_glossary_summary,
)

client = TestClient(app)


def test_get_all_glossary_terms():
    all_terms = get_all_glossary_terms()
    assert all_terms["total_terms"] == 41
    terms_list = [t["term"] for t in all_terms["terms"]]
    assert "ANN" in terms_list
    assert "DistilRoBERTa" in terms_list
    assert "WebP" in terms_list
    assert "Qdrant" in terms_list

    # Verify alphabetical ordering
    terms_upper = [t["term"].upper() for t in all_terms["terms"]]
    assert terms_upper == sorted(terms_upper)


def test_glossary_category_filtering():
    ai_terms = get_all_glossary_terms(category="ai_ml")
    assert ai_terms["total_terms"] == 18
    assert all(t["category"] == "ai_ml" for t in ai_terms["terms"])

    backend_terms = get_all_glossary_terms(category="backend_storage")
    assert backend_terms["total_terms"] == 14

    arch_terms = get_all_glossary_terms(category="architecture")
    assert arch_terms["total_terms"] == 4

    sec_terms = get_all_glossary_terms(category="security")
    assert sec_terms["total_terms"] == 3


def test_glossary_letter_filtering():
    c_terms = get_all_glossary_terms(letter="C")
    assert c_terms["total_terms"] >= 3
    assert all(t["term"].upper().startswith("C") for t in c_terms["terms"])

    p_terms = get_all_glossary_terms(letter="P")
    assert p_terms["total_terms"] >= 3
    assert all(t["term"].upper().startswith("P") for t in p_terms["terms"])


def test_get_glossary_term_by_name():
    term_hnsw = get_glossary_term_by_name("HNSW")
    assert term_hnsw is not None
    assert term_hnsw["category"] == "ai_ml"
    assert "Hierarchical Navigable Small World" in term_hnsw["full_name"]
    assert "Qdrant" in term_hnsw["usage_in_memegpt"]

    term_r2 = get_glossary_term_by_name("r2")
    assert term_r2 is not None
    assert "Cloudflare" in term_r2["full_name"]

    assert get_glossary_term_by_name("nonexistent_concept_xyz") is None


def test_search_glossary():
    search_emb = search_glossary("embedding")
    assert search_emb["total_matches"] >= 3

    search_ocr = search_glossary("Tesseract")
    assert search_ocr["total_matches"] >= 1
    assert any(t["term"] == "OCR" for t in search_ocr["matches"])

    search_groq = search_glossary("LPU")
    assert search_groq["total_matches"] >= 1


def test_get_glossary_summary():
    summary = get_glossary_summary()
    assert summary["total_terms"] == 41
    assert summary["categories_count"] == 5
    assert "ai_ml" in summary["category_distribution"]
    assert "backend_storage" in summary["category_distribution"]


def test_appendix_glossary_api_endpoints():
    res_all = client.get("/api/v1/appendix/glossary")
    assert res_all.status_code == 200
    assert res_all.json()["total_terms"] == 41

    res_cat = client.get("/api/v1/appendix/glossary?category=ai_ml")
    assert res_cat.status_code == 200
    assert res_cat.json()["total_terms"] == 18

    res_let = client.get("/api/v1/appendix/glossary?letter=M")
    assert res_let.status_code == 200
    assert res_let.json()["total_terms"] >= 1

    res_stats = client.get("/api/v1/appendix/glossary/summary")
    assert res_stats.status_code == 200
    assert res_stats.json()["total_terms"] == 41

    res_search = client.get("/api/v1/appendix/glossary/search?q=Cosine")
    assert res_search.status_code == 200
    assert res_search.json()["total_matches"] >= 1

    res_term = client.get("/api/v1/appendix/glossary/CLIP")
    assert res_term.status_code == 200
    assert res_term.json()["term"]["term"] == "CLIP"

    res_404 = client.get("/api/v1/appendix/glossary/non_existent_term_123")
    assert res_404.status_code == 404
