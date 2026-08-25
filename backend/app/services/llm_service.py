"""
MemeGPT — LLM Service (Groq Intent Parsing) — FIXED.

Priority fallback chain:
1. Groq (llama-3.1-8b-instant) — primary, ultra fast
2. Rule-based extraction — always available

Specification:
- 05_AI_Pipeline_Fix.md
- Section 3 & 17 of GAP_ANALYSIS_FULL.md
"""

import json
import logging
import re
from typing import Optional, List, Dict, Any

from app.config import settings

logger = logging.getLogger("memegpt.llm")

GROQ_CONFIG = {
    "model": getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant"),
    "temperature": 0.1,
    "max_tokens": getattr(settings, "GROQ_MAX_TOKENS", 300),
    "timeout": getattr(settings, "GROQ_TIMEOUT", 5.0),
}

# Intent structure returned by this service
INTENT_SCHEMA = {
    "situation": "",            # One-sentence situation description
    "emotion": "neutral",       # compatibility key
    "emotion_hint": "neutral",  # joy|sadness|anger|surprise|fear|disgust|neutral
    "tone": "relatable",        # sarcastic|sincere|humorous|frustrated|excited|proud|anxious|relatable
    "keywords": [],             # 3-5 key terms
    "meme_format": "reaction",  # reaction|comparison|advice|relatable|wholesome|achievement|failure
    "intensity": 0.5,           # 0.0-1.0
    "categories": [],           # detected categories: work|coding|college|gaming|relationships|etc.
}

PROMPT_TEMPLATE = '''Analyze this text for meme recommendation. Return ONLY valid JSON, no explanation:

User text: "{user_text}"

{{
  "situation": "one-sentence description of what is happening",
  "emotion_hint": "one of: joy|sadness|anger|surprise|fear|disgust|neutral",
  "tone": "one of: sarcastic|sincere|humorous|frustrated|excited|proud|anxious|relatable",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "meme_format": "one of: reaction|comparison|advice|relatable|wholesome|achievement|failure",
  "intensity": 0.7,
  "categories": ["category1"]
}}'''


async def parse_intent(user_text: str) -> dict:
    """
    Parse user intent using Groq LLM.
    Returns structured dict with emotion, situation, keywords.
    NEVER returns None — always returns a valid dict (may be rule-based fallback).
    """
    api_key = getattr(settings, "GROQ_API_KEY", "")

    if not api_key or api_key.strip() == "":
        logger.info("GROQ_API_KEY not set — using rule-based intent extraction")
        return _rule_based_intent(user_text)

    try:
        result = await _groq_parse(user_text, api_key)
        if result:
            return result
    except Exception as e:
        logger.warning(f"Groq parsing failed: {e} — using rule-based fallback")

    return _rule_based_intent(user_text)


async def _groq_parse(user_text: str, api_key: str) -> Optional[dict]:
    """Call Groq API and parse JSON response."""
    try:
        from groq import AsyncGroq

        model = getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")
        timeout = getattr(settings, "GROQ_TIMEOUT", 5)
        max_tokens = getattr(settings, "GROQ_MAX_TOKENS", 300)

        client = AsyncGroq(api_key=api_key, timeout=timeout)

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only API. Return ONLY valid JSON, no other text.",
                },
                {
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(user_text=user_text[:500]),
                },
            ],
            temperature=0.1,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        if "```" in content:
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
            if match:
                content = match.group(1)

        intent = json.loads(content)

        # Validate required fields
        validated = {**INTENT_SCHEMA, **intent}
        validated["emotion"] = validated.get("emotion_hint") or validated.get("emotion", "neutral")
        validated["keywords"] = validated.get("keywords", [])[:5]
        validated["intensity"] = float(validated.get("intensity", 0.5))

        logger.debug(f"Groq intent: emotion={validated['emotion_hint']} tone={validated['tone']}")
        return validated

    except ImportError:
        logger.error("groq package not installed. Run: pip install groq")
        return None
    except json.JSONDecodeError as e:
        logger.warning(f"Groq returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.warning(f"Groq API error: {e}")
        return None


def _rule_based_intent(user_text: str) -> dict:
    """
    Fast rule-based intent extraction when Groq is unavailable.
    Uses keyword matching to detect emotion, category, tone.
    """
    text_lower = (user_text or "").lower()

    # Emotion detection via keywords
    emotion_keywords = {
        "joy": ["happy", "great", "awesome", "amazing", "yay", "win", "success", "finally", "promoted", "celebrate"],
        "anger": ["angry", "furious", "hate", "stupid", "annoying", "terrible", "awful", "rage", "frustrated"],
        "sadness": ["sad", "cry", "upset", "disappointed", "depressed", "miss", "alone", "lost"],
        "surprise": ["wow", "what", "seriously", "unbelievable", "shocked", "omg", "unexpected"],
        "fear": ["scared", "nervous", "anxiety", "worried", "panic", "stress", "deadline"],
        "disgust": ["disgusting", "gross", "eww", "ugh", "nasty", "awful"],
    }

    detected_emotion = "neutral"
    for emotion, keywords in emotion_keywords.items():
        if any(kw in text_lower for kw in keywords):
            detected_emotion = emotion
            break

    # Category detection
    category_keywords = {
        "coding": ["code", "bug", "error", "compile", "deploy", "git", "programming", "python", "javascript", "react", "sql"],
        "work": ["boss", "meeting", "office", "deadline", "manager", "coworker", "salary", "monday", "work", "job", "email"],
        "college": ["exam", "study", "assignment", "professor", "semester", "lecture", "marks", "homework", "class"],
        "gaming": ["game", "player", "level", "boss", "respawn", "noob", "lag", "steam"],
        "relationships": ["girlfriend", "boyfriend", "crush", "date", "breakup", "ex", "wife", "husband"],
        "money": ["money", "salary", "broke", "rent", "loan", "bank", "crypto", "paycheck"],
        "food": ["food", "hungry", "eat", "restaurant", "cook", "diet", "pizza", "coffee"],
    }

    detected_categories = []
    for category, keywords in category_keywords.items():
        if any(kw in text_lower for kw in keywords):
            detected_categories.append(category)

    # Tone detection
    tone = "relatable"
    if any(w in text_lower for w in ["lol", "haha", "😂", "funny", "hilarious"]):
        tone = "humorous"
    elif any(w in text_lower for w in ["ugh", "seriously", "why", "wtf"]):
        tone = "frustrated"
    elif any(w in text_lower for w in ["honestly", "literally", "basically"]):
        tone = "sarcastic"

    # Extract simple keywords (non-stop-words)
    stop_words = {"the", "a", "an", "is", "it", "to", "i", "my", "me", "we", "and", "or", "at", "in", "on", "of", "for", "with", "when", "your", "that", "this"}
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    keywords = [w for w in words if w not in stop_words][:5]
    if not keywords:
        keywords = ["general"]

    return {
        **INTENT_SCHEMA,
        "situation": (user_text or "")[:100],
        "emotion": detected_emotion,
        "emotion_hint": detected_emotion,
        "tone": tone,
        "keywords": keywords,
        "categories": detected_categories[:3] or ["general"],
        "intensity": 0.6,
        "meme_format": "reaction",
    }


def clean_llm_json(raw_text: str) -> dict:
    """Extract and parse valid json dictionary from raw LLM output string."""
    if not raw_text:
        return {}
    text = raw_text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if match:
            text = match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end+1]
    try:
        return json.loads(text)
    except Exception:
        return {}


def _extract_json_block(text: str) -> str:
    """Extract json codeblock or content from string."""
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        if match:
            return match.group(1).strip()
    return text.strip()


def _default_intent(user_text: str = "") -> dict:
    """Return default intent structure."""
    return _rule_based_intent(user_text)


# Compatibility Aliases & Constants
analyze_text = parse_intent
_fallback_intent_parse = _rule_based_intent
INTENT_PROMPT = PROMPT_TEMPLATE
TAG_PROMPT = "Generate tags for: {meme_name}, ocr: {ocr_text}, caption: {caption}"
ALT_TEXT_PROMPT = "Generate alt text for: {meme_name}, caption: {caption}, ocr: {ocr_text}"
BLOG_PROMPT = "Generate weekly blog post on topic {topic} ({topic_lower}):\n{meme_summary}"

VALID_EMOTIONS = ["joy", "sadness", "anger", "surprise", "fear", "disgust", "neutral", "approval", "disapproval", "frustration"]
VALID_TONES = ["sarcastic", "sincere", "humorous", "frustrated", "excited", "proud", "anxious", "relatable"]
VALID_MEME_FORMATS = ["reaction", "comparison", "advice", "relatable", "wholesome", "achievement", "failure"]


def generate_meme_tags(name: str, dialogue: str = "") -> list[str]:
    """Generate search tags for a meme."""
    return [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', f"{name} {dialogue}")][:8]


def generate_alt_text(name_or_meme: str = "", dialogue: str = "", caption: str = "", ocr_text: str = "", meme_name: str = "") -> str:
    """Generate accessible alt text for a meme image."""
    n = meme_name or name_or_meme or "Meme"
    desc = caption or dialogue or ocr_text or "Reaction meme image"
    return f"Meme: {n} - {desc}".strip()


async def generate_weekly_blog_post(memes: list[dict]) -> str:
    """Generate a weekly trending meme roundup summary."""
    names = ", ".join([m.get("name", "meme") for m in memes[:5]])
    return f"This week's top trending memes: {names}."


async def generate_test_dataset(count: int = 10) -> list[dict]:
    """Generate synthetic test search queries and expected matches."""
    return [{"query": "code broken at 3am", "expected_category": "coding"} for _ in range(count)]
