"""Tests for MemeGPT's specialized RAG pipeline from 05_AI_System/RAG.md."""

import pytest
from app.services.rag_service import rag_recommend


@pytest.mark.asyncio
async def test_rag_recommend_three_stages_and_metadata():
    query = "when you fix a bug in production and break 5 other things"
    result = await rag_recommend(query=query, format_pref="image", limit=3, top_k_candidates=5)

    # 1. Top-level response contract
    assert isinstance(result, dict)
    assert result["query"] == query
    assert "memes" in result
    assert isinstance(result["memes"], list)

    # 2. Stage metadata inspection
    assert "rag_metadata" in result
    meta = result["rag_metadata"]

    # Stage 1: Query Enrichment
    assert "query_enrichment" in meta
    assert "intent" in meta["query_enrichment"]
    assert "emotion" in meta["query_enrichment"]
    assert "composed_query" in meta["query_enrichment"]
    assert "latency_ms" in meta["query_enrichment"]

    # Stage 2: ANN Vector Retrieval
    assert "retrieval" in meta
    assert meta["retrieval"]["vector_dim"] == 384
    assert meta["retrieval"]["candidates_retrieved"] >= 0

    # Stage 3: Augmentation / Re-ranking (No LLM generation hallucination)
    assert "augmentation" in meta
    assert meta["augmentation"]["strategy"] == "composite_rerank_no_hallucination"
    assert len(meta["augmentation"]["signals_applied"]) >= 4

    # Total latency
    assert "total_latency_ms" in meta
    assert meta["total_latency_ms"] >= 0


@pytest.mark.asyncio
async def test_rag_recommend_urls_present():
    result = await rag_recommend("monday morning standup meeting", limit=2)
    memes = result["memes"]
    if memes:
        first_meme = memes[0]
        assert "urls" in first_meme
        assert "original" in first_meme["urls"]
        assert "webp" in first_meme["urls"]
