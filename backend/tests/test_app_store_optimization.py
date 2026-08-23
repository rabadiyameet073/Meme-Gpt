"""Tests for App Store Optimization (ASO) from 16_SEO_Marketing/App_Store_Optimization.md."""

from fastapi.testclient import TestClient
from app.main import app
from app.services.aso_service import (
    get_ios_app_store_listing,
    get_google_play_listing,
    get_screenshot_strategy,
    get_keyword_research_matrix,
    get_rating_prompt_strategy,
    get_aso_best_practices,
    evaluate_rating_prompt_eligibility,
)

client = TestClient(app)


def test_ios_app_store_listing():
    ios = get_ios_app_store_listing()
    assert ios["app_name"] == "MemeGPT – AI Meme Finder"
    assert len(ios["app_name"]) <= 30
    assert ios["subtitle"] == "Find Perfect Memes Instantly"
    assert len(ios["subtitle"]) <= 30
    assert ios["primary_category"] == "Entertainment"
    assert ios["secondary_category"] == "Utilities"
    assert len(ios["keywords_field"]) <= 100
    assert "meme finder" in ios["keywords_field"]
    assert "FEATURES" in ios["description"]


def test_google_play_listing():
    play = get_google_play_listing()
    assert play["app_name"] == "MemeGPT: AI Meme Finder & Download"
    assert len(play["short_description"]) <= 80
    assert play["category"] == "Entertainment"
    assert "meme" in play["tags"]
    assert "ai" in play["tags"]


def test_screenshot_strategy():
    strategy = get_screenshot_strategy()
    assert strategy["total_screenshots"] == 5
    screens = strategy["screenshots"]
    assert screens[0]["position"] == 1
    assert "Home screen" in screens[0]["screen"]
    assert screens[1]["position"] == 2
    assert "Search results" in screens[1]["screen"]
    assert screens[2]["position"] == 3
    assert "Meme detail" in screens[2]["screen"]
    assert screens[3]["position"] == 4
    assert "share sheet" in screens[3]["screen"].lower()
    assert screens[4]["position"] == 5
    assert "Trending" in screens[4]["screen"]


def test_keyword_research_matrix():
    kw = get_keyword_research_matrix()
    assert kw["total_tracked_keywords"] == 7
    assert kw["aggregate_monthly_search_volume"] >= 2000000

    keywords = [k["keyword"] for k in kw["keywords"]]
    assert "meme" in keywords
    assert "meme generator" in keywords
    assert "funny memes" in keywords
    assert "gif maker" in keywords
    assert "ai meme" in keywords
    assert "meme finder" in keywords
    assert "meme gpt" in keywords


def test_rating_prompt_strategy_and_rules():
    ratings = get_rating_prompt_strategy()
    assert len(ratings["triggers"]) == 3
    assert len(ratings["strict_rules"]) == 4


def test_aso_best_practices():
    practices = get_aso_best_practices()
    assert practices["total_practices"] == 6


def test_evaluate_rating_prompt_eligibility():
    # Error block
    err_eval = evaluate_rating_prompt_eligibility(
        searches_count=5, downloads_count=5, shares_count=2, days_since_last_prompt=40, last_action_was_error=True
    )
    assert err_eval["eligible"] is False
    assert "Never prompt after an error" in err_eval["reason"]

    # 30-day cooldown block
    cooldown_eval = evaluate_rating_prompt_eligibility(
        searches_count=5, downloads_count=5, shares_count=2, days_since_last_prompt=15, last_action_was_error=False
    )
    assert cooldown_eval["eligible"] is False
    assert "30-day cooldown" in cooldown_eval["reason"]

    # Eligible on 3rd search
    search_eval = evaluate_rating_prompt_eligibility(
        searches_count=3, downloads_count=0, shares_count=0, days_since_last_prompt=35, last_action_was_error=False
    )
    assert search_eval["eligible"] is True
    assert search_eval["trigger"] == "3rd successful search"

    # Eligible on 5th download
    dl_eval = evaluate_rating_prompt_eligibility(
        searches_count=1, downloads_count=5, shares_count=0, days_since_last_prompt=35, last_action_was_error=False
    )
    assert dl_eval["eligible"] is True
    assert dl_eval["trigger"] == "5th meme download"

    # Eligible on share
    share_eval = evaluate_rating_prompt_eligibility(
        searches_count=1, downloads_count=0, shares_count=1, days_since_last_prompt=35, last_action_was_error=False
    )
    assert share_eval["eligible"] is True
    assert share_eval["trigger"] == "Successful meme share"

    # Ineligible due to low engagement
    low_eval = evaluate_rating_prompt_eligibility(
        searches_count=1, downloads_count=0, shares_count=0, days_since_last_prompt=35, last_action_was_error=False
    )
    assert low_eval["eligible"] is False


def test_marketing_aso_api_endpoints():
    res_ios = client.get("/api/v1/marketing/aso/ios")
    assert res_ios.status_code == 200
    assert res_ios.json()["app_name"] == "MemeGPT – AI Meme Finder"

    res_play = client.get("/api/v1/marketing/aso/google-play")
    assert res_play.status_code == 200
    assert "MemeGPT" in res_play.json()["app_name"]

    res_screens = client.get("/api/v1/marketing/aso/screenshots")
    assert res_screens.status_code == 200
    assert res_screens.json()["total_screenshots"] == 5

    res_kw = client.get("/api/v1/marketing/aso/keywords")
    assert res_kw.status_code == 200
    assert res_kw.json()["total_tracked_keywords"] == 7

    res_ratings = client.get("/api/v1/marketing/aso/ratings")
    assert res_ratings.status_code == 200
    assert len(res_ratings.json()["triggers"]) == 3

    res_prac = client.get("/api/v1/marketing/aso/practices")
    assert res_prac.status_code == 200
    assert res_prac.json()["total_practices"] == 6

    res_eval = client.post(
        "/api/v1/marketing/aso/evaluate-rating-prompt",
        json={"searches_count": 4, "downloads_count": 0, "shares_count": 0, "days_since_last_prompt": 35, "last_action_was_error": False},
    )
    assert res_eval.status_code == 200
    assert res_eval.json()["eligible"] is True
