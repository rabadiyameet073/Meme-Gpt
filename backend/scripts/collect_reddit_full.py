"""
MemeGPT — Collect top memes from Reddit subreddits.
Requires PRAW: pip install praw
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

from app.database import SessionLocal, Meme

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("reddit")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MemeGPT/1.0")

SUBREDDITS = [
    ("memes", "general", 500),
    ("dankmemes", "general", 500),
    ("ProgrammerHumor", "programming", 300),
    ("me_irl", "relatable", 300),
    ("AdviceAnimals", "reactions", 200),
    ("reactiongifs", "reactions", 300),
    ("wholesomememes", "wholesome", 200),
    ("BlackPeopleTwitter", "social", 200),
    ("terriblefacebookmemes", "absurd", 100),
    ("HistoryMemes", "educational", 100),
    ("gaming", "gaming", 200),
    ("WorkReform", "work", 100),
]

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".gifv"}


def detect_emotion(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["surprised", "shock", "omg", "unexpected", "wait what"]):
        return "surprise"
    if any(w in t for w in ["angry", "hate", "stupid", "wtf", "annoying", "rage"]):
        return "anger"
    if any(w in t for w in ["sad", "cry", "miss", "alone", "depress"]):
        return "sadness"
    if any(w in t for w in ["happy", "great", "awesome", "win", "love", "finally"]):
        return "joy"
    if any(w in t for w in ["confused", "why", "how", "what", "understand"]):
        return "confusion"
    return "neutral"


def main():
    if not REDDIT_CLIENT_ID:
        logger.error("❌ REDDIT_CLIENT_ID not set in .env")
        return

    try:
        import praw
    except ImportError:
        logger.error("❌ Install praw first: pip install praw")
        return

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}")
        return

    db = SessionLocal()
    total_added = 0

    for subreddit_name, category, limit in SUBREDDITS:
        logger.info(f"Collecting from r/{subreddit_name} (limit={limit})...")
        added = 0

        try:
            subreddit = reddit.subreddit(subreddit_name)
            posts = list(subreddit.top(time_filter="all", limit=limit))
        except Exception as e:
            logger.warning(f"Failed r/{subreddit_name}: {e}")
            time.sleep(5)
            continue

        for post in posts:
            url = getattr(post, "url", "")
            if not any(url.lower().endswith(ext) for ext in VALID_EXTENSIONS):
                continue
            if getattr(post, "over_18", False):
                continue

            # Normalize .gifv → .gif
            if url.endswith(".gifv"):
                url = url[:-5] + ".gif"

            slug = f"reddit-{post.id}"
            existing = db.query(Meme).filter(Meme.slug == slug).first()
            if existing:
                continue

            fmt = "gif" if url.endswith(".gif") else "image"
            meme_id = abs(hash(post.id)) % (10**9) + 2000000

            meme = Meme(
                id=meme_id,
                slug=slug,
                name=post.title[:250],
                image_url=url,
                gif_url=url if fmt == "gif" else None,
                thumb_url=url,
                format=fmt,
                category=category,
                emotion=detect_emotion(post.title),
                source="reddit",
                source_id=post.id,
                subreddit=subreddit_name,
                upvotes=getattr(post, "score", 0),
                is_nsfw=False,
                usage_count=0,
                keywords=[subreddit_name, category, fmt],
                explanation=post.title[:500],
            )

            try:
                db.add(meme)
                db.flush()
                added += 1
                total_added += 1
            except Exception as e:
                db.rollback()
                logger.debug(f"Skip post {post.id}: {e}")

        db.commit()
        logger.info(f"  Added {added} from r/{subreddit_name} (total: {total_added})")
        time.sleep(2)

    db.close()
    logger.info(f"\n✅ Done! Total memes added: {total_added}")


if __name__ == "__main__":
    main()
