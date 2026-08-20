"""Tests for embedding service and multimodal vector combinations from 05_AI_System/Embeddings.md."""

import numpy as np
from app.services.embedding_service import (
    embed_text,
    detect_emotion,
    get_combined_embedding,
)


def test_embed_text_dimensions():
    vec = embed_text("when code compiles on the first attempt")
    assert isinstance(vec, list)
    assert len(vec) == 384


def test_get_combined_embedding_math_and_dimensions():
    # Simulate 384-dim text and 512-dim image vectors
    text_emb = [0.1] * 384
    image_emb = [0.2] * 512

    combined = get_combined_embedding(text_emb, image_emb, text_weight=0.65, image_weight=0.35)

    # 1. Total dimensions must be 384 + 512 = 896
    assert len(combined) == 896

    # 2. Must be unit L2 normalized
    arr = np.array(combined)
    norm = np.linalg.norm(arr)
    assert np.isclose(norm, 1.0, atol=1e-4)


def test_detect_emotion_classes():
    emo = detect_emotion("I am super excited and happy about this new release!")
    assert "primary" in emo
    assert "confidence" in emo
    # Known 7 classes: anger, disgust, fear, joy, neutral, sadness, surprise
    valid_classes = {"anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise", "humor", "frustration", "anxiety", "triumph", "despair", "stress", "ambition"}
    assert emo["primary"] in valid_classes
