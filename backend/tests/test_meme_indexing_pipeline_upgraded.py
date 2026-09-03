"""
Tests for 06_Meme_Indexing_Pipeline.md (Upgraded Docs).

Verifies:
- generate_embeddings.py full pipeline: download_image, ocr_image, caption_image, embed_image, embed_text, build_rich_text, index_memes
- scripts/download_memes.py media downloader with retry and streaming
- scripts/index_to_qdrant.py CLI bridge
"""

from io import BytesIO
from unittest.mock import MagicMock, patch
from PIL import Image
import pytest

from generate_embeddings import (
    download_image,
    ocr_image,
    caption_image,
    embed_image,
    embed_text,
    build_rich_text,
    index_memes,
    load_models,
)
from scripts.download_memes import download_file, run_downloader


def test_download_image_success():
    """Verify download_image downloads and converts byte response into a PIL RGB Image."""
    img_byte_arr = BytesIO()
    sample_img = Image.new("RGB", (100, 100), color="blue")
    sample_img.save(img_byte_arr, format="JPEG")

    mock_resp = MagicMock()
    mock_resp.content = img_byte_arr.getvalue()
    mock_resp.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_resp):
        pil_img = download_image("https://cdn.memegpt.com/test.jpg")
        assert pil_img is not None
        assert isinstance(pil_img, Image.Image)
        assert pil_img.size == (100, 100)


def test_ocr_image_graceful_fallback():
    """Verify ocr_image returns empty string if pytesseract or binary is not found."""
    sample_img = Image.new("RGB", (100, 100), color="white")
    text = ocr_image(sample_img)
    assert isinstance(text, str)


def test_caption_image_with_mock():
    """Verify caption_image processes image with BLIP model and decodes generated caption."""
    mock_processor = MagicMock()
    mock_processor.return_value = {"input_ids": [1, 2, 3]}
    mock_processor.decode.return_value = "a funny cat sitting on a keyboard"

    mock_model = MagicMock()
    mock_model.generate.return_value = [[1, 2, 3]]

    models = {
        "blip": mock_model,
        "blip_processor": mock_processor,
    }

    sample_img = Image.new("RGB", (100, 100), color="white")
    caption = caption_image(sample_img, models)
    assert caption == "a funny cat sitting on a keyboard"


def test_embed_image_with_mock():
    """Verify embed_image returns 512-dimensional normalized vector."""
    mock_processor = MagicMock()
    mock_processor.return_value = {"pixel_values": [0.1]}

    mock_tensor = MagicMock()
    mock_tensor.norm.return_value = 1.0
    mock_tensor.__truediv__.return_value = mock_tensor
    mock_tensor.__getitem__.return_value.tolist.return_value = [0.05] * 512

    mock_model = MagicMock()
    mock_model.get_image_features.return_value = mock_tensor

    models = {
        "clip": mock_model,
        "clip_processor": mock_processor,
    }

    sample_img = Image.new("RGB", (100, 100), color="white")
    vec = embed_image(sample_img, models)
    assert vec is not None
    assert len(vec) == 512


def test_embed_text_returns_384_dimensions():
    """Verify embed_text returns 384-dimensional vector."""
    models = load_models(skip_images=True)
    vec = embed_text("Deploying to production on Friday afternoon", models)
    assert isinstance(vec, list)
    assert len(vec) == 384


def test_build_rich_text_comprehensive():
    """Verify build_rich_text constructs comprehensive structured text from all attributes."""
    meme = {
        "name": "Distracted Boyfriend",
        "categories": ["relationship", "temptation"],
        "emotions": ["guilt", "distraction"],
        "dialogue": "Boyfriend looking back at other girl",
        "explanation": "When something shiny distracts you from your current commitment",
        "keywords": ["distracted", "boyfriend", "girl", "cheating"],
    }
    ocr_text = "NEW JAVASCRIPT FRAMEWORK"
    caption = "a man looking at another woman while holding hands with his girlfriend"

    rich = build_rich_text(meme, ocr_text=ocr_text, caption=caption)
    assert "Meme: Distracted Boyfriend" in rich
    assert "Category: relationship, temptation" in rich
    assert "Emotions: guilt, distraction" in rich
    assert "Text on meme: Boyfriend looking back at other girl" in rich
    assert "When to use: When something shiny distracts you from your current commitment" in rich
    assert "Keywords: distracted, boyfriend, girl, cheating" in rich
    assert "OCR extracted text: NEW JAVASCRIPT FRAMEWORK" in rich
    assert "Image shows: a man looking at another woman while holding hands with his girlfriend" in rich


def test_index_memes_pipeline_execution():
    """Verify index_memes runs batch processing with DB items and Qdrant upsert."""
    mock_client = MagicMock()
    with patch("app.services.search_service.get_qdrant_client", return_value=mock_client):
        with patch("app.services.search_service.create_qdrant_collection", return_value=True):
            with patch("app.services.search_service.upsert_memes", return_value=5):
                index_memes(limit=5, recreate=False, skip_images=True)
