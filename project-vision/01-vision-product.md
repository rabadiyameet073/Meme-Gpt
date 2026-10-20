# 01 — Vision & Product

## 1.1 One-liner
**MemeGPT: "Say anything. Get the perfect meme."** Free-text life situation → best meme (GIF/PNG/MP4/WebP) in <1.5s, free, anonymous, no account required.

## 1.2 Problem (legacy: Business_Problem.md)
1. **Discovery pain:** users feel a moment, know a meme exists, but spend 2–10 min hunting (camera rolls hoard 50–200 unsorted memes).
2. **Keyword gap:** Giphy/Tenor keyword search ≈20% relevance — misses context, sarcasm-vs-sincerity, and multi-sentence situations.
3. **Format fragmentation:** WhatsApp wants GIF, Instagram PNG, Discord WebP/sticker, TikTok/Reels MP4 — no single source serves all four + thumbnails.
4. **No conversation search:** pasting a chat log or email thread returns nothing useful anywhere else.

## 1.3 Solution (legacy: Business_Solution.md)
- **Semantic understanding:** MiniLM 384d embeddings + Groq `llama-3.1-8b-instant` intent JSON + DistilRoBERTa emotion → Qdrant cosine + composite rerank → ~85% relevance (vs ~20% keyword).
- **Emotion-aware ranking:** 7-class emotion detection adds +15% primary / +8% secondary boosts.
- **Every format, one record:** each meme carries `image_url / gif_url / mp4_url / webp_url / thumb_url` + per-format platform tip in UI.
- **Conversation mode:** LLM splits pasted threads into ≤3 labeled contexts, each searched independently.
- **Library:** favorites + custom collections + recent-20 + offline-50 (mobile) with anonymous session IDs (no login needed for MVP).
- **Moats:** feedback flywheel (copy/download/share/vote weights feed popularity), 8-layer index (Reddit + OCR + BLIP + CLIP + LLM tags + meta + text + image vectors), $0 infra, 10k+ programmatic SEO pages.

## 1.4 Users (legacy: User_Personas.md / Stakeholders.md)
| Persona | Profile | Usage | Value / plan |
|---|---|---|---|
| Mike (primary) | 18–28 student, mobile 70% | 5–10 memes/day, WhatsApp-ready in seconds | Volume + virality, $0 |
| Dave (secondary) | 22–35 dev, Slack desktop 80% | 3–5/day, tech memes, hates ad-heavy Giphy | API usage, $9 dev tier |
| Chloe (tertiary) | 20–30 creator, desktop 60% | 10+/day, HQ PNG/MP4, trending hunter | Revenue + UGC, $9 |
| Marketers / mods | Brand-safe reactions, 5-sec responses | Campaign + community | $15 team (future) |
| Developers | REST API, <30 min integration, 100 req/day free | Bots, Discord/Telegram | API growth loop |

## 1.5 Scope
**P0 (ship):** AI search, emotion detection, responsive web, multiformat output, clipboard copy, direct download, trending, suggestion chips, feedback voting, SEO meme pages.
**P1 (next):** user accounts, API keys + tiers, content moderation queue, analytics dashboard.
**P2 (later):** multi-turn chat refinement, collections sync, Expo app parity, reverse image search, i18n (ES/PT/HI first — intent parser already multilingual).
**Explicitly out:** meme generator/editor, video editing, social feed/comments, public uploads, payments (until P4), white-label, browser extension.

## 1.6 Product flows (legacy: Product_Workflow.md)
- **F1 Basic:** open → type/paste (≤2000 chars, `Ctrl/Cmd+Enter`) → `POST /api/v1/search` → top-5 <1.5s with % confidence → preview modal → copy-paste or download-picker → toast.
- **F2 Conversation:** paste thread → LLM returns 2–3 labeled contexts (e.g. "exam panic / fear", "defeat / resignation") → each section shows its own top memes.
- **F3 Download:** format picker (GIF 1–5MB chat loops · PNG 50–500KB crisp · MP4 2–10MB 10× smaller · WebP 30–200KB) → 307 redirect to R2/CDN → toast + `download` counter.
- **F4 Chat refinement:** "more sarcastic" / "like #1 but GIF" → session history re-ranks without retyping.
- **F5 Trending:** hourly cron score `(downloads×3 + copies×2 + searches×1 + recency×0.5) / decay`; badges Hot ≥0.8 / Rising / Steady; category chips All/Work/Gaming/Relationships/Tech/Sports.
- **F6 Library:** star → favorites (200 cap, localStorage → Supabase sync P1); collections + ZIP export + search within saved.
- **Shortcuts:** `⌘/Ctrl+Enter` search · `/` focus · `C/D/S/F` copy/download/share/favorite · `1–6` tabs; mobile: swipe cards, long-press preview, double-tap vote.

## 1.7 Targets (legacy: Goals.md)
| Metric | Target | Measured by |
|---|---|---|
| Relevance (thumbs-up) | >75% | `POST /feedback` CTR |
| Precision@5 / MRR | >0.70 / >0.80 | `evaluate.py` weekly labeled set |
| Zero-result rate | <5% | search logs (`result_count=0`) |
| Latency P50 / P95 | ~560ms / <1.5s (cached ~15ms) | `response_time_ms` histogram |
| DAU | 1k M3 → 10k M6 → 50k Y1 | Umami/analytics |
| Retention D7 / NPS | >30–50% / >30–60 | cohort + survey |
| Copy/download rate | >50% of searches | feedback weights |
| Uptime | 99.5% | UptimeRobot + Sentry |

## 1.8 Anti-goals (what we will NOT do)
- No dark-pattern growth (no fake urgency, no spam invites, no forced signup walls).
- No quality-for-quantity trades (a 500-meme accurate index beats a 50k noisy one).
- No paid infra before 10k DAU sustained for 2 weeks (free-tier discipline).
- No PII collection to "improve recommendations" (anonymous session IDs only).
- No shipping without the §README definition of done (tests + smoke + docs).

## 1.9 KPI dashboard spec (what `/stats` + Umami must show)
Panels: searches/day · P50/P95 latency · cache-hit % · copy/download/share counts · thumbs-up % · zero-result % · top-20 queries (hashed) · DAU/WAU · D7 retention · error rate by endpoint. Alerts: P95>3s for 15 min · error rate>2% · Qdrant points drop · R2 4xx spike.
