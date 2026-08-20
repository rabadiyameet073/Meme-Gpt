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
GROQ_CONFIG = {
    "model": GROQ_MODEL or "llama-3.1-8b-instant",
    "temperature": 0.1,  # Low = consistent JSON output
    "max_tokens": 200,   # Intent JSON is small
    "top_p": 0.9,
    "timeout": GROQ_TIMEOUT or 5.0,  # Fail fast, use fallback
}

# ── Prompt Inventory (from 05_AI_System/Prompt_Engineering.md) ────────────────

INTENT_PROMPT = """You are a meme recommendation engine. Analyze the user's text and extract structured intent.

User text: "{user_text}"

Return ONLY valid JSON with these fields:
{{
  "emotion": "joy|sadness|anger|surprise|fear|disgust|neutral",
  "situation": "brief description of what's happening",
  "tone": "sarcastic|sincere|humorous|frustrated|excited|resigned",
  "keywords": ["5-8 search keywords for finding relevant memes"],
  "meme_format": "reaction|comparison|advice|relatable|wholesome"
}}

Rules:
- Return ONLY JSON, no markdown, no explanation
- Keywords should include synonyms and related concepts
- Emotion should be the dominant feeling
- Meme_format describes the type of meme that would fit best"""

TAG_PROMPT = """Analyze this meme and return ONLY valid JSON:

Meme name: {meme_name}
Text in image: {ocr_text}
Visual description: {caption}

Return:
{{
  "emotions": ["2-4 emotions this meme expresses"],
  "situations": ["3-5 situations where you'd send this meme"],
  "keywords": ["10 search keywords people would use to find this"],
  "tone": "sarcastic|sincere|humorous|frustrated|excited|relatable",
  "meme_type": "reaction|comparison|advice|relatable|wholesome",
  "alt_text": "Accessible image description for screen readers"
}}"""

ALT_TEXT_PROMPT = """Generate an accessible, concise alt text description for screen readers describing this meme:
Meme name: {meme_name}
Visual description: {caption}
Text inside image: {ocr_text}

Return ONLY the alt text description in 1-2 sentences."""

BLOG_PROMPT = """Write an SEO-optimized blog post:
Title: "Top 20 {topic} Memes of This Week"

Memes available:
{meme_summary}

Include:
- 300-word intro (natural, conversational)
- Meme sections with: name, why it's funny, when to use it
- Conclusion with CTA to try MemeGPT

Target keyword: "{topic_lower} memes"
Tone: funny, relatable, internet-native"""

VALID_EMOTIONS = ["joy", "sadness", "anger", "surprise", "fear", "disgust", "neutral", "humor", "frustration", "anxiety", "triumph", "despair", "stress", "ambition"]
VALID_TONES = ["sarcastic", "sincere", "humorous", "frustrated", "excited", "resigned", "relatable", "dark_humor", "wholesome", "savage"]
VALID_MEME_FORMATS = ["reaction", "comparison", "advice", "relatable", "wholesome", "situational", "template"]


def clean_llm_json(raw_text: str, default: dict | None = None) -> dict:
    """Clean markdown markers and extract JSON block from LLM output."""
    if not raw_text:
        return default or {}

    raw = raw_text.strip()
    # Strip markdown ```json markers
    if raw.startswith("```"):
        parts = raw.split("```")
        if len(parts) >= 2:
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except Exception:
                pass
        return default or {}


INTENT_SYSTEM_PROMPT = INTENT_PROMPT


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


analyze_text = parse_intent
_default_intent = _fallback_intent_parse


def generate_meme_tags(meme_name: str, ocr_text: str = "", caption: str = "") -> dict:
    """Use Groq LLM to generate rich tags for a meme.

    Specification: 05_AI_System/Code_Generation.md
    """
    client = _get_groq_client()
    if client is None:
        return _fallback_meme_tags(meme_name, ocr_text, caption)

    prompt = f"""Analyze this meme and return ONLY valid JSON:

Meme name: {meme_name}
Text in image: {ocr_text}
Visual description: {caption}

Return:
{{
  "emotions": ["list of 2-4 emotions this meme expresses"],
  "situations": ["3-5 situations where you'd send this meme"],
  "keywords": ["10 search keywords people would use to find this"],
  "tone": "sarcastic|sincere|humorous|frustrated|excited|relatable",
  "meme_type": "reaction|comparison|advice|relatable|wholesome",
  "alt_text": "Accessible description for screen readers"
}}"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content.strip()
        tags = json.loads(content)
        return {
            "emotions": tags.get("emotions", ["humor", "relatable"]),
            "situations": tags.get("situations", [f"When dealing with {meme_name.lower()}"]),
            "keywords": tags.get("keywords", [meme_name.lower(), "meme"]),
            "tone": tags.get("tone", "humorous"),
            "meme_type": tags.get("meme_type", "reaction"),
            "alt_text": tags.get("alt_text", f"Meme depicting {meme_name} - {caption}"),
        }
    except Exception as e:
        logger.error(f"Groq tag generation failed: {e}")
        return _fallback_meme_tags(meme_name, ocr_text, caption)


def _fallback_meme_tags(meme_name: str, ocr_text: str = "", caption: str = "") -> dict:
    """Fallback meme tag generator when Groq is offline."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", f"{meme_name} {ocr_text} {caption}".lower())
    keywords = list(dict.fromkeys(words))[:10]
    return {
        "emotions": ["humor", "relatable", "irony"],
        "situations": [
            f"When encountering {meme_name.lower()}",
            "Relatable daily struggles",
            "Humorous reaction in group chat",
        ],
        "keywords": keywords or [meme_name.lower(), "meme"],
        "tone": "relatable",
        "meme_type": "reaction",
        "alt_text": f"Meme depicting {meme_name}. {caption}".strip(),
    }


def generate_alt_text(meme_name: str, caption: str = "", ocr_text: str = "") -> str:
    """Generate concise accessible alt text for screen readers.

    Prompt 3 from 05_AI_System/Prompt_Engineering.md (T=0.3, max_tokens=100).
    """
    client = _get_groq_client()
    if client is None:
        return f"Meme depicting {meme_name}. {caption}".strip()

    prompt = ALT_TEXT_PROMPT.format(meme_name=meme_name, caption=caption, ocr_text=ocr_text)
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.debug(f"Alt text generation fallback: {e}")
        return f"Meme depicting {meme_name}. {caption}".strip()


def generate_weekly_blog_post(topic: str, memes: list[dict]) -> str:
    """Generate an SEO-optimized markdown blog post for a given topic and meme list.

    Specification: 05_AI_System/Code_Generation.md
    """
    client = _get_groq_client()
    if client is None:
        return _fallback_blog_post(topic, memes)

    meme_summary = "\n".join(
        [f"- {m.get('name', 'Meme')}: {m.get('caption', m.get('description', ''))}" for m in memes[:10]]
    )

    prompt = f"""Write an SEO-optimized blog post:
Title: "Top 20 {topic} Memes of This Week"

Memes available:
{meme_summary}

Include:
- 300-word intro (natural, conversational)
- Meme sections with: name, why it's funny, when to use it
- Conclusion with CTA to try MemeGPT

Target keyword: "{topic.lower()} memes"
Tone: funny, relatable, internet-native"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq blog generation failed: {e}")
        return _fallback_blog_post(topic, memes)


def _fallback_blog_post(topic: str, memes: list[dict]) -> str:
    """Fallback template-based markdown blog post."""
    sections = []
    for i, meme in enumerate(memes[:5], 1):
        name = meme.get("name", f"Featured Meme {i}")
        sections.append(
            f"### {i}. {name}\n\n"
            f"**Why it's funny:** Perfectly captures the reality of {topic.lower()} with humor and precision.\n\n"
            f"**When to use it:** When words fail and only a high-impact reaction meme will do."
        )

    sections_str = "\n\n".join(sections)
    return f"""# Top 20 {topic} Memes of This Week

Welcome to this week's definitive roundup of the funniest and most relatable **{topic.lower()} memes** on the internet. Whether you are navigating daily chaos or just looking for the perfect reaction image for your team chat, these memes have you covered.

{sections_str}

## Conclusion

Ready to find the perfect meme for every situation in real time? Try **[MemeGPT](https://memegpt.live)** today and let AI find your next laugh in under 500 milliseconds!
"""


def generate_test_dataset(count: int = 5) -> list[dict]:
    """Generate synthetic test meme records for local integration and benchmarking."""
    templates = [
        ("Distracted Boyfriend", "Man looking back at another woman while his girlfriend looks angry", "disloyalty, temptation"),
        ("This Is Fine", "Dog in a burning room drinking coffee", "denial, crisis, calmness"),
        ("Drake Hotline Bling", "Drake showing disapproval then approval", "preference, decision, comparison"),
        ("Two Buttons", "Man sweating profusely while choosing between two red buttons", "dilemma, tough choice, anxiety"),
        ("Expanding Brain", "Four stages of increasing brain illumination", "intellect, irony, progression"),
    ]

    results = []
    for i in range(min(count, len(templates))):
        name, caption, emotions_str = templates[i]
        tags = _fallback_meme_tags(name, "", caption)
        results.append({
            "id": f"test_meme_{i+1}",
            "name": name,
            "caption": caption,
            "emotions": [e.strip() for e in emotions_str.split(",")],
            "tags": tags,
            "format": "image",
            "url": f"https://example.com/memes/{name.lower().replace(' ', '_')}.jpg",
        })
    return results

