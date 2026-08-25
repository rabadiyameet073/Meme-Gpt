"""
Tests for Meme Indexing Pipeline from 06_Meme_Indexing_Pipeline.md.
"""

from unittest.mock import MagicMock, patch
from pathlib import Path

from generate_embeddings import (
    build_rich_text,
    embed_text,
    download_image,
    ocr_image,
    caption_image,
    embed_image,
    index_memes,
)
from scripts.download_memes import download_file


def test_build_rich_text_composition():
    meme = {
        "name": "Disaster Girl",
        "category": "schadenfreude",
        "categories": ["dark_humor", "reaction"],
        "emotions": ["joy", "amusement"],
        "dialogue": "House burning down",
        "explanation": "Smiling in front of catastrophe",
        "keywords": ["fire", "girl", "smile", "disaster"],
    }
    ocr_text = "House is fine"
    caption = "A young girl smiles at the camera while a house burns in the background"

    rich_text = build_rich_text(meme, ocr_text=ocr_text, caption=caption)

    assert "Meme: Disaster Girl" in rich_text
    assert "Category: dark_humor, reaction" in rich_text
    assert "Emotions: joy, amusement" in rich_text
    assert "Text on meme: House burning down" in rich_text
    assert "When to use: Smiling in front of catastrophe" in rich_text
    assert "Keywords: fire, girl, smile, disaster" in rich_text
    assert "OCR extracted text: House is fine" in rich_text
    assert "Image shows: A young girl smiles at the camera" in rich_text


def test_embed_text_fallback():
    models = {"text": None}
    vector = embed_text("Simple reaction meme query", models)
    assert isinstance(vector, list)
    assert len(vector) == 384


def test_download_image_error_handling():
    # Empty url should return None
    assert download_image("") is None

    # Invalid url returns None without raising
    with patch("requests.get", side_effect=Exception("Connection error")):
        assert download_image("https://invalid.example.com/meme.jpg") is None


def test_ocr_and_caption_fallbacks():
    # OCR on None or empty
    assert ocr_image(None) == ""

    # Caption on empty models
    assert caption_image(None, models={}) == ""

    # CLIP embed on empty models
    assert embed_image(None, models={}) is None


def test_download_file_utility(tmp_path: Path):
    dest = tmp_path / "test_meme.jpg"
    mock_resp = MagicMock()
    mock_resp.iter_content.return_value = [b"fake_image_bytes"]
    mock_resp.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_resp):
        success = download_file("https://cdn.example.com/test.jpg", dest)
        assert success is True
        assert dest.exists()
        assert dest.read_bytes() == b"fake_image_bytes"


def test_index_memes_dry_run_with_skip_images():
    # Index with skip_images=True and limit=2 should run cleanly without Qdrant/CLIP errors
    index_memes(limit=2, recreate=False, skip_images=True)
