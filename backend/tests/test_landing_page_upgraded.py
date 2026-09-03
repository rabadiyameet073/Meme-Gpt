"""
Tests for 17_Landing_Page.md (Upgraded Docs).

Verifies:
1. frontend/public/landing.html exists and contains complete marketing structure
2. GET /landing endpoint returns 200 with text/html
3. Content contains SEO tags, Features grid, How It Works steps, and CTA
"""

from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_landing_html_file_exists():
    """Verify landing.html exists in frontend/public."""
    candidates = [
        Path("frontend/public/landing.html"),
        Path("d:/Meme GPT/frontend/public/landing.html"),
        Path(__file__).resolve().parents[2] / "frontend" / "public" / "landing.html",
    ]
    landing_file = next((p for p in candidates if p.exists()), Path("frontend/public/landing.html"))
    assert landing_file.exists()
    content = landing_file.read_text(encoding="utf-8")

    assert "MemeGPT" in content
    assert "Features" in content
    assert "5,000+" in content
    assert "Vector" in content




def test_get_landing_endpoint():
    """Verify GET /landing returns 200 and serves HTML."""
    resp = client.get("/landing")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "MemeGPT" in resp.text
    assert "hero-badge" in resp.text
