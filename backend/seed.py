import json
import random
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Meme, MemeUsage, MemeVote, SearchLog, SessionLocal, init_db
from data.meme_dataset import MEME_DATASET


def seed(reset: bool = False):
    """Seed the database with memes.

    By default (DB-07), this is non-destructive (upsert-only): it initializes tables
    without dropping existing data, updates existing memes by slug, and preserves users
    and API keys. If reset=True (--reset CLI flag), tables are cleared first.
    """
    init_db(drop_all=reset)
    db = SessionLocal()
    try:
        if reset:
            db.query(MemeVote).delete()
            db.query(MemeUsage).delete()
            db.query(SearchLog).delete()
            db.query(Meme).delete()
            db.commit()

        inserted = 0
        updated = 0

        for item in MEME_DATASET:
            name = item["name"]
            slug = item.get("slug") or re.sub(r"[^a-z0-9\s-]", "", str(name).lower()).strip().replace(" ", "-")[:180]

            existing = db.query(Meme).filter(Meme.slug == slug).first()
            if existing:
                existing.name = name
                existing.categories = item.get("categories") or [item["category"]]
                existing.emotions = item.get("emotions") or []
                existing.category = item["category"]
                existing.dialogue = item["dialogue"]
                existing.explanation = item["explanation"]
                existing.keywords = json.dumps(item["keywords"]) if isinstance(item.get("keywords"), list) else item.get("keywords", "[]")
                existing.image_url = item.get("image_url") or item.get("image")
                existing.gif_url = item.get("gif_url") or item.get("gif")
                existing.mp4_url = item.get("mp4_url") or item.get("video")
                existing.thumb_url = item.get("thumb_url")
                existing.webp_url = item.get("webp_url")
                existing.image_ref = item.get("image")
                existing.video_ref = item.get("video")
                existing.gif_ref = item.get("gif")
                existing.alt_text = item.get("alt_text")
                existing.source = item.get("source", "manual")
                existing.nsfw = item.get("nsfw", False)
                existing.moderation_status = item.get("moderation_status", "approved")
                updated += 1
            else:
                db.add(
                    Meme(
                        id=str(uuid.uuid4()),
                        name=name,
                        slug=slug,
                        categories=item.get("categories") or [item["category"]],
                        emotions=item.get("emotions") or [],
                        category=item["category"],
                        dialogue=item["dialogue"],
                        explanation=item["explanation"],
                        keywords=json.dumps(item["keywords"]) if isinstance(item.get("keywords"), list) else item.get("keywords", "[]"),
                        image_url=item.get("image_url") or item.get("image"),
                        gif_url=item.get("gif_url") or item.get("gif"),
                        mp4_url=item.get("mp4_url") or item.get("video"),
                        thumb_url=item.get("thumb_url"),
                        webp_url=item.get("webp_url"),
                        image_ref=item.get("image"),
                        video_ref=item.get("video"),
                        gif_ref=item.get("gif"),
                        alt_text=item.get("alt_text"),
                        source=item.get("source", "manual"),
                        nsfw=item.get("nsfw", False),
                        moderation_status=item.get("moderation_status", "approved"),
                        viral_score=item.get("viralScore", random.uniform(30, 100)),
                        popularity_score=item.get("popularity") or (item.get("viralScore", 85.0) / 100),
                        usage_count=item.get("usage_count") or random.randint(0, 50),
                        upvotes=random.randint(0, 100),
                        downvotes=random.randint(0, 20),
                    )
                )
                inserted += 1

        db.commit()
        count = db.query(Meme).count()
        with_images = db.query(Meme).filter(Meme.image_url.isnot(None)).count()
        print(f"Seeding completed: {inserted} inserted, {updated} updated (total {count} memes in DB, {with_images} with images).")
    finally:
        db.close()


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed(reset=reset_flag)
