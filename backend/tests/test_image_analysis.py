"""Tests for multi-modal Image Analysis pipeline from 05_AI_System/Image_Analysis.md."""

import numpy as np
from app.services.image_analysis_service import (
    extract_text,
    generate_caption,
    embed_image,
    create_combined_embedding,
    process_meme,
)


def test_create_combined_embedding_normalization_and_weights():
    # 384-dim text and 512-dim image embeddings
    text_emb = [0.1] * 384
    image_emb = [0.2] * 512

    combined = create_combined_embedding(text_emb, image_emb)

    # 1. Total dimensions must be 384 + 512 = 896
    assert len(combined) == 896

    # 2. Must be unit L2 normalized
    arr = np.array(combined)
    norm = np.linalg.norm(arr)
    assert np.isclose(norm, 1.0, atol=1e-4)


def test_embed_image_fallback_dimensions():
    # Calling on non-existent path should return 512-dim vector
    vec = embed_image("non_existent_image.jpg")
    assert isinstance(vec, list)
    assert len(vec) == 512


def test_generate_caption_fallback():
    caption = generate_caption("path/to/distracted_boyfriend.jpg")
    assert isinstance(caption, str)
    assert len(caption) > 0


def test_extract_text_empty_on_missing():
    text = extract_text("missing_file.png")
    assert text == ""


def test_process_meme_full_pipeline():
    result = process_meme("sample_dog_fire.jpg", "This Is Fine")
    assert isinstance(result, dict)
    assert result["name"] == "This Is Fine"
    assert "text_embedding" in result
    assert len(result["text_embedding"]) == 384
    assert "image_embedding" in result
    assert len(result["image_embedding"]) == 512
    assert "combined_embedding" in result
    assert len(result["combined_embedding"]) == 896
    assert "emotions" in result
    assert "keywords" in result
    assert "composed_text" in result
