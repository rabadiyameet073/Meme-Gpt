"""Tests for Multi-Format Support from 08_Features/Multi_Format.md."""

from app.services.multi_format_service import (
    get_format_catalog,
    get_format_platform_recommendation,
    resolve_all_meme_format_assets,
)


def test_format_catalog_specifications():
    catalog = get_format_catalog()
    assert "gif" in catalog
    assert "image" in catalog
    assert "video" in catalog
    assert "webp" in catalog
    assert "thumb" in catalog

    assert catalog["gif"]["extension"] == ".gif"
    assert catalog["gif"]["avg_size"] == "1–5MB"
    assert "WhatsApp" in catalog["gif"]["use_case"]

    assert catalog["image"]["extension"] == ".png"
    assert catalog["image"]["avg_size"] == "50–500KB"

    assert catalog["video"]["extension"] == ".mp4"
    assert catalog["video"]["avg_size"] == "2–10MB"


def test_platform_recommendation_tips():
    assert get_format_platform_recommendation("gif") == "Best for WhatsApp, Discord, Slack"
    assert get_format_platform_recommendation("image") == "Best for Instagram, email, blog"
    assert get_format_platform_recommendation("png") == "Best for Instagram, email, blog"
    assert get_format_platform_recommendation("video") == "Best for TikTok, Reels, YouTube Shorts"
    assert get_format_platform_recommendation("mp4") == "Best for TikTok, Reels, YouTube Shorts"
    assert get_format_platform_recommendation("webp") == "Best for Telegram stickers, web"


def test_resolve_all_meme_format_assets():
    sample_meme = {
        "id": "meme_999",
        "slug": "this-is-fine",
        "formats": {
            "image": "https://cdn.memegpt.com/images/this-is-fine.png",
            "gif": "https://cdn.memegpt.com/memes/this-is-fine.gif",
            "video": "https://cdn.memegpt.com/videos/this-is-fine.mp4",
        }
    }

    resolved = resolve_all_meme_format_assets(sample_meme)
    assert resolved["slug"] == "this-is-fine"
    assert resolved["formats"]["gif"]["extension"] == ".gif"
    assert resolved["formats"]["gif"]["recommendation"] == "Best for WhatsApp, Discord, Slack"
    assert resolved["formats"]["image"]["extension"] == ".png"
    assert resolved["formats"]["video"]["extension"] == ".mp4"
    assert resolved["formats"]["webp"]["extension"] == ".webp"
