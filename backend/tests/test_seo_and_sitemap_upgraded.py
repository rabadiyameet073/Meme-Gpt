"""
Tests for 13_SEO_And_Sitemap.md (Upgraded Docs).

Verifies:
1. /sitemap.xml endpoint generation and XML structure
2. /robots.txt endpoint and file content
3. /meme/{slug}/og rich social preview HTML generation
4. Schema.org ImageObject JSON-LD markup
"""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.database import SessionLocal, Meme

client = TestClient(app)


def test_robots_txt_file_and_endpoint():
    """Verify robots.txt exists in frontend/public and is served from backend root."""
    frontend_robots = Path("d:/Meme GPT/frontend/public/robots.txt")
    assert frontend_robots.exists()
    file_content = frontend_robots.read_text(encoding="utf-8")
    assert "User-agent: *" in file_content
    assert "Disallow: /api/" in file_content
    assert "Sitemap:" in file_content

    # Test backend root /robots.txt endpoint
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    assert "Disallow: /api/" in resp.text
    assert "sitemap.xml" in resp.text


def test_sitemap_xml_endpoint():
    """Verify /sitemap.xml returns valid XML with proper headers and url entries."""
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    assert "public, max-age=3600" in resp.headers.get("cache-control", "")

    xml_text = resp.text
    assert "<?xml version=" in xml_text
    assert "<urlset" in xml_text
    assert "<loc>" in xml_text
    assert "<priority>" in xml_text
    assert "</urlset>" in xml_text


def test_meme_og_html_endpoint():
    """Verify /meme/{slug}/og returns rich crawler HTML with OpenGraph and Schema.org tags."""
    db = SessionLocal()
    try:
        meme = Meme(
            id="seo_test_meme_99",
            name="SEO Test Meme",
            slug="seo-test-meme-99",
            category="seo",
            explanation="Testing Open Graph crawler metadata",
            image_url="https://cdn.memegpt.com/images/seo-test.jpg",
        )
        db.add(meme)
        db.commit()
        db.refresh(meme)

        resp = client.get(f"/meme/{meme.slug}/og")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        html = resp.text

        # Verify Open Graph tags
        assert 'property="og:title"' in html
        assert 'property="og:image"' in html
        assert 'property="og:description"' in html
        assert "SEO Test Meme" in html

        # Verify Twitter Card
        assert 'name="twitter:card"' in html
        assert 'name="twitter:title"' in html

        # Verify Schema.org JSON-LD
        assert "application/ld+json" in html
        assert "ImageObject" in html

        # Clean up
        db.delete(meme)
        db.commit()
    finally:
        db.close()


def test_meme_og_404():
    """Verify /meme/{non_existent}/og returns 404."""
    resp = client.get("/meme/non-existent-slug-xyz-12345/og")
    assert resp.status_code == 404
