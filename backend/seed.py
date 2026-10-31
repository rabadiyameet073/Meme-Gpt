import json
import random
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Meme, MemeUsage, MemeVote, SearchLog, SessionLocal, init_db
from data.meme_dataset import MEME_DATASET


def seed():
    init_db(drop_all=True)
    db = SessionLocal()
    db.query(MemeVote).delete()
    db.query(MemeUsage).delete()
    db.query(SearchLog).delete()
    db.query(Meme).delete()
    db.commit()

    for item in MEME_DATASET:
        db.add(
            Meme(
                id=str(uuid.uuid4()),
                name=item["name"],
                slug=item.get("slug"),
                categories=item.get("categories") or [item["category"]],
                emotions=item.get("emotions") or [],
                category=item["category"],
                dialogue=item["dialogue"],
                explanation=item["explanation"],
                keywords=json.dumps(item["keywords"]),
                image_url=item.get("image_url") or item.get("image"),
                gif_url=item.get("gif_url") or item.get("gif"),
                mp4_url=item.get("mp4_url") or item.get("video"),
                thumb_url=item.get("thumb_url"),
                webp_url=item.get("webp_url"),
                image_ref=item.get("image"),
                video_ref=item.get("video"),
                gif_ref=item.get("gif"),
                alt_text=item.get("alt_text"),
                source=item.get("source"),
                nsfw=item.get("nsfw", False),
                moderation_status=item.get("moderation_status", "approved"),
                viral_score=item.get("viralScore", random.uniform(30, 100)),
                popularity_score=item.get("popularity") or (item.get("viralScore", 85.0) / 100),
                usage_count=item.get("usage_count") or random.randint(0, 50),
                upvotes=random.randint(0, 100),
                downvotes=random.randint(0, 20),
            )
        )
    db.commit()
    count = db.query(Meme).count()
    with_images = db.query(Meme).filter(Meme.image_url.isnot(None)).count()
    db.close()
    print(f"Seeded {count} memes ({with_images} with image_url).")
    if count != len(MEME_DATASET):
        raise SystemExit(
            f"Seed mismatch: expected {len(MEME_DATASET)} rows, wrote {count}"
        )


if __name__ == "__main__":
    seed()
