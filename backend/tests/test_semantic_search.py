"""Embedding & Semantic Search Tests from 10_Testing/Backend_Tests.md."""

import math
from app.semantic_search import embed_text


def test_embed_text_dimensions():
    vec = embed_text("hello world")
    assert len(vec) == 384


def test_embed_text_normalized():
    vec = embed_text("test query")
    norm = math.sqrt(sum(v**2 for v in vec))
    assert abs(norm - 1.0) < 0.02  # L2 normalized
