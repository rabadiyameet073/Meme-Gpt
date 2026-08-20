"""MemeGPT — Text Composer & Chunking Strategy.

Implements the specification from 05_AI_System/Chunking.md.
Composes multiple meme metadata fields into a dense, high-signal text
optimized for MiniLM sentence embedding.
"""

from typing import Any


def compose_meme_text(meme: dict[str, Any]) -> str:
    """Combine all meme metadata fields into a single rich text

    optimized for MiniLM embedding.

    Order matters! Most important info first — embedding models
    pay more attention to early tokens.
    """
    parts = []

    # 1. Name (most important — users search by meme name)
    name = (meme.get("name") or "").strip()
    if name:
        parts.append(f"Meme: {name}.")

    # 2. Description/caption (visual content)
    caption = (meme.get("blip_caption") or meme.get("caption") or meme.get("description") or "").strip()
    if caption:
        parts.append(f"Shows: {caption}.")

    # 3. OCR text (text visible in the meme image, skipped if identical to name or too short)
    ocr = (meme.get("ocr_text") or meme.get("dialogue") or "").strip()
    if ocr and len(ocr) > 3 and ocr.lower() != name.lower():
        parts.append(f"Text in image: {ocr}.")

    # 4. Emotional tags (critical for emotion-based search)
    emotions = meme.get("emotions")
    if emotions:
        if isinstance(emotions, list):
            emotion_str = ", ".join(str(e) for e in emotions if str(e).strip())
        else:
            emotion_str = str(emotions).strip()
        if emotion_str:
            parts.append(f"Emotions: {emotion_str}.")

    # 5. Situations (contextual usage)
    situations = meme.get("situations")
    if situations:
        if isinstance(situations, list):
            sit_str = ", ".join(str(s) for s in situations[:5] if str(s).strip())
        else:
            sit_str = str(situations).strip()
        if sit_str:
            parts.append(f"Used when: {sit_str}.")

    # 6. Categories
    categories = meme.get("categories")
    if categories:
        if isinstance(categories, list):
            cat_str = ", ".join(str(c) for c in categories if str(c).strip())
        else:
            cat_str = str(categories).strip()
        if cat_str:
            parts.append(f"Categories: {cat_str}.")

    # 7. Keywords (LLM-generated search terms)
    keywords = meme.get("keywords")
    if keywords:
        if isinstance(keywords, list):
            kw_str = ", ".join(str(k) for k in keywords[:10] if str(k).strip())
        else:
            kw_str = str(keywords).strip()
        if kw_str:
            parts.append(f"Keywords: {kw_str}.")

    composed = " ".join(parts)

    # Truncate to 512 tokens (MiniLM limit ~2048 chars)
    return composed[:2048]


def compose_query_text(
    user_text: str,
    intent: dict[str, Any] | None = None,
    emotion: dict[str, Any] | None = None,
) -> str:
    """Compose rich structured query text for online embedding."""
    intent = intent or {}
    emotion = emotion or {}

    primary_emo = emotion.get("primary", "")
    sec_emo = emotion.get("secondary", "")
    emo_str = f"{primary_emo}, {sec_emo}".strip(" ,") if sec_emo else primary_emo

    keywords = intent.get("keywords", [])
    kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)

    lines = [
        f"User said: {user_text}",
    ]
    if intent.get("situation"):
        lines.append(f"Situation: {intent['situation']}")
    if emo_str:
        lines.append(f"Emotion: {emo_str}")
    if intent.get("tone"):
        lines.append(f"Tone: {intent['tone']}")
    if kw_str:
        lines.append(f"Keywords: {kw_str}")
    if intent.get("meme_format"):
        lines.append(f"Meme type needed: {intent['meme_format']}")

    return "\n".join(lines).strip()
