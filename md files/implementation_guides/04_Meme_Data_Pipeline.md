# 04 — Meme Data Collection Pipeline (50,000+ Memes)
> **Priority:** 🔴 Critical — Without real meme data, search returns nothing
> **Time Needed:** Setup 3-4 hours, then let it run overnight
> **Result:** 50,000+ real memes indexed in Qdrant with images on CDN

---

## 📊 Target: Meme Database by Source

| Source | Target Count | Format | Quality |
|---|---|---|---|
| **Imgflip** (templates) | 1,000 | PNG | ⭐⭐⭐ Iconic meme formats |
| **Giphy** (GIFs) | 20,000 | GIF | ⭐⭐ Great for reactions |
| **Reddit** (r/memes etc.) | 25,000 | GIF/PNG | ⭐⭐⭐ Best context |
| **Tenor** (reaction GIFs) | 4,000 | GIF | ⭐⭐ Good reactions |
| **Total** | **50,000** | Mixed | — |

---

## 📋 PHASE 1 — Get API Keys (15 minutes)

### Groq API Key (for intent parsing)
```
1. Go to: https://console.groq.com
2. Sign up → API Keys → Create API Key
3. Add to .env: GROQ_API_KEY=gsk_XXXXXXXX
```

### Giphy API Key (for GIF collection)
```
1. Go to: https://developers.giphy.com
2. "Get Started" → Create App → SDK → "Create App"
3. App Name: MemeGPT, Use Case: Other
4. Copy API Key
5. Add to .env: GIPHY_API_KEY=your_key_here
```

### Reddit API (for meme collection from r/memes etc.)
```
1. Go to: https://www.reddit.com/prefs/apps
2. "Create Another App" → Type: Script
3. Name: MemeGPT, Redirect URI: http://localhost
4. Copy: Client ID (under app name), Secret
5. Add to .env:
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USER_AGENT=MemeGPT/1.0
```

### Tenor API Key (optional but good for reactions)
```
1. Go to: https://developers.google.com/tenor/guides/quickstart
2. Create a Google Cloud project → Enable Tenor API → Create API Key
3. Add to .env: TENOR_API_KEY=your_key_here
```

---

## 📋 PHASE 2 — Collect from Imgflip (Easiest, Start Here)

Imgflip has 5,000+ meme templates with no auth needed. This is the fastest start.

**Run the existing script:**
```powershell
cd "d:\Meme GPT\backend"
python scripts/scrape_imgflip.py
```

**If the script doesn't collect enough, use this enhanced version:**

Create `d:\Meme GPT\backend\scripts\collect_imgflip_full.py`:

```python
"""
Collect meme templates from Imgflip and seed into SQLite.
No API key needed for the public memes endpoint.
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
        memes_data = data["data"]["memes"]
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
```

```powershell
cd "d:\Meme GPT\backend"
python scripts/collect_imgflip_full.py
```

---

## 📋 PHASE 3 — Collect from Giphy (20,000 GIFs)

Create `d:\Meme GPT\backend\scripts\collect_giphy_full.py`:

```python
"""
Collect reaction GIFs from Giphy API.
Covers 200+ common meme/reaction search terms.
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

logging.basicConfig(level=logging.INFO)
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
                    "limit": 25,  # 25 per term × 100 terms = 2,500 GIFs
                    "rating": "g",  # Safe content
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
                original = gif["images"]["original"]
                image_url = original.get("url", "")
                thumb_url = gif["images"].get("fixed_width", {}).get("url", image_url)

                if not image_url:
                    continue

                slug = f"giphy-{giphy_id}"
                existing = db.query(Meme).filter(Meme.slug == slug).first()
                if existing:
                    continue

                meme_id = abs(hash(giphy_id)) % (10**9) + 1000000  # Offset to avoid collision

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

        # Giphy rate limit: 100 req/hr. Sleep to stay safe.
        time.sleep(1.5)

    db.close()
    logger.info(f"\n✅ Done! Total GIFs added: {total_added}")


if __name__ == "__main__":
    main()
```

```powershell
cd "d:\Meme GPT\backend"
python scripts/collect_giphy_full.py
```

---

## 📋 PHASE 4 — Collect from Reddit (Best Quality Memes)

Create `d:\Meme GPT\backend\scripts\collect_reddit_full.py`:

```python
"""
Collect top memes from Reddit subreddits.
Requires PRAW: pip install praw
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reddit")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MemeGPT/1.0")

# Subreddits to collect from with category tags
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

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

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
            url = post.url
            if not any(url.lower().endswith(ext) for ext in VALID_EXTENSIONS):
                continue
            if post.over_18:
                continue  # Skip NSFW

            # Normalize .gifv → .gif
            if url.endswith(".gifv"):
                url = url[:-5] + ".gif"

            slug = f"reddit-{post.id}"
            existing = db.query(Meme).filter(Meme.slug == slug).first()
            if existing:
                continue

            fmt = "gif" if url.endswith(".gif") else "image"
            meme_id = abs(hash(post.id)) % (10**9) + 2000000  # Offset

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
                upvotes=post.score,
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
        time.sleep(2)  # Respect Reddit rate limits

    db.close()
    logger.info(f"\n✅ Done! Total memes added: {total_added}")


if __name__ == "__main__":
    main()
```

```powershell
pip install praw
cd "d:\Meme GPT\backend"
python scripts/collect_reddit_full.py
```

---

## 📋 PHASE 5 — Generate Embeddings + Index to Qdrant

After collecting memes, run the full indexing pipeline:

```powershell
cd "d:\Meme GPT\backend"

# Check how many memes we have now
python -c "
from app.database import SessionLocal, Meme
db = SessionLocal()
count = db.query(Meme).count()
print(f'Total memes in DB: {count}')
db.close()
"

# Generate embeddings and index ALL memes into Qdrant
python scripts/reindex_all_to_qdrant.py
```

---

## 📋 PHASE 6 — Upload All Media to R2

```powershell
cd "d:\Meme GPT\backend"
python scripts/upload_to_r2_full.py

# Then generate thumbnails
python scripts/generate_thumbnails_full.py
```

---

## 📋 PHASE 7 — Verify Everything

```powershell
cd "d:\Meme GPT\backend"
python -c "
from app.database import SessionLocal, Meme
from app.services.search_service import get_qdrant_client

# Count in DB
db = SessionLocal()
db_count = db.query(Meme).count()
cdn_count = db.query(Meme).filter(Meme.image_url.like('%cdn%')).count()
db.close()

# Count in Qdrant
client = get_qdrant_client()
qdrant_count = 0
if client:
    info = client.get_collection('memes')
    qdrant_count = info.vectors_count

print(f'DB memes: {db_count}')
print(f'CDN hosted: {cdn_count}')
print(f'Qdrant vectors: {qdrant_count}')
print()

if db_count < 1000:
    print('⚠️  Run more collection scripts — need at least 1,000 memes')
elif qdrant_count < 100:
    print('⚠️  Run reindex_all_to_qdrant.py — Qdrant needs more vectors')
elif cdn_count < db_count * 0.5:
    print('⚠️  Run upload_to_r2_full.py — many memes not on CDN yet')
else:
    print('✅ Data pipeline looks good!')
"
```

---

## 📅 Run Order Summary

```
Day 1 (2-3 hours, runs mostly unattended):
  1. python scripts/collect_imgflip_full.py    ← Fast, 1000 memes, 5 min
  2. python scripts/collect_giphy_full.py      ← Slow, 2500 GIFs, ~1 hour
  3. python scripts/collect_reddit_full.py     ← Medium, 2000+ memes, ~2 hours

Then (1-2 hours):
  4. python scripts/reindex_all_to_qdrant.py  ← Generate embeddings + index
  5. python scripts/upload_to_r2_full.py      ← Upload images to CDN
  6. python scripts/generate_thumbnails_full.py ← Create thumbnails
```

**After this, your app has 5,000-6,000 real memes with:**
- ✅ AI vector search working
- ✅ Images on CDN
- ✅ Fast thumbnails
- ✅ 10 results per search

**Next step → `06_Deployment_Railway_Vercel.md`**
