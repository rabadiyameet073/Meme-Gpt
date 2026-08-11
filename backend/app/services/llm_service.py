"""MemeGPT — LLM Intent Parsing Service (Groq API).

Uses Groq's free API with Llama 3.1-8B-Instant for real-time intent parsing.
Target latency: ~300ms per request.
Fallback: keyword-only extraction if Groq is unavailable or API key missing.

Specification: 02_TECH_STACK_AND_MODELS.md, 05_AI_System/LLM_Workflow.md
"""

import json
import logging
import re
from typing import Optional

from app.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TIMEOUT

logger = logging.getLogger("memegpt.llm")

_groq_client = None


def _get_groq_client():
    """Lazy-initialize the Groq client."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client

    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — LLM intent parsing disabled, using fallback")
        return None

    try:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT)
        logger.info("✅ Groq LLM client initialized")
        return _groq_client
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None


# ── System prompt for intent parsing (from LLM_Workflow.md) ───────────────────

INTENT_SYSTEM_PROMPT = """You are MemeGPT's intent parser. Given a user's text describing a situation, feeling, or conversation, extract structured information for meme recommendation.

You MUST respond with ONLY a valid JSON object. No markdown, no explanation, no extra text.

JSON schema:
{
  "situation": "brief description of what's happening",
  "emotion": "primary emotion (one of: frustration, anxiety, triumph, despair, humor, stress, ambition)",
  "tone": "desired meme tone (one of: humorous, sarcastic, dark_humor, wholesome, savage, relatable)",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "meme_format": "reaction or situational or template",
  "categories": ["category1", "category2"]
}

Available categories: coding, startup, relationship, college, office, funny, motivation, unrealistic_goals, ai, business, exam, failure, success, gaming, bollywood, youtube, money, sleep

Example input: "My boss called at midnight to ask about a report that's due next month"
Example output: {"situation": "boss calling at midnight for non-urgent work", "emotion": "frustration", "tone": "sarcastic", "keywords": ["boss", "midnight", "work", "overwork"], "meme_format": "reaction", "categories": ["office", "funny"]}
"""


async def parse_intent(user_text: str) -> dict:
    """Parse user text into structured intent using Groq LLM.

    Returns a dict with keys: situation, emotion, tone, keywords, meme_format, categories.
    Falls back to keyword extraction if LLM is unavailable.
    """
    client = _get_groq_client()

    if client is None:
        return _fallback_intent_parse(user_text)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.3,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()

        # Parse the JSON response
        try:
            intent = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if json_match:
                intent = json.loads(json_match.group())
            else:
                logger.warning(f"Failed to parse LLM response as JSON: {raw[:200]}")
                return _fallback_intent_parse(user_text)

        # Validate and normalize
        return {
            "situation": intent.get("situation", user_text[:100]),
            "emotion": intent.get("emotion", "humor"),
            "tone": intent.get("tone", "humorous"),
            "keywords": intent.get("keywords", [])[:10],
            "meme_format": intent.get("meme_format", "reaction"),
            "categories": intent.get("categories", ["funny"])[:3],
        }

    except Exception as e:
        logger.error(f"Groq LLM request failed: {e}")
        return _fallback_intent_parse(user_text)


def _fallback_intent_parse(user_text: str) -> dict:
    """Keyword-based intent extraction when LLM is unavailable.

    Uses the existing rule engine for category/emotion detection.
    """
    from app.rule_engine import run_rule_engine, detect_emotion

    rules = run_rule_engine(user_text)
    emotion = detect_emotion(user_text)

    # Extract simple keywords from the text
    words = re.findall(r"\b[a-zA-Z]{3,}\b", user_text.lower())
    # Filter out common stopwords
    stopwords = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can",
        "had", "her", "was", "one", "our", "out", "has", "his", "how",
        "its", "may", "new", "now", "old", "see", "way", "who", "did",
        "get", "got", "him", "let", "say", "she", "too", "use", "than",
        "that", "this", "with", "from", "have", "been", "were", "they",
        "will", "when", "what", "just", "like", "know", "about", "into",
        "your", "some", "them", "then", "very", "made", "make", "much",
    }
    keywords = [w for w in words if w not in stopwords][:8]

    return {
        "situation": user_text[:100],
        "emotion": emotion.get("primary", "humor"),
        "tone": "humorous",
        "keywords": keywords,
        "meme_format": "reaction",
        "categories": rules.categories[:3] or ["funny"],
    }
