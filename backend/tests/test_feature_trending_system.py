"""Tests for Trending System from 08_Features/Trending_System.md."""

from app.services.trending_system_service import (
    calculate_trending_velocity_score,
    get_trending_tier_info,
    refresh_category_trending_cache,
    get_cached_category_trending,
    SUPPORTED_TRENDING_CATEGORIES,
)


def test_trending_velocity_formula():
    # Test formula: (views*0.1 + clicks*0.5 + downloads*2.0 + shares*3.0 + thumbs_up*2.0) / 1000
    # Example: 1000 views (100) + 200 clicks (100) + 100 downloads (200) + 100 shares (300) + 100 thumbs (200) = 900 -> 0.90
    f_counts = {
        "views": 1000,
        "clicks": 200,
        "downloads": 100,
        "shares": 100,
        "thumbs_up": 100,
    }
    score = calculate_trending_velocity_score(f_counts)
    assert abs(score - 0.90) < 1e-4

    # High viral capped at 1.0
    f_viral = {
        "views": 10000,
        "downloads": 1000,
        "shares": 2000,
    }
    assert calculate_trending_velocity_score(f_viral) == 1.0


def test_trending_tier_ranges():
    # Hot: 0.80 - 1.00
    hot_tier = get_trending_tier_info(0.85)
    assert hot_tier["tier"] == "hot"
    assert "🔥" in hot_tier["label"]
    assert hot_tier["is_visible"] is True

    # Rising: 0.50 - 0.79
    rising_tier = get_trending_tier_info(0.65)
    assert rising_tier["tier"] == "rising"
    assert "📈" in rising_tier["label"]
    assert rising_tier["is_visible"] is True

    # Steady: 0.20 - 0.49
    steady_tier = get_trending_tier_info(0.35)
    assert steady_tier["tier"] == "steady"
    assert "➡️" in steady_tier["label"]
    assert steady_tier["is_visible"] is True

    # Below threshold: <0.20
    low_tier = get_trending_tier_info(0.12)
    assert low_tier["tier"] == "below_threshold"
    assert low_tier["is_visible"] is False


def test_refresh_and_category_caching():
    sample_memes = [
        {
            "id": "meme_work_01",
            "name": "Work Coffee",
            "category": "work",
            "feedback": {"views": 1000, "clicks": 200, "downloads": 150, "shares": 100, "thumbs_up": 80},
        },
        {
            "id": "meme_work_02",
            "name": "Monday Meeting",
            "category": "work",
            "feedback": {"views": 500, "clicks": 100, "downloads": 50, "shares": 30, "thumbs_up": 20},
        },
        {
            "id": "meme_game_01",
            "name": "Gaming Rage",
            "category": "gaming",
            "feedback": {"views": 800, "clicks": 180, "downloads": 90, "shares": 70, "thumbs_up": 50},
        },
    ]

    refresh_res = refresh_category_trending_cache(memes_list=sample_memes, categories=SUPPORTED_TRENDING_CATEGORIES, limit=50)
    assert "all" in refresh_res
    assert "work" in refresh_res
    assert "gaming" in refresh_res

    # Retrieve from cache
    work_trending = get_cached_category_trending("work")
    assert len(work_trending) == 2
    # Verify sorted in descending order of score
    assert work_trending[0]["trending_score"] >= work_trending[1]["trending_score"]
    assert work_trending[0]["id"] == "meme_work_01"
