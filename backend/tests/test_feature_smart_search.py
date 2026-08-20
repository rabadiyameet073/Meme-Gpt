"""Tests for Smart Meme Search from 08_Features/Smart_Meme_Search.md."""

from app.services.smart_search_service import (
    calculate_smart_search_composite_score,
    preprocess_smart_search_query,
    evaluate_search_quality_metrics,
    get_search_pipeline_steps,
)


def test_composite_scoring_formula():
    # Base only
    s1 = calculate_smart_search_composite_score(0.80)
    assert s1 == 0.80

    # With primary emotion boost (+0.15) and popularity (+0.10 * 0.5 = +0.05)
    s2 = calculate_smart_search_composite_score(
        cosine_similarity=0.70,
        primary_emotion_match=True,
        popularity_score=0.50,
    )
    # 0.70 + 0.15 + 0.05 = 0.90
    assert abs(s2 - 0.90) < 1e-4

    # With all boosts (+0.15, +0.08, +0.10*1.0, +0.05)
    s3 = calculate_smart_search_composite_score(
        cosine_similarity=0.85,
        primary_emotion_match=True,
        secondary_emotion_match=True,
        popularity_score=1.0,
        format_preference_match=True,
    )
    # 0.85 + 0.15 + 0.08 + 0.10 + 0.05 = 1.23 -> capped at 1.0
    assert s3 == 1.0


def test_query_preprocessing_edge_cases():
    # Normal query
    p_norm = preprocess_smart_search_query("when your code compiles but output is wrong")
    assert p_norm["clean_query"] == "when your code compiles but output is wrong"
    assert p_norm["is_chat_paste"] is False
    assert p_norm["is_gibberish"] is False

    # Multi-line chat log paste
    chat_log = "User A: did you see the PR?\nUser B: yeah it failed CI\nUser A: again?"
    p_chat = preprocess_smart_search_query(chat_log)
    assert p_chat["is_chat_paste"] is True
    assert "User A: did you see the PR? | User B: yeah it failed CI | User A: again?" in p_chat["clean_query"]

    # Emoji-only query
    p_emoji = preprocess_smart_search_query("😂😂😂 💀")
    assert p_emoji["is_emoji_only"] is True

    # Gibberish query
    p_gibberish = preprocess_smart_search_query("zqwxrtpkln")
    assert p_gibberish["is_gibberish"] is True
    assert p_gibberish["suggest_try_something_else"] is True


def test_ir_evaluation_metrics():
    retrieved = ["meme_1", "meme_2", "meme_3", "meme_4", "meme_5", "meme_6", "meme_7", "meme_8", "meme_9", "meme_10"]
    relevant = {"meme_1", "meme_3", "meme_5", "meme_9", "meme_12"}

    metrics = evaluate_search_quality_metrics(retrieved, relevant)

    # Precision@3: 2 relevant in top 3 (meme_1, meme_3) -> 2/3 = 0.6667
    assert abs(metrics["precision_at_3"] - 0.6667) < 0.001

    # Precision@5: 3 relevant in top 5 (meme_1, meme_3, meme_5) -> 3/5 = 0.60
    assert metrics["precision_at_5"] == 0.60

    # Recall@10: 4 relevant in top 10 (meme_1, meme_3, meme_5, meme_9) out of 5 -> 4/5 = 0.80
    assert metrics["recall_at_10"] == 0.80

    # MRR: First relevant is at rank 1 -> 1/1 = 1.0
    assert metrics["mrr"] == 1.0

    # NDCG@5 > 0.60
    assert metrics["ndcg_at_5"] > 0.60


def test_pipeline_steps():
    steps = get_search_pipeline_steps()
    assert len(steps) == 6
    step_names = [s["name"] for s in steps]
    assert "Intent Parsing" in step_names
    assert "Emotion Detection" in step_names
    assert "Query Building" in step_names
    assert "Embedding" in step_names
    assert "Vector Search" in step_names
    assert "Re-ranking" in step_names
