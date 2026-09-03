"""
MemeGPT — Collect reaction GIFs from Giphy API.
Covers 100+ common meme/reaction search terms.
Specification: 04_Meme_Data_Pipeline.md
"""
import os
import sys
import time
import hashlib
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", ".env"))

import httpx
from app.database import SessionLocal, Meme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("giphy")

GIPHY_KEY = os.getenv("GIPHY_API_KEY", "")
GIPHY_URL = "https://api.giphy.com/v1/gifs/search"

# 100 high-value search terms for meme reactions
SEARCH_TERMS = [
    "reaction funny", "monday morning", "when you realize", "that moment when",
    "surprised pikachu", "facepalm", "mind blown", "clapping", "thumbs up",
    "thumbs down", "eye roll", "crying laughing", "confused", "shocked",
    "frustrated", "celebration", "winning", "failing", "awkward",
    "deal with it", "not impressed", "bored", "excited", "nervous",
    "thinking", "smug", "disappointed", "proud", "embarrassed",
    "angry", "happy dance", "sad", "disgusted", "scared",
    "typing furiously", "no idea", "fine everything is fine",
    "this is fine", "computer burning", "coffee need coffee",
    "programmer coding", "bug found", "it works", "deploy friday",
    "code review", "meeting could be email", "zoom call", "working from home",
    "monday blues", "friday feeling", "weekend mode", "waiting",
    "loading", "buffering", "done finished", "success kid",
    "galaxy brain", "big brain", "galaxy brain thinking",
    "drake approved", "drake rejected", "two buttons",
    "distracted boyfriend", "woman yelling cat",
    "spongebob mocking", "patrick star", "surprised face",
    "oh no", "uh oh", "here we go again", "not again",
    "same time every year", "season again", "cannot believe",
    "plot twist", "unexpected", "mind blown reaction",
    "okay then", "well then", "moving on",
    "relationship goals", "friendship goals", "coworker annoying",
    "boss calling", "deadline approaching", "project delayed",
    "budget cut", "promoted", "rejected application",
    "social anxiety", "introvert life", "extrovert problems",
    "studying late", "exam tomorrow", "forgot homework",
    "teacher explaining", "student sleeping class",
    "pizza delivery", "food arriving", "hungry waiting",
    "gaming rage quit", "game won", "game lost",
    "loading screen", "respawning", "no more lives",
    "level up", "achievement unlocked",
    "twitter drama", "ratio", "going viral",
    "dark mode", "light mode", "night owl",
    "morning person", "not a morning person",
    "adulting hard", "responsibility", "bills arriving",
    "money gone", "paycheck spent", "broke again",
]


def main():
    if not GIPHY_KEY:
        logger.error("❌ GIPHY_API_KEY not set in .env")
        return

    db = SessionLocal()
    total_added = 0

    for term in SEARCH_TERMS:
        logger.info(f"Fetching: '{term}'")
        try:
            response = httpx.get(
                GIPHY_URL,
                params={
                    "api_key": GIPHY_KEY,
                    "q": term,
                    "limit": 25,
                    "rating": "g",
                    "lang": "en",
                },
                timeout=15
            )
            data = response.json()
            gifs = data.get("data", [])
        except Exception as e:
            logger.warning(f"Failed for '{term}': {e}")
            time.sleep(2)
            continue

        added = 0
        for gif in gifs:
            try:
                giphy_id = gif["id"]
                title = gif.get("title", term) or term
                original = gif.get("images", {}).get("original", {})
                image_url = original.get("url", "")
                thumb_url = gif.get("images", {}).get("fixed_width", {}).get("url", image_url)

                if not image_url:
                    continue

                slug = f"giphy-{giphy_id}"
                existing = db.query(Meme).filter(Meme.slug == slug).first()
                if existing:
                    continue

                meme_id = abs(hash(giphy_id)) % (10**9) + 1000000

                meme = Meme(
                    id=meme_id,
                    slug=slug,
                    name=title[:200],
                    image_url=image_url,
                    gif_url=image_url,
                    thumb_url=thumb_url,
                    format="gif",
                    category="reactions",
                    emotion="neutral",
                    source="giphy",
                    source_id=giphy_id,
                    is_nsfw=False,
                    usage_count=0,
                    keywords=[term, "gif", "reaction"],
                    explanation=f"Reaction GIF: {title}",
                )
                db.add(meme)
                db.flush()
                added += 1
                total_added += 1

            except Exception as e:
                db.rollback()
                logger.debug(f"Skip gif: {e}")

        db.commit()
        logger.info(f"  Added {added} GIFs for '{term}' (total: {total_added})")

        # Giphy rate limit: sleep to stay safe
        time.sleep(1.5)

    db.close()
    logger.info(f"\n✅ Done! Total GIFs added: {total_added}")


if __name__ == "__main__":
    main()
