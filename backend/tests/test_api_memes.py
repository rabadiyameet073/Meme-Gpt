"""Tests for Meme API, Trending API, and Download API from 07_APIs/Meme_API.md."""

import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, Meme
from app.services.meme_service import calculate_trending_score, format_meme_detail_response

client = TestClient(app)
init_db()


def test_get_meme_detail_by_slug():
    with next(get_db()) as db:
        test_id = f"meme_{uuid.uuid4().hex[:6]}"
        slug = f"this-is-fine-{test_id}"
        meme = Meme(
            id=test_id,
            name="This Is Fine",
            slug=slug,
            category="work",
            dialogue="This is fine.",
            explanation="A dog sitting in a burning room saying this is fine",
            keywords='["work", "stress", "acceptance", "chaos"]',
            viral_score=8.7,
            usage_count=15823,
            gif_ref=f"https://cdn.memegpt.com/gifs/{slug}.gif",
            image_ref=f"https://cdn.memegpt.com/images/{slug}.jpg",
            video_ref=None,
        )
        db.add(meme)
        db.commit()

    response = client.get(f"/api/v1/memes/{slug}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_id
    assert data["name"] == "This Is Fine"
    assert data["slug"] == slug
    assert "work" in data["categories"]
    assert "formats" in data
    assert data["formats"]["gif"] == f"https://cdn.memegpt.com/gifs/{slug}.gif"
    assert data["formats"]["image"] == f"https://cdn.memegpt.com/images/{slug}.jpg"
    assert data["formats"]["video"] is None
    assert data["share_url"] == f"https://memegpt.com/meme/{slug}"
    assert data["popularity_score"] <= 1.0


def test_get_meme_not_found():
    response = client.get("/api/v1/memes/non-existent-slug-xyz-9999")
    assert response.status_code == 404
    data = response.json()
    assert "No meme found" in (data.get("message") or data.get("detail", "")) or "error" in data


def test_download_meme_redirect():
    with next(get_db()) as db:
        test_id = f"meme_dl_{uuid.uuid4().hex[:6]}"
        slug = f"downloadable-meme-{test_id}"
        meme = Meme(
            id=test_id,
            name="Downloadable Meme",
            slug=slug,
            category="gaming",
            dialogue="Let me download",
            explanation="Download test",
            keywords="[]",
            gif_ref=f"https://cdn.memegpt.com/gifs/{slug}.gif",
            image_ref=f"https://cdn.memegpt.com/images/{slug}.jpg",
            video_ref=None,
        )
        db.add(meme)
        db.commit()

    # 1. Successful 301 redirect for available GIF format
    response = client.get(f"/api/v1/memes/{slug}/download?format=gif", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == f"https://cdn.memegpt.com/gifs/{slug}.gif"

    # 2. 400 Bad Request for unavailable video format
    response_video = client.get(f"/api/v1/memes/{slug}/download?format=video", follow_redirects=False)
    assert response_video.status_code == 400
    assert "not available" in (response_video.json().get("message") or response_video.json().get("detail", ""))


def test_get_trending_memes():
    with next(get_db()) as db:
        for i in range(3):
            test_id = f"trend_{uuid.uuid4().hex[:6]}"
            meme = Meme(
                id=test_id,
                name=f"Trending Meme {i}",
                slug=f"trending-{test_id}",
                category="work",
                dialogue="Trending dialogue",
                explanation="Trending explanation",
                keywords="[]",
                viral_score=float(10 - i),
                usage_count=100 * (i + 1),
            )
            db.add(meme)
        db.commit()

    response = client.get("/api/v1/trending?category=work&limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["category"] == "work"
    assert "results" in data
    assert len(data["results"]) >= 3
    assert data["limit"] == 10
    assert data["offset"] == 0

    first = data["results"][0]
    assert "id" in first
    assert "name" in first
    assert "slug" in first
    assert "trending_score" in first
    assert 0.0 <= first["trending_score"] <= 1.0


def test_calculate_trending_score():
    with next(get_db()) as db:
        test_id = f"score_calc_{uuid.uuid4().hex[:6]}"
        meme = Meme(
            id=test_id,
            name="Score Calc Meme",
            slug=f"calc-{test_id}",
            category="tech",
            dialogue="calc",
            explanation="calc",
            keywords="[]",
            viral_score=5.0,
            usage_count=50,
            upvotes=20,
        )
        db.add(meme)
        db.commit()

        score = calculate_trending_score(meme, db=db, time_window_hours=24)
        assert 0.0 <= score <= 1.0
