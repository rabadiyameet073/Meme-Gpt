# MemeGPT — Multi-Format Support

> **Document Version:** 1.0 · **Last Updated:** 2026-08-01

---

## Format Support

| Format | Extension | Use Case | Size (avg) |
|---|---|---|---|
| **GIF** | .gif | WhatsApp, Discord, Slack | 1–5MB |
| **PNG/JPG** | .png/.jpg | Instagram, email, blog | 50–500KB |
| **MP4** | .mp4 | TikTok, Reels, YouTube Shorts | 2–10MB |
| **WebP** | .webp | Telegram stickers, web | 30–200KB |
| **Thumbnail** | .webp | Search results preview | 10–50KB |

## Platform Recommendation
When a user selects a format, show a helpful tip:
- **GIF** → "Best for WhatsApp, Discord, Slack"
- **Image** → "Best for Instagram, email, blog"
- **Video** → "Best for TikTok, Reels, YouTube Shorts"
- **WebP** → "Best for Telegram stickers, web"

---

# MemeGPT — Trending Memes

Hourly-updated trending section based on search volume, downloads, and recency.

### Categories
`All` · `Work` · `Gaming` · `Relationships` · `Tech` · `Sports` · `TV/Movies` · `Wholesome`

### Trending Algorithm
```python
trending_score = (
    downloads_24h * 3.0 +
    copies_24h * 2.0 +
    searches_24h * 1.0 +
    recency_bonus * 0.5
) / time_decay_factor
```

---

# MemeGPT — Favorites & Collections

Users save memes to a personal library organized into collections.

### Storage
- **Anonymous users:** localStorage (device-local)
- **Authenticated users:** Supabase (synced)

### Default Collections
- ⭐ Favorites (auto-created)
- 🕐 Recent (last 20 viewed)
- Custom collections (user-created)

---

# MemeGPT — Copy & Download

### Copy to Clipboard
- Uses `navigator.clipboard.write()` with `ClipboardItem`
- Copies actual image data (not URL)
- Works in Chrome, Edge, Safari 14+
- Fallback: copy share URL for unsupported browsers

### Download
- Direct CDN link download via `<a download>` attribute
- Filename: `{meme-slug}.{format}` (e.g., `this-is-fine.gif`)
- No redirect, no popup

---

# MemeGPT — Chat Refinement

Multi-turn conversational search where users refine results.

```
Turn 1: "Monday morning feeling" → [5 results]
Turn 2: "Something more sarcastic" → [5 refined results]
Turn 3: "Show me GIF versions" → [format switch]
Turn 4: "Download the second one" → [triggers download]
```

### Implementation
- Maintain conversation context (last 5 turns)
- Each turn modifies the search embedding
- LLM extracts refinement intent (filter, format, emotion shift)

---

# MemeGPT — SEO Pages

Individual meme pages for search engine indexing.

### URL Pattern
`https://memegpt.com/meme/{slug}`

### Page Content
- High-res meme image with alt text
- Meme name and description
- Origin story and usage context
- Download buttons (all formats)
- Related memes carousel
- Schema.org structured data

### Target: 10,000+ indexed pages
Each page targets long-tail keywords:
- "this is fine meme download"
- "drake pointing meme gif"

---

> **Related Documents:**
> - [Smart_Meme_Search.md](./Smart_Meme_Search.md) · [07_APIs/Meme_API.md](../07_APIs/Meme_API.md)
