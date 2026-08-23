"""Tests for SEO Strategy & Technical SEO Implementation from 16_SEO_Marketing/SEO_Strategy.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.seo_strategy_service import (
    get_root_seo_metadata,
    generate_meme_seo_metadata,
    generate_meme_jsonld,
    generate_xml_sitemap_sample,
    get_robots_txt_rules,
    get_core_web_vitals_benchmarks,
    get_seo_category_pages,
    generate_seo_blog_post_outline,
    get_seo_target_keywords,
    get_seo_monitoring_matrix,
    get_seo_best_practices,
    audit_core_web_vitals_compliance,
)

client = TestClient(app)


def test_root_seo_metadata():
    meta = get_root_seo_metadata()
    assert meta["metadataBase"] == "https://memegpt.com"
    assert "MemeGPT" in meta["title"]["default"]
    assert "openGraph" in meta
    assert "twitter" in meta
    assert meta["robots"]["index"] is True
    assert meta["canonical"] == "https://memegpt.com"


def test_generate_meme_seo_metadata():
    meta = generate_meme_seo_metadata(
        slug="drake-hotline-bling",
        title="Drake Hotline Bling",
        description="Drake rejecting one thing and approving another",
        image_url="https://r2.memegpt.com/drake.jpg",
        keywords=["drake", "choice", "rejection"],
    )
    assert "Drake Hotline Bling Meme" in meta["title"]
    assert "Drake Hotline Bling meme" in meta["keywords"]
    assert "drake" in meta["keywords"]
    assert meta["alternates"]["canonical"] == "https://memegpt.com/meme/drake-hotline-bling"
    assert meta["openGraph"]["type"] == "article"


def test_generate_meme_jsonld():
    jsonld = generate_meme_jsonld(
        slug="distracted-boyfriend",
        name="Distracted Boyfriend",
        description="Guy looking back at another girl while girlfriend glares",
        image_url="https://r2.memegpt.com/distracted.jpg",
        thumb_url="https://r2.memegpt.com/thumb_distracted.webp",
        keywords=["jealousy", "temptation", "cheating"],
    )
    assert jsonld["@context"] == "https://schema.org"
    assert jsonld["@type"] == "ImageObject"
    assert jsonld["name"] == "Distracted Boyfriend Meme"
    assert jsonld["contentUrl"] == "https://r2.memegpt.com/distracted.jpg"
    assert jsonld["creator"]["name"] == "MemeGPT"


def test_generate_xml_sitemap_sample():
    sitemap = generate_xml_sitemap_sample(limit=5)
    assert "https://memegpt.com/sitemap.xml" in sitemap["sitemap_url"]
    assert sitemap["total_static_routes"] == 6
    assert sitemap["total_dynamic_sample_routes"] == 5

    urls = [r["url"] for r in sitemap["routes"]]
    assert "https://memegpt.com" in urls
    assert "https://memegpt.com/download" in urls
    assert "https://memegpt.com/meme/drake-hotline-bling" in urls


def test_robots_txt_rules():
    robots = get_robots_txt_rules()
    assert robots["sitemap"] == "https://memegpt.com/sitemap.xml"
    assert len(robots["rules"]) == 2
    disallowed = robots["rules"][1]["disallow"]
    assert "/api/" in disallowed
    assert "/_next/" in disallowed


def test_core_web_vitals_benchmarks():
    vitals = get_core_web_vitals_benchmarks()
    assert vitals["total_metrics"] == 5
    metrics = [m["metric"] for m in vitals["metrics"]]
    assert "LCP" in metrics
    assert "FID" in metrics
    assert "CLS" in metrics
    assert "TTFB" in metrics
    assert "FCP" in metrics


def test_seo_category_pages():
    cats = get_seo_category_pages()
    assert cats["total_categories"] == 4
    keywords = [c["target_keyword"] for c in cats["categories"]]
    assert "work memes" in keywords
    assert "monday memes" in keywords
    assert "programmer memes" in keywords
    assert "relationship memes" in keywords


def test_generate_seo_blog_post_outline():
    outline = generate_seo_blog_post_outline("Monday Morning")
    assert outline["target_topic"] == "Monday Morning"
    assert "Top 20 Monday Morning Memes" in outline["title"]
    assert outline["target_keyword"] == "monday morning memes"
    assert len(outline["structure"]) == 3


def test_seo_target_keywords():
    kw = get_seo_target_keywords()
    assert kw["total_keywords"] == 8
    assert kw["aggregate_monthly_search_volume"] >= 700000

    keywords = [k["keyword"] for k in kw["keywords"]]
    assert "meme generator" in keywords
    assert "funny memes 2025" in keywords
    assert "ai meme generator" in keywords
    assert "best monday memes" in keywords


def test_seo_monitoring_and_practices():
    monitors = get_seo_monitoring_matrix()
    assert monitors["total_monitors"] == 5

    practices = get_seo_best_practices()
    assert practices["total_practices"] == 7


def test_audit_core_web_vitals_compliance():
    pass_audit = audit_core_web_vitals_compliance(
        lcp_ms=1800, fid_ms=45, cls_score=0.03, ttfb_ms=250, fcp_ms=1100
    )
    assert pass_audit["verdict"] == "PASSED_GREEN"
    assert pass_audit["scores"]["lcp"]["status"] == "PASS"

    fail_audit = audit_core_web_vitals_compliance(
        lcp_ms=3200, fid_ms=150, cls_score=0.25, ttfb_ms=900, fcp_ms=2200
    )
    assert fail_audit["verdict"] == "NEEDS_OPTIMIZATION"
    assert fail_audit["scores"]["lcp"]["status"] == "FAIL"


def test_marketing_seo_api_endpoints():
    res_root = client.get("/api/v1/marketing/seo/root-metadata")
    assert res_root.status_code == 200
    assert res_root.json()["metadataBase"] == "https://memegpt.com"

    res_robots = client.get("/api/v1/marketing/seo/robots")
    assert res_robots.status_code == 200
    assert "sitemap" in res_robots.json()

    res_sitemap = client.get("/api/v1/marketing/seo/sitemap?limit=5")
    assert res_sitemap.status_code == 200
    assert res_sitemap.json()["total_static_routes"] == 6

    res_vitals = client.get("/api/v1/marketing/seo/web-vitals")
    assert res_vitals.status_code == 200
    assert res_vitals.json()["total_metrics"] == 5

    res_cats = client.get("/api/v1/marketing/seo/categories")
    assert res_cats.status_code == 200
    assert res_cats.json()["total_categories"] == 4

    res_kw = client.get("/api/v1/marketing/seo/keywords")
    assert res_kw.status_code == 200
    assert res_kw.json()["total_keywords"] == 8

    res_mon = client.get("/api/v1/marketing/seo/monitoring")
    assert res_mon.status_code == 200
    assert res_mon.json()["total_monitors"] == 5

    res_prac = client.get("/api/v1/marketing/seo/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 7

    res_meta = client.post(
        "/api/v1/marketing/seo/generate-meme-metadata",
        json={
            "slug": "two-buttons",
            "title": "Two Buttons",
            "description": "Guy sweating between two red buttons",
            "image_url": "https://r2.memegpt.com/two_buttons.jpg",
            "keywords": ["dilemma", "choice"],
        },
    )
    assert res_meta.status_code == 200
    assert "Two Buttons Meme" in res_meta.json()["metadata"]["title"]

    res_jsonld = client.post(
        "/api/v1/marketing/seo/generate-jsonld",
        json={
            "slug": "two-buttons",
            "name": "Two Buttons",
            "description": "Guy sweating between two red buttons",
            "image_url": "https://r2.memegpt.com/two_buttons.jpg",
            "thumb_url": "https://r2.memegpt.com/thumb_two_buttons.webp",
            "keywords": ["dilemma", "choice"],
        },
    )
    assert res_jsonld.status_code == 200
    assert res_jsonld.json()["jsonld"]["@type"] == "ImageObject"

    res_blog = client.post(
        "/api/v1/marketing/seo/generate-blog-outline",
        json={"topic": "Remote Work"},
    )
    assert res_blog.status_code == 200
    assert "Top 20 Remote Work Memes" in res_blog.json()["title"]

    res_audit = client.post(
        "/api/v1/marketing/seo/audit-web-vitals",
        json={"lcp_ms": 1500, "fid_ms": 30, "cls_score": 0.02, "ttfb_ms": 200, "fcp_ms": 800},
    )
    assert res_audit.status_code == 200
    assert res_audit.json()["verdict"] == "PASSED_GREEN"
