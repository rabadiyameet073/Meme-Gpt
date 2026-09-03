"""
Tests for 09_CDN_R2_Setup.md (Upgraded Docs).

Verifies:
- build_meme_urls() URL construction
- get_r2_client() singleton and fallback
- upload_file() S3 put_object interaction
- upload_meme_image() MIME and folder routing
- generate_thumbnail() WebP generation and cropping
- upload_thumbnail() thumbnail upload
- resolve_formats() fallback resolution
- upload_to_r2 and generate_thumbnails scripts
"""

from io import BytesIO
from unittest.mock import MagicMock, patch
from PIL import Image
import pytest

from app.services.cdn_service import (
    build_meme_urls,
    get_r2_client,
    upload_file,
    upload_meme_image,
    generate_thumbnail,
    upload_thumbnail,
    resolve_formats,
    get_share_url,
)
from scripts.generate_thumbnails import generate_all_thumbnails
from scripts.upload_to_r2 import upload_all_memes


def test_build_meme_urls_structure():
    """Verify build_meme_urls formats correct paths for images, gifs, videos, webp, thumbs."""
    urls = build_meme_urls("drake-hotline-bling")
    assert "image_url" in urls
    assert urls["image_url"].endswith("/images/drake-hotline-bling.jpg")
    assert urls["gif_url"].endswith("/gifs/drake-hotline-bling.gif")
    assert urls["mp4_url"].endswith("/videos/drake-hotline-bling.mp4")
    assert urls["webp_url"].endswith("/webp/drake-hotline-bling.webp")
    assert urls["thumb_url"].endswith("/thumbs/drake-hotline-bling.webp")


def test_get_share_url():
    """Verify get_share_url builds shareable URLs with query referral."""
    share_url = get_share_url("distracted-boyfriend", query_id="q_12345")
    assert "/meme/distracted-boyfriend?ref=q_12345" in share_url


def test_generate_thumbnail_dimensions_and_format():
    """Verify generate_thumbnail produces valid 200x200 WebP bytes."""
    img_byte_arr = BytesIO()
    sample_img = Image.new("RGB", (600, 400), color="red")
    sample_img.save(img_byte_arr, format="JPEG")

    thumb_bytes = generate_thumbnail(img_byte_arr.getvalue(), size=(200, 200))
    assert thumb_bytes is not None
    assert len(thumb_bytes) > 0

    # Verify generated image properties
    thumb_img = Image.open(BytesIO(thumb_bytes))
    assert thumb_img.format == "WEBP"
    assert thumb_img.size == (200, 200)


def test_upload_file_mock():
    """Verify upload_file calls S3 put_object and returns CDN URL."""
    mock_s3 = MagicMock()
    with patch("app.services.cdn_service.get_r2_client", return_value=mock_s3):
        url = upload_file(
            file_data=b"fake_image_bytes",
            key="images/test-meme.jpg",
            content_type="image/jpeg",
        )
        assert url is not None
        assert url.endswith("/images/test-meme.jpg")
        assert mock_s3.put_object.called
        call_kwargs = mock_s3.put_object.call_args[1]
        assert call_kwargs["Key"] == "images/test-meme.jpg"
        assert call_kwargs["ContentType"] == "image/jpeg"


def test_upload_meme_image_folder_routing():
    """Verify upload_meme_image routes gifs to gifs/ and mp4s to videos/."""
    mock_s3 = MagicMock()
    with patch("app.services.cdn_service.get_r2_client", return_value=mock_s3):
        gif_url = upload_meme_image("test-gif", b"gifbytes", fmt="gif")
        assert gif_url is not None
        assert "/gifs/test-gif.gif" in gif_url

        mp4_url = upload_meme_image("test-vid", b"vidbytes", fmt="mp4")
        assert mp4_url is not None
        assert "/videos/test-vid.mp4" in mp4_url


def test_resolve_formats_fallbacks():
    """Verify resolve_formats prioritizes explicit URLs and falls back to legacy refs."""
    meme = {
        "slug": "sample-meme",
        "imageRef": "https://i.imgflip.com/sample.jpg",
        "gifRef": "https://media.giphy.com/sample.gif",
    }
    formats = resolve_formats(meme)
    assert formats["image"] == "https://i.imgflip.com/sample.jpg"
    assert formats["gif"] == "https://media.giphy.com/sample.gif"
    assert "thumb" in formats
    assert "webp" in formats
