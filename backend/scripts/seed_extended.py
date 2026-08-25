#!/usr/bin/env python3
"""
MemeGPT — Extended Meme Seed (Hand-curated with emotions & context).
Supplements the Imgflip scraper with high-quality metadata.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

EXTENDED_MEMES = [
    {
        "id": "ext-001",
        "name": "Drake Pointing Meme",
        "slug": "drake-pointing",
        "categories": ["comparison", "reaction", "choice"],
        "emotions": ["approval", "disapproval"],
        "dialogue": "No [image of something bad] / Yes [image of something preferred]",
        "explanation": "Use when comparing two things where you clearly prefer one over the other. Perfect for coding preferences, lifestyle choices, or any decision.",
        "keywords": ["drake", "pointing", "choice", "prefer", "vs", "comparison"],
        "image_url": "https://i.imgflip.com/30b1gx.jpg",
        "source": "imgflip",
        "popularity_score": 0.98,
    },
    {
        "id": "ext-002",
        "name": "Distracted Boyfriend",
        "slug": "distracted-boyfriend",
        "categories": ["relationships", "temptation", "comparison"],
        "emotions": ["temptation", "betrayal", "desire"],
        "dialogue": "Boyfriend looking at another woman while his girlfriend looks on disapprovingly",
        "explanation": "Use when you're distracted by something new when you should focus on something else. Great for productivity humor, new tech vs old tech.",
        "keywords": ["distracted", "boyfriend", "girlfriend", "temptation", "new", "shiny"],
        "image_url": "https://i.imgflip.com/1ur9b0.jpg",
        "source": "imgflip",
        "popularity_score": 0.97,
    },
    {
        "id": "ext-003",
        "name": "Surprised Pikachu",
        "slug": "surprised-pikachu",
        "categories": ["gaming", "reaction", "surprise"],
        "emotions": ["surprise", "shock", "irony"],
        "dialogue": "[Does something obviously problematic] *surprised pikachu face*",
        "explanation": "Use when someone is shocked by an obvious consequence of their own actions. Perfect for ironic or self-aware situations.",
        "keywords": ["pikachu", "surprised", "shocked", "obvious", "consequence"],
        "image_url": "https://i.imgflip.com/3ocgt8.jpg",
        "source": "imgflip",
        "popularity_score": 0.96,
    },
    {
        "id": "ext-004",
        "name": "This Is Fine",
        "slug": "this-is-fine",
        "categories": ["stress", "work", "chaos", "denial"],
        "emotions": ["denial", "calm", "anxiety"],
        "dialogue": "Dog sitting in burning room saying 'This is fine'",
        "explanation": "Use when you're in a bad situation but pretending everything is okay. Perfect for Monday mornings, broken code, or any overwhelming scenario.",
        "keywords": ["fine", "burning", "dog", "denial", "chaos", "calm", "okay"],
        "image_url": "https://i.imgflip.com/26am.jpg",
        "source": "imgflip",
        "popularity_score": 0.95,
    },
    {
        "id": "ext-005",
        "name": "Roll Safe Think About It",
        "slug": "roll-safe-think-about-it",
        "categories": ["advice", "smart", "irony"],
        "emotions": ["cleverness", "smugness"],
        "dialogue": "[Questionable smart idea] *points to head*",
        "explanation": "Use when presenting a 'clever' solution that seems smart but is actually flawed or missing the point. Great for ironic advice.",
        "keywords": ["roll safe", "smart", "think", "head", "clever", "loophole"],
        "image_url": "https://i.imgflip.com/1h7in3.jpg",
        "source": "imgflip",
        "popularity_score": 0.88,
    },
    {
        "id": "ext-006",
        "name": "Success Kid",
        "slug": "success-kid",
        "categories": ["achievement", "win", "success"],
        "emotions": ["joy", "pride", "satisfaction"],
        "dialogue": "Kid clenching fist triumphantly",
        "explanation": "Use to celebrate a small victory or achievement. Perfect for when something finally works after many attempts.",
        "keywords": ["success", "win", "achievement", "victory", "finally", "yes"],
        "image_url": "https://i.imgflip.com/1bhk.jpg",
        "source": "imgflip",
        "popularity_score": 0.87,
    },
    {
        "id": "ext-007",
        "name": "Woman Yelling at Cat",
        "slug": "woman-yelling-at-cat",
        "categories": ["reaction", "argument", "comparison"],
        "emotions": ["anger", "confusion", "defiance"],
        "dialogue": "[Angry accusation] / [Cat looking confused and unbothered]",
        "explanation": "Use when someone is dramatically overreacting while the other party is calmly unbothered. Great for any absurd argument.",
        "keywords": ["woman", "yelling", "cat", "argument", "reaction", "unbothered"],
        "image_url": "https://i.imgflip.com/345v97.jpg",
        "source": "imgflip",
        "popularity_score": 0.94,
    },
    {
        "id": "ext-008",
        "name": "Expanding Brain",
        "slug": "expanding-brain",
        "categories": ["irony", "comparison", "intelligence"],
        "emotions": ["irony", "cleverness", "absurdity"],
        "dialogue": "Small brain → Medium brain → Large brain → Galaxy brain",
        "explanation": "Use to show a progression from normal thinking to increasingly absurd 'big brain' ideas. Great for ironic intellectual escalation.",
        "keywords": ["brain", "expanding", "big brain", "galaxy", "smart", "ideas"],
        "image_url": "https://i.imgflip.com/1jwhww.jpg",
        "source": "imgflip",
        "popularity_score": 0.91,
    },
]


def seed_extended():
    from app.database import SessionLocal, Meme

    db = SessionLocal()
    added = 0
    updated = 0
    try:
        for data in EXTENDED_MEMES:
            existing = db.query(Meme).filter((Meme.slug == data["slug"]) | (Meme.id == data["id"])).first()
            if existing:
                existing.categories = data["categories"]
                existing.emotions = data["emotions"]
                existing.explanation = data["explanation"]
                existing.keywords = data["keywords"]
                existing.popularity_score = data.get("popularity_score", 0.8)
                if data.get("image_url"):
                    existing.image_url = data["image_url"]
                    existing.image_ref = data["image_url"]
                updated += 1
            else:
                meme_data = {k: v for k, v in data.items() if k in Meme.__table__.columns.keys()}
                meme_data["image_ref"] = data.get("image_url")
                meme = Meme(**meme_data)
                db.add(meme)
                added += 1

        db.commit()
        print(f"[OK] Extended seed: {added} new memes, {updated} updated")
    finally:
        db.close()


if __name__ == "__main__":
    seed_extended()
