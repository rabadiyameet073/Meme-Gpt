"""Tests for Copy & Download feature from 08_Features/Copy_Download.md."""

from app.services.copy_download_service import (
    get_platform_support_matrix,
    get_copy_download_analytics_weights,
    generate_download_asset_descriptor,
)


def test_platform_support_matrix():
    matrix = get_platform_support_matrix()
    assert "Chrome 76+" in matrix
    assert matrix["Chrome 76+"]["image_copy"] is True
    assert matrix["Chrome 76+"]["url_fallback"] is True

    assert "Firefox" in matrix
    assert matrix["Firefox"]["image_copy"] is False
    assert matrix["Firefox"]["url_fallback"] is True

    assert "Mobile Safari (iOS 16+)" in matrix
    assert matrix["Mobile Safari (iOS 16+)"]["image_copy"] is True


def test_analytics_signal_weights():
    weights = get_copy_download_analytics_weights()
    assert weights["copy_image"]["weight"] == 1.0
    assert weights["copy_url"]["weight"] == 0.5
    assert weights["download"]["weight"] == 2.0
    assert weights["format_change"]["weight"] == 0.1


def test_generate_download_asset_descriptor():
    meme_mock = {
        "id": "meme_042",
        "name": "This Is Fine",
        "slug": "this-is-fine",
        "formats": {
            "image": "https://cdn.memegpt.com/images/this-is-fine.png",
            "gif": "https://cdn.memegpt.com/memes/this-is-fine.gif",
            "video": "https://cdn.memegpt.com/videos/this-is-fine.mp4",
            "webp": "https://cdn.memegpt.com/webp/this-is-fine.webp",
        }
    }

    # Image download
    img_desc = generate_download_asset_descriptor(meme_mock, "image")
    assert img_desc["filename"] == "this-is-fine.png"
    assert img_desc["url"] == "https://cdn.memegpt.com/images/this-is-fine.png"
    assert img_desc["content_type"] == "image/png"

    # GIF download
    gif_desc = generate_download_asset_descriptor(meme_mock, "gif")
    assert gif_desc["filename"] == "this-is-fine.gif"
    assert gif_desc["url"] == "https://cdn.memegpt.com/memes/this-is-fine.gif"
    assert gif_desc["content_type"] == "image/gif"

    # Video download
    vid_desc = generate_download_asset_descriptor(meme_mock, "video")
    assert vid_desc["filename"] == "this-is-fine.mp4"
    assert vid_desc["url"] == "https://cdn.memegpt.com/videos/this-is-fine.mp4"
    assert vid_desc["content_type"] == "video/mp4"
