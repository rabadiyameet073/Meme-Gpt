# 15 — Seed Data Expansion
# Imgflip Scraper, 5000+ Memes, Fix Media URLs

> **Gap Source:** Section 16 of GAP_ANALYSIS_FULL.md  
> **Priority:** P1  
> **Target:** 5,000+ memes with real metadata and media URLs

---

## WHAT IS MISSING

- Unknown meme count in current DB (could be < 100)
- All `image_url`, `gif_url`, `mp4_url` = NULL (no CDN)
- No Imgflip scraper implemented
- No emotion tags on memes
- No Reddit scraper

---

## STEP 1 — Check Current Meme Count

```bash
cd "d:\Meme GPT\backend"
python -c "
from app.database import SessionLocal, Meme
db = SessionLocal()
count = db.query(Meme).count()
print(f'Current meme count: {count}')
db.close()
"
```

---

## STEP 2 — Imgflip Scraper

**Create** `d:\Meme GPT\backend\scripts\scrape_imgflip.py`:

```python
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

    raw_memes = scrape_imgflip()
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

            # Check if already exists
            existing = db.query(Meme).filter(Meme.slug == slug).first()
            if existing:
                skipped += 1
                continue

            explanation = (
                f"Use the {name} meme when you want to express {', '.join(emotions) or 'any emotion'}. "
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
                dialogue="",  # Will be updated manually or by AI
                image_url=image_url,
                image_ref=image_url,  # Use imgflip URL directly
                source="imgflip",
                nsfw=False,
                popularity_score=0.5,
            )
            db.add(meme)
            added += 1

        db.commit()
        logger.info(f"✅ Seeded {added} Imgflip memes ({skipped} skipped — already existed)")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")
    finally:
        db.close()

    return added


if __name__ == "__main__":
    seed_imgflip_memes()
```

---

## STEP 3 — Extended Meme Seed Data (Manual Curated)

**Create** `d:\Meme GPT\backend\scripts\seed_extended.py`:

```python
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
    try:
        for data in EXTENDED_MEMES:
            existing = db.query(Meme).filter(Meme.slug == data["slug"]).first()
            if existing:
                # Update with better metadata
                existing.categories = data["categories"]
                existing.emotions = data["emotions"]
                existing.explanation = data["explanation"]
                existing.keywords = data["keywords"]
                existing.popularity_score = data.get("popularity_score", 0.8)
                if data.get("image_url") and not existing.image_url:
                    existing.image_url = data["image_url"]
                    existing.image_ref = data["image_url"]
            else:
                meme = Meme(**{k: v for k, v in data.items()
                             if k in Meme.__table__.columns.keys()})
                meme.image_ref = data.get("image_url")
                db.add(meme)
                added += 1

        db.commit()
        print(f"✅ Extended seed: {added} new memes, {len(EXTENDED_MEMES)-added} updated")
    finally:
        db.close()


if __name__ == "__main__":
    seed_extended()
```

---

## STEP 4 — Run All Seeders

```bash
cd "d:\Meme GPT\backend"

# 1. Run existing seed.py
python seed.py

# 2. Run Imgflip scraper (adds 100 more memes)
python scripts/scrape_imgflip.py

# 3. Run extended seed (updates metadata)
python scripts/seed_extended.py

# 4. Check count
python -c "
from app.database import SessionLocal, Meme
db = SessionLocal()
print(f'Total memes: {db.query(Meme).count()}')
with_images = db.query(Meme).filter(Meme.image_url.isnot(None)).count()
print(f'With images: {with_images}')
db.close()
"
```

---

## STEP 5 — Verify Memes Have Correct Emotions Format

```bash
python -c "
from app.database import SessionLocal, Meme
db = SessionLocal()
samples = db.query(Meme).limit(5).all()
for m in samples:
    print(f'{m.name}: categories={m.categories} emotions={m.emotions}')
db.close()
"
```

All categories and emotions should be Python lists, not strings.
