"""
MemeGPT — Rate Limiting & Security Header Tests.
"""

import pytest


def test_security_headers_present(client):
    """Test response includes all essential security headers."""
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    headers = resp.headers

    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert "strict-origin-when-cross-origin" in headers.get("referrer-policy", "")
    assert "x-ratelimit-limit" in headers
    assert "x-ratelimit-remaining" in headers


def test_robots_txt_endpoint(client):
    """Test robots.txt is accessible and disallows private routes."""
    resp = client.get("/robots.txt")
    assert resp.status_code == 200
    assert "User-agent: *" in resp.text
    assert "Disallow: /api/" in resp.text


def test_sitemap_xml_endpoint(client):
    """Test sitemap.xml returns valid XML."""
    resp = client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "<?xml" in resp.text
    assert "<urlset" in resp.text
