"""
MemeGPT — Collect meme templates from Imgflip and seed into SQLite.
No API key needed for the public memes endpoint.
Specification: 04_Meme_Data_Pipeline.md
"""
import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

import httpx
from app.database import SessionLocal, Meme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("imgflip")

IMGFLIP_URL = "https://api.imgflip.com/get_memes"

# Meme category mapping based on name keywords
CATEGORY_MAP = {
    "programming": ["code", "developer", "programmer", "bug", "software", "computer", "tech"],
    "relationships": ["girlfriend", "boyfriend", "wife", "husband", "dating", "love", "couple"],
    "work": ["boss", "work", "office", "meeting", "job", "monday", "friday", "deadline"],
    "gaming": ["game", "gaming", "gamer", "playstation", "xbox", "minecraft", "fortnite"],
    "school": ["school", "teacher", "student", "homework", "exam", "college", "study"],
    "food": ["food", "eat", "hungry", "pizza", "coffee", "lunch", "dinner"],
    "social_media": ["twitter", "instagram", "facebook", "tiktok", "youtube", "reddit"],
    "reactions": ["surprised", "angry", "sad", "happy", "confused", "shocked", "laughing"],
    "general": [],
}

EMOTION_MAP = {
    "surprised": ["surprised", "shocked", "omg", "pikachu", "unexpected"],
    "angry": ["angry", "rage", "furious", "mad", "annoyed"],
    "happy": ["happy", "success", "winner", "celebration", "proud", "great"],
    "sad": ["sad", "crying", "lonely", "disappointed", "heartbreak"],
    "confused": ["confused", "what", "why", "how", "brain", "think"],
    "disgust": ["gross", "disgusting", "eww", "yuck"],
    "neutral": [],
}


def detect_category(name: str) -> str:
    name_lower = name.lower()
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in name_lower for kw in keywords):
            return cat
    return "general"


def detect_emotion(name: str) -> str:
    name_lower = name.lower()
    for emotion, keywords in EMOTION_MAP.items():
        if any(kw in name_lower for kw in keywords):
            return emotion
    return "neutral"


def make_slug(name: str) -> str:
    clean = name.lower().replace(" ", "-")
    clean = "".join(c for c in clean if c.isalnum() or c == "-")
    return clean[:80]


def main():
    logger.info("Fetching Imgflip meme templates...")
    try:
        response = httpx.get(IMGFLIP_URL, timeout=30)
        data = response.json()
        memes_data = data.get("data", {}).get("memes", [])
        logger.info(f"Got {len(memes_data)} memes from Imgflip")
    except Exception as e:
        logger.error(f"Failed to fetch from Imgflip: {e}")
        return

    db = SessionLocal()
    added = 0
    skipped = 0

    for item in memes_data:
        imgflip_id = str(item["id"])
        name = item["name"]
        image_url = item["url"]
        width = item.get("width", 0)
        height = item.get("height", 0)

        slug = make_slug(name)

        # Skip if already exists
        existing = db.query(Meme).filter(Meme.slug == slug).first()
        if existing:
            skipped += 1
            continue

        # Generate unique integer ID
        meme_id = abs(hash(imgflip_id)) % (10**9)

        meme = Meme(
            id=meme_id,
            slug=slug,
            name=name,
            image_url=image_url,
            thumb_url=image_url,  # Will be replaced after thumbnail generation
            format="image",
            category=detect_category(name),
            emotion=detect_emotion(name),
            source="imgflip",
            source_id=imgflip_id,
            width=width,
            height=height,
            is_nsfw=False,
            usage_count=0,
            keywords=[name],
            explanation=f"Popular meme template: {name}",
        )

        try:
            db.add(meme)
            db.flush()
            added += 1
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to add {name}: {e}")

    db.commit()
    db.close()
    logger.info(f"✅ Done! Added: {added} | Skipped (already existed): {skipped}")


if __name__ == "__main__":
    main()
