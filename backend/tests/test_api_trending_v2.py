"""Tests for Trending API from 07_APIs/Trending_API.md."""

import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, Meme
from app.services.trending_service import (
    calculate_advanced_trending_score,
    normalize_trending_scores,
    validate_trending_params,
)

client = TestClient(app)
init_db()


def test_get_trending_full_schema():
    with next(get_db()) as db:
        for i in range(3):
            test_id = f"trend_v2_{uuid.uuid4().hex[:6]}"
            db.add(Meme(
                id=test_id,
                name=f"Trending V2 Meme {i}",
                slug=f"trending-v2-{test_id}",
                category="tech",
                dialogue=f"Tech dialogue {i}",
                explanation="Trending explanation",
                keywords="[]",
                usage_count=50 * (i + 1),
                viral_score=float(i + 1),
            ))
        db.commit()

    response = client.get("/api/v1/trending?category=tech&period=24h&limit=5")
    assert response.status_code == 200
    res = response.json()

    assert res["success"] is True
    assert "data" in res
    data = res["data"]
    assert data["category"] == "tech"
    assert data["period"] == "24h"
    assert "results" in data
    assert len(data["results"]) >= 1

    first = data["results"][0]
    assert "id" in first
    assert "name" in first
    assert "slug" in first
    assert "trending_score" in first
    assert "trending_rank" in first
    assert "category_rank" in first
    assert "downloads_24h" in first
    assert "copies_24h" in first
    assert "shares_24h" in first
    assert "searches_24h" in first
    assert "preview_url" in first
    assert "formats" in first

    meta = data["meta"]
    assert "total_results" in meta
    assert "total_trending" in meta
    assert "updated_at" in meta
    assert "next_update" in meta


def test_get_trending_periods():
    # 7d lookback period
    response_7d = client.get("/api/v1/trending?category=all&period=7d&limit=3")
    assert response_7d.status_code == 200
    res_7d = response_7d.json()
    assert res_7d["data"]["period"] == "7d"
    assert "downloads_7d" in res_7d["data"]["results"][0]

    # 30d lookback period
    response_30d = client.get("/api/v1/trending?category=all&period=30d&limit=3")
    assert response_30d.status_code == 200
    res_30d = response_30d.json()
    assert res_30d["data"]["period"] == "30d"
    assert "downloads_30d" in res_30d["data"]["results"][0]


def test_get_trending_invalid_category():
    response = client.get("/api/v1/trending?category=invalid_category_xyz")
    assert response.status_code == 400
    assert "category" in (response.json().get("message") or response.json().get("detail", "")).lower()


def test_get_trending_invalid_period():
    response = client.get("/api/v1/trending?period=1year")
    assert response.status_code == 400
    assert "period" in (response.json().get("message") or response.json().get("detail", "")).lower()


def test_trending_scoring_math():
    with next(get_db()) as db:
        test_id = f"math_{uuid.uuid4().hex[:6]}"
        meme = Meme(
            id=test_id,
            name="Math Meme",
            slug=f"math-{test_id}",
            category="gaming",
            dialogue="math",
            explanation="math",
            keywords="[]",
            usage_count=100,
        )
        db.add(meme)
        db.commit()

        score_data = calculate_advanced_trending_score(meme, db=db, period_hours=24)
        assert "raw_score" in score_data
        assert score_data["raw_score"] >= 0.0
