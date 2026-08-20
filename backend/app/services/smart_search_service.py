"""Smart Meme Search Deep Dive Service for MemeGPT.
Specification: 08_Features/Smart_Meme_Search.md
"""

import math
import re
from typing import Any, Dict, List, Optional, Set

PRIMARY_EMOTION_BOOST = 0.15
SECONDARY_EMOTION_BOOST = 0.08
POPULARITY_WEIGHT = 0.10
FORMAT_PREFERENCE_BOOST = 0.05
MAX_SEARCH_TEXT_LENGTH = 2000


def calculate_smart_search_composite_score(
    cosine_similarity: float,
    primary_emotion_match: bool = False,
    secondary_emotion_match: bool = False,
    popularity_score: float = 0.0,
    format_preference_match: bool = False,
) -> float:
    """Calculate composite search score from 08_Features/Smart_Meme_Search.md.
    
    Formula:
        final_score = (
            cosine_similarity
            + (0.15 if primary_emotion_match else 0.0)
            + (0.08 if secondary_emotion_match else 0.0)
            + (popularity_score * 0.10)
            + (0.05 if format_preference_match else 0.0)
        )
    Capped at 1.0.
    """
    base = max(0.0, min(1.0, float(cosine_similarity)))
    pop = max(0.0, min(1.0, float(popularity_score)))

    score = base
    if primary_emotion_match:
        score += PRIMARY_EMOTION_BOOST
    if secondary_emotion_match:
        score += SECONDARY_EMOTION_BOOST
    score += pop * POPULARITY_WEIGHT
    if format_preference_match:
        score += FORMAT_PREFERENCE_BOOST

    return round(min(1.0, max(0.0, score)), 4)


def preprocess_smart_search_query(raw_query: str) -> Dict[str, Any]:
    """Preprocess and sanitize search queries, handling chat log pastes, emojis, and gibberish."""
    if not raw_query:
        return {
            "clean_query": "",
            "is_chat_paste": False,
            "is_emoji_only": False,
            "is_gibberish": False,
            "suggest_try_something_else": True,
        }

    # Truncate to maximum characters
    truncated = raw_query[:MAX_SEARCH_TEXT_LENGTH].strip()

    # Detect multi-line conversation paste
    lines = [l.strip() for l in truncated.splitlines() if l.strip()]
    is_chat_paste = len(lines) >= 2 or any(":" in l for l in lines)

    # Flatten chat paste to semantic context
    if is_chat_paste:
        clean_text = " | ".join(lines)
    else:
        clean_text = " ".join(truncated.split())

    # Check emoji-only
    non_ascii_chars = [c for c in clean_text if ord(c) > 127]
    ascii_letters = [c for c in clean_text if c.isalnum()]
    is_emoji_only = len(non_ascii_chars) > 0 and len(ascii_letters) == 0

    # Simple gibberish heuristic: long repeated chars or low vowel ratio with length > 6
    is_gibberish = False
    if len(ascii_letters) >= 7 and not is_chat_paste:
        letters_only = "".join(ascii_letters).lower()
        vowels = sum(1 for c in letters_only if c in "aeiou")
        consonants = len(letters_only) - vowels
        if vowels == 0 or (consonants > 6 and vowels / len(letters_only) < 0.15):
            is_gibberish = True

    return {
        "clean_query": clean_text,
        "is_chat_paste": is_chat_paste,
        "is_emoji_only": is_emoji_only,
        "is_gibberish": is_gibberish,
        "suggest_try_something_else": is_gibberish,
    }


def evaluate_search_quality_metrics(
    retrieved_ids: List[str],
    relevant_ids: Set[str],
    relevant_scores_map: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Calculate Information Retrieval (IR) quality metrics specified in Smart_Meme_Search.md.
    
    Metrics:
        - Precision@3: Relevant in top-3 ÷ 3
        - Precision@5: Relevant in top-5 ÷ 5
        - Recall@10: Relevant in top-10 ÷ total relevant
        - MRR: Mean Reciprocal Rank of first relevant item
        - NDCG@5: Normalized Discounted Cumulative Gain
    """
    total_relevant = len(relevant_ids)
    if total_relevant == 0:
        return {
            "precision_at_3": 0.0,
            "precision_at_5": 0.0,
            "recall_at_10": 0.0,
            "mrr": 0.0,
            "ndcg_at_5": 0.0,
        }

    # Precision@3
    top3 = retrieved_ids[:3]
    p_at_3 = sum(1 for mid in top3 if mid in relevant_ids) / 3.0

    # Precision@5
    top5 = retrieved_ids[:5]
    p_at_5 = sum(1 for mid in top5 if mid in relevant_ids) / 5.0

    # Recall@10
    top10 = retrieved_ids[:10]
    recall_at_10 = sum(1 for mid in top10 if mid in relevant_ids) / float(total_relevant)

    # MRR (Mean Reciprocal Rank)
    mrr = 0.0
    for idx, mid in enumerate(retrieved_ids, start=1):
        if mid in relevant_ids:
            mrr = 1.0 / idx
            break

    # NDCG@5
    scores_map = relevant_scores_map or {mid: 1.0 for mid in relevant_ids}
    dcg_5 = 0.0
    for idx, mid in enumerate(top5, start=1):
        rel = scores_map.get(mid, 0.0)
        dcg_5 += rel / math.log2(idx + 1)

    # Ideal DCG@5
    ideal_scores = sorted([scores_map.get(mid, 1.0) for mid in relevant_ids], reverse=True)[:5]
    idcg_5 = sum(score / math.log2(i + 2) for i, score in enumerate(ideal_scores))
    ndcg_5 = (dcg_5 / idcg_5) if idcg_5 > 0.0 else 0.0

    return {
        "precision_at_3": round(p_at_3, 4),
        "precision_at_5": round(p_at_5, 4),
        "recall_at_10": round(min(1.0, recall_at_10), 4),
        "mrr": round(mrr, 4),
        "ndcg_at_5": round(min(1.0, ndcg_5), 4),
    }


def get_search_pipeline_steps() -> List[Dict[str, Any]]:
    """Return the 6-step internal search pipeline architecture specification."""
    return [
        {
            "step": "A",
            "name": "Intent Parsing",
            "model": "Groq Llama 3.1 8B",
            "latency": "~300ms",
            "output": "{emotion, situation, tone, keywords, format}",
        },
        {
            "step": "B",
            "name": "Emotion Detection",
            "model": "DistilRoBERTa",
            "latency": "~100ms",
            "output": "{primary, secondary, confidence}",
        },
        {
            "step": "C",
            "name": "Query Building",
            "model": "Combiner",
            "latency": "<10ms",
            "output": "Rich query text (user + intent + emotion)",
        },
        {
            "step": "D",
            "name": "Embedding",
            "model": "MiniLM-L6-v2",
            "latency": "~50ms",
            "output": "384-dimensional vector",
        },
        {
            "step": "E",
            "name": "Vector Search",
            "engine": "Qdrant / In-Memory Cosine Index",
            "latency": "~50ms",
            "output": "Top 10 candidates",
        },
        {
            "step": "F",
            "name": "Re-ranking",
            "engine": "Composite Scoring Logic",
            "latency": "~10ms",
            "output": "Top 5 results with final scores",
        },
    ]
