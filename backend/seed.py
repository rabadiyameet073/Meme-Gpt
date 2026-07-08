import json
import random
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import Meme, MemeUsage, MemeVote, SearchLog, SessionLocal, init_db
from data.meme_dataset import MEME_DATASET


def seed():
    init_db()
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
                category=item["category"],
                dialogue=item["dialogue"],
                explanation=item["explanation"],
                keywords=json.dumps(item["keywords"]),
                video_ref=item.get("video"),
                gif_ref=item.get("gif"),
                viral_score=item.get("viralScore", random.uniform(30, 100)),
                usage_count=random.randint(0, 50),
                upvotes=random.randint(0, 100),
                downvotes=random.randint(0, 20),
            )
        )
    db.commit()
    count = db.query(Meme).count()
    db.close()
    print(f"Seeded {count} memes.")


if __name__ == "__main__":
    seed()
