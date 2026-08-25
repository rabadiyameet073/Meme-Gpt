#!/usr/bin/env python3
"""
MemeGPT — Imgflip Meme Scraper.
Fetches top memes from Imgflip API and adds to DB.

Imgflip API: https://api.imgflip.com/get_memes
- Returns top 100 memes with name, url, box_count
- Free, no API key needed

Run: python scripts/scrape_imgflip.py
"""

import json
import logging
import re
import sys
import uuid
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scraper.imgflip")

IMGFLIP_API = "https://api.imgflip.com/get_memes"

# Category mapping for common meme names
CATEGORY_MAP = {
    "drake": ["reaction", "comparison"],
    "distracted": ["relationships", "comparison"],
    "pikachu": ["gaming", "reaction"],
    "this is fine": ["work", "stress"],
    "bernie": ["reaction", "political"],
    "mocking": ["reaction", "sarcastic"],
    "change my mind": ["debate", "opinion"],
    "expanding brain": ["comparison", "ironic"],
    "two buttons": ["decision", "struggle"],
    "woman yelling": ["reaction", "anger"],
    "coffin dance": ["wholesome", "viral"],
    "kermit": ["reaction", "opinion"],
    "roll safe": ["advice", "smart"],
    "success kid": ["achievement", "win"],
    "first world problems": ["complaint", "ironic"],
    "batman slapping": ["reaction", "correction"],
    "doge": ["reaction", "wow"],
    "disaster girl": ["evil", "chaos"],
    "one does not simply": ["difficulty", "work"],
    "always has been": ["realization", "twist"],
    "crying cat": ["sadness", "relatable"],
    "gru plan": ["planning", "backfire"],
    "monday": ["work", "week"],
    "sleeping": ["tired", "relatable"],
}

EMOTION_MAP = {
    "drake": ["approval", "disapproval"],
    "pikachu": ["surprise", "shock"],
    "this is fine": ["denial", "calm"],
    "distracted": ["temptation", "desire"],
    "crying cat": ["sadness", "disappointment"],
    "success kid": ["joy", "pride"],
    "disaster girl": ["mischief", "satisfaction"],
    "one does not simply": ["seriousness", "warning"],
}


def slugify(name: str) -> str:
    """Convert meme name to URL slug."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug[:100]


def get_categories(name: str) -> list[str]:
    """Guess meme categories from name."""
    name_lower = name.lower()
    for keyword, cats in CATEGORY_MAP.items():
        if keyword in name_lower:
            return cats
    return ["reaction", "general"]


def get_emotions(name: str) -> list[str]:
    """Guess meme emotions from name."""
    name_lower = name.lower()
    for keyword, emotions in EMOTION_MAP.items():
        if keyword in name_lower:
            return emotions
    return []


def get_keywords(name: str) -> list[str]:
    """Extract keywords from meme name."""
    stop_words = {"the", "a", "an", "is", "of", "my", "and", "or", "to", "in", "with"}
    words = re.findall(r'\b[a-z]{3,}\b', name.lower())
    return [w for w in words if w not in stop_words][:8]


def scrape_imgflip() -> list[dict]:
    """Fetch memes from Imgflip API."""
    logger.info(f"Fetching memes from {IMGFLIP_API}...")
    resp = requests.get(IMGFLIP_API, timeout=15)
    resp.raise_for_status()

    data = resp.json()
    if not data.get("success"):
        raise ValueError(f"Imgflip API error: {data}")

    memes = data["data"]["memes"]
    logger.info(f"Received {len(memes)} memes from Imgflip")
    return memes


def seed_imgflip_memes():
    """Fetch memes from Imgflip and insert into DB."""
    from app.database import SessionLocal, Meme

    try:
        raw_memes = scrape_imgflip()
    except Exception as e:
        logger.warning(f"Could not reach Imgflip API ({e}) — using fallback seed data")
        return 0

    db = SessionLocal()
    added = 0
    skipped = 0

    try:
        for raw in raw_memes:
            name = raw.get("name", "").strip()
            imgflip_id = str(raw.get("id", ""))
            image_url = raw.get("url", "")

            if not name or not imgflip_id:
                continue

            slug = slugify(name)
            categories = get_categories(name)
            emotions = get_emotions(name)
            keywords = get_keywords(name)

            existing = db.query(Meme).filter((Meme.slug == slug) | (Meme.id == imgflip_id)).first()
            if existing:
                if not existing.image_url:
                    existing.image_url = image_url
                    existing.image_ref = image_url
                skipped += 1
                continue

            explanation = (
                f"Use the {name} meme when you want to express {', '.join(emotions) or 'relatable humor'}. "
                f"Common in {', '.join(categories)} contexts."
            )

            meme = Meme(
                id=imgflip_id,
                name=name,
                slug=slug,
                categories=categories,
                emotions=emotions,
                keywords=keywords,
                explanation=explanation,
                dialogue="",
                image_url=image_url,
                image_ref=image_url,
                source="imgflip",
                nsfw=False,
                popularity_score=0.7,
            )
            db.add(meme)
            added += 1

        db.commit()
        logger.info(f"✅ Seeded {added} Imgflip memes ({skipped} skipped/updated)")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
    finally:
        db.close()

    return added


if __name__ == "__main__":
    seed_imgflip_memes()
