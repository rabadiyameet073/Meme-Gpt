# 09 — SEO & Marketing Completion Guide
> Complete category pages, auto-generated blog, Google Search Console, and App Store Optimization.

---

## Problem Statement

| Feature | Status | Gap |
|---------|--------|-----|
| Root SEO metadata | ✅ | — |
| Dynamic sitemap | ✅ | — |
| Individual meme pages | 🟡 | Skeleton → Fixed in Guide 07 |
| Meme category pages (`/memes/work-memes`) | ❌ | Created in Guide 07, need indexing |
| Auto-generated blog | 🟡 | Structure built in Guide 07, need content |
| Google Search Console | ❌ | Need verification |
| Core Web Vitals | 🟡 | Need measurement |
| iOS App Store listing (ASO) | ❌ | Need submission |
| Google Play Store listing | ❌ | Need submission |

---

## Step 1: Submit Sitemap to Google Search Console

### 1.1 Verify Domain

1. Go to [Google Search Console](https://search.google.com/search-console/)
2. Add property → `https://memegpt.com`
3. Verify via DNS TXT record:
   - Type: `TXT`
   - Name: `@`
   - Value: `google-site-verification=YOUR_TOKEN`

### 1.2 Submit Sitemap

After verification:
1. Go to Sitemaps → Add new sitemap
2. Enter: `https://memegpt.com/sitemap.xml`
3. Submit

### 1.3 Add Verification to `layout.tsx`

**Modify:** `apps/web/app/layout.tsx`

Add to the metadata export:
```typescript
export const metadata: Metadata = {
  // ... existing metadata ...
  verification: {
    google: 'YOUR_GOOGLE_VERIFICATION_TOKEN',
  },
};
```

---

## Step 2: Optimize Core Web Vitals

### 2.1 Next.js Image Optimization

Replace all `<img>` tags in `apps/web/` with `next/image`:

```tsx
import Image from 'next/image';

// Instead of:
<img src={meme.image_url} alt={meme.name} />

// Use:
<Image
  src={meme.image_url}
  alt={meme.name}
  width={600}
  height={400}
  placeholder="blur"
  blurDataURL="data:image/png;base64,iVBORw0KGgo..."
  loading="lazy"
/>
```

### 2.2 Configure Image Domains

**Modify:** `apps/web/next.config.mjs`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.memegpt.com' },
      { protocol: 'https', hostname: '*.r2.dev' },
      { protocol: 'https', hostname: 'i.imgflip.com' },
      { protocol: 'https', hostname: 'media.giphy.com' },
    ],
  },
};

export default nextConfig;
```

### 2.3 Add Font Preloading

Already done in `layout.tsx` with `next/font/google` and `display: 'swap'`.

### 2.4 Measure CWV

```powershell
npx lighthouse https://memegpt.com --output html --output-path ./cwv-report.html
```

Targets:
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

---

## Step 3: Generate Blog Content

Create a script to auto-generate SEO-optimized blog posts using Groq:

**File (create new):** `scripts/generate_blog_posts.py`

```python
"""Generate SEO blog posts about meme culture using Groq LLM."""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.config import GROQ_API_KEY

BLOG_TOPICS = [
    {"slug": "how-ai-finds-perfect-meme", "title": "How AI Finds the Perfect Meme for Any Situation", "keywords": "AI meme finder, meme recommendation, vector search"},
    {"slug": "top-50-work-memes-2026", "title": "Top 50 Work Memes of 2026", "keywords": "work memes, office memes, funny work memes"},
    {"slug": "meme-formats-explained", "title": "GIF vs PNG vs MP4: Which Meme Format Should You Use?", "keywords": "meme format, download meme, gif vs png"},
    {"slug": "meme-history-evolution", "title": "The Evolution of Internet Memes: 2000 to 2026", "keywords": "meme history, internet culture, meme evolution"},
    {"slug": "best-reaction-memes", "title": "100 Best Reaction Memes for Every Emotion", "keywords": "reaction memes, funny reactions, meme reactions"},
]

OUTPUT_DIR = Path(__file__).parent.parent / "apps" / "web" / "content" / "blog"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_post(topic: dict) -> str:
    """Generate a blog post using Groq."""
    import httpx

    prompt = f"""Write a 1500-word SEO-optimized blog post about:
Title: {topic['title']}
Target keywords: {topic['keywords']}

Requirements:
- Include an engaging introduction
- Use H2 and H3 headings
- Include practical examples and tips
- End with a call-to-action to try MemeGPT
- Write in a casual, fun tone appropriate for meme culture
- Include relevant emojis
- Return as Markdown

Write the full post now:"""

    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3000,
            "temperature": 0.7,
        },
        timeout=30,
    )
    return resp.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    for topic in BLOG_TOPICS:
        print(f"Generating: {topic['title']}...")
        content = generate_post(topic)

        frontmatter = f"""---
title: "{topic['title']}"
slug: "{topic['slug']}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
keywords: "{topic['keywords']}"
description: "{topic['title']} — MemeGPT Blog"
---

"""
        output_file = OUTPUT_DIR / f"{topic['slug']}.md"
        output_file.write_text(frontmatter + content, encoding="utf-8")
        print(f"  ✅ Saved to {output_file}")
```

Run it:
```powershell
cd "d:\Meme GPT"
python scripts/generate_blog_posts.py
```

---

## Step 4: App Store Optimization (ASO)

### 4.1 Google Play Store Listing

Prepare these assets:
- **App Name:** MemeGPT — AI Meme Finder
- **Short Description (80 chars):** Find the perfect meme for any situation. AI-powered. Free.
- **Full Description (4000 chars):** Write a keyword-rich description
- **Screenshots:** 6-8 phone screenshots of the app
- **Feature Graphic:** 1024×500 banner
- **Categories:** Entertainment, Social

### 4.2 Apple App Store Listing

- **App Name:** MemeGPT — AI Meme Finder
- **Subtitle:** Perfect memes in seconds
- **Keywords (100 chars):** meme,ai,funny,gif,download,reaction,search,meme finder,meme app
- **Screenshots:** 6.5" and 5.5" iPhone screenshots
- **App Preview Video:** 30-second screen recording

---

## Verification Checklist

- [ ] Google Search Console verified and sitemap submitted
- [ ] `next/image` used for all images in `apps/web`
- [ ] Lighthouse CWV scores: LCP < 2.5s, FID < 100ms, CLS < 0.1
- [ ] Blog posts generated and accessible at `/blog/[slug]`
- [ ] Category pages indexed by Google (check Search Console)
- [ ] Google Play Store listing prepared
- [ ] Apple App Store listing prepared
