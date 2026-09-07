# 02 — Meme Database Population Guide
> Populate the database from <1000 memes to 5,000+ using existing scripts.

---

## Problem Statement

The database file `backend/memegpt.db` is ~350KB with likely fewer than 1,000 memes. The spec requires 5,000+ memes from Imgflip, Reddit, Giphy, and Tenor. All the collection scripts already exist — they just need to be run in order.

---

## Prerequisites

- Python 3.11+ with `backend/requirements.txt` installed
- `.env` file with at minimum: `GROQ_API_KEY`, `GIPHY_API_KEY`
- Optional: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` for Reddit scraping

---

## Step 1: Verify Environment

```powershell
cd "d:\Meme GPT"
python scripts/check_env.py
```

If any keys are missing, add them to `.env`:
```env
GROQ_API_KEY=gsk_your_key_here
GIPHY_API_KEY=your_giphy_key_here
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=MemeGPT/1.0
```

---

## Step 2: Run the Huge Dataset Builder

This is the most important script — it collects memes from multiple sources:

```powershell
cd "d:\Meme GPT"
python scripts/build_huge_dataset.py
```

**What this does (22KB script):**
1. Scrapes top 100 meme templates from Imgflip API (free, no key needed)
2. Fetches popular memes from Reddit JSON API
3. Fetches GIFs from Giphy API
4. Generates metadata (emotions, keywords, categories) via Groq LLM
5. Saves to `data/raw/memes_master.json`

**Expected output:** 2,000–5,000 memes collected

---

## Step 3: Run Individual Collectors for More Data

### 3.1 Imgflip Full Collection (300+ templates)

```powershell
cd "d:\Meme GPT\backend"
python scripts/collect_imgflip_full.py
```

### 3.2 Imgflip Web Scraping (1000+ additional)

```powershell
cd "d:\Meme GPT\backend"
python scripts/scrape_imgflip.py
```

### 3.3 Giphy Full Collection (500+ GIFs)

```powershell
cd "d:\Meme GPT\backend"
python scripts/collect_giphy_full.py
```

### 3.4 Reddit Collection (1000+ from r/memes, r/dankmemes)

```powershell
cd "d:\Meme GPT\backend"
python scripts/collect_reddit_full.py
```

---

## Step 4: Preprocess All Memes

Run the preprocessing script to generate rich text descriptions for each meme:

```powershell
cd "d:\Meme GPT"
python scripts/preprocess_memes.py
```

**This generates for each meme:**
- Rich text description combining name + dialogue + emotions + keywords
- Stored in `data/processed/memes_processed.json`

---

## Step 5: Generate Embeddings

```powershell
cd "d:\Meme GPT"
python scripts/generate_embeddings.py
```

**This uses:**
- `all-MiniLM-L6-v2` for text embeddings (384-dim)
- Saves to `data/embeddings/memes_with_embeddings.json`

**Alternative: Use the backend script (more robust):**
```powershell
cd "d:\Meme GPT\backend"
python generate_embeddings.py
```

---

## Step 6: Seed the Database

```powershell
cd "d:\Meme GPT\backend"
python seed.py
```

For extended seeding with more metadata:
```powershell
cd "d:\Meme GPT\backend"
python scripts/seed_extended.py
```

---

## Step 7: Index into Qdrant

If you have Qdrant configured (QDRANT_URL in .env):

```powershell
cd "d:\Meme GPT"
python scripts/index_qdrant.py
```

For full re-indexing:
```powershell
cd "d:\Meme GPT\backend"
python scripts/reindex_all_to_qdrant.py
```

---

## Step 8: Verify

### 8.1 Check database count

```powershell
cd "d:\Meme GPT\backend"
python -c "
from app.database import SessionLocal, Meme
db = SessionLocal()
count = db.query(Meme).count()
print(f'Total memes in database: {count}')
db.close()
"
```

**Target:** 5,000+ memes

### 8.2 Verify Qdrant index

```powershell
cd "d:\Meme GPT"
python scripts/verify_index.py
```

### 8.3 Test a search

```powershell
cd "d:\Meme GPT\backend"
python -c "
import asyncio
from app.services.recommendation_service import recommend
result = asyncio.run(recommend('when the code finally works'))
print(f'Results: {len(result.get(\"results\", []))}')
for r in result.get('results', [])[:3]:
    print(f'  - {r.get(\"name\", \"?\")} ({r.get(\"score\", 0):.2f})')
"
```

---

## Step 9: Upload Media to Cloudflare R2

If R2 is configured in `.env`:

```powershell
cd "d:\Meme GPT"
python scripts/upload_to_r2.py
```

For full upload with thumbnails:
```powershell
cd "d:\Meme GPT\backend"
python scripts/upload_to_r2_full.py
```

Then verify CDN URLs:
```powershell
cd "d:\Meme GPT"
python scripts/verify_cdn_urls.py
```

---

## Adding More Memes Later

### Manual addition via API

```bash
curl -X POST http://localhost:8000/api/v1/admin/memes \
  -H "X-API-Key: memegpt_admin_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Distracted Boyfriend",
    "categories": ["relationships", "humor"],
    "emotions": ["surprise", "guilt"],
    "image_url": "https://cdn.memegpt.com/images/distracted-boyfriend.jpg",
    "gif_url": "https://cdn.memegpt.com/gifs/distracted-boyfriend.gif"
  }'
```

### Automated nightly collection (GitHub Actions)

The workflow at `.github/workflows/cron.yml` can be configured to run nightly:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily
```

---

## Verification Checklist

- [ ] `data/raw/memes_master.json` has 5,000+ entries
- [ ] `data/processed/memes_processed.json` exists
- [ ] `data/embeddings/` has embedding files
- [ ] Database query returns 5,000+ memes
- [ ] Qdrant collection has matching vector count (if configured)
- [ ] Search returns relevant results for test queries
- [ ] R2 CDN URLs are accessible (if configured)
