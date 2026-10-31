# 01 — MemeGPT: Product Vision & Features
> Industry-level specification for a solo developer building an AI-powered meme recommendation engine

---

## Vision

MemeGPT is an AI-powered meme recommendation engine that understands context, emotion, sarcasm, and cultural nuance to suggest the **perfect meme for any moment**. Users input text — a conversation snippet, a sentence, a feeling, a whole script — and MemeGPT returns the most relevant, funniest, most shareable meme across all formats (GIF, PNG, MP4, WebP).

**Core Promise:** Zero effort. Maximum relatability. Instant meme.

---

## Mission

> "Make meme discovery as fast as thinking of one."

- For content creators: stop wasting 20 minutes scrolling Google for the right meme
- For group chats: reply with the perfect reaction in 5 seconds
- For marketers: find culturally resonant memes for campaigns instantly
- For developers (Phase 3): access a meme recommendation API

---

## Platform Overview

### Platform 1 — Web App (`app.memegpt.com`)
A ChatGPT-style chat interface for the browser:
- Text area input (supports paste of long conversations)
- Animated results grid with meme previews
- Copy / Download buttons (GIF, PNG, MP4, WebP, Link)
- Session history (last 20 searches)
- Format toggle: GIF | Image | Video
- "More like this" feedback button on each result
- Dark mode only (matches meme culture)

### Platform 2 — Landing Website (`memegpt.com`)
Marketing + download hub:
- Hero with live interactive demo (no sign-up needed)
- Feature showcase with animated examples
- App Store + Play Store download buttons
- SEO-optimized meme pages (`/meme/drake-pointing`)
- Blog for meme trend content
- Pricing page (future monetization)

### Platform 3 — Mobile App (iOS + Android)
React Native cross-platform app:
- All core web features in a native feel
- Native share sheet (one tap to WhatsApp, Instagram, iMessage, etc.)
- Home screen widget showing "meme of the day"
- Push notifications for trending meme alerts
- Offline cached library (last 50 downloaded memes)
- Target size: **40–60 MB** (well within 40–100 MB goal)

---

## Core Features (Detailed)

---

### Feature 1: Intelligent Meme Recommendation Engine

The heart of the product. User types anything and gets the best meme.

**Inputs accepted:**
| Input Type | Example |
|---|---|
| Single sentence | "I stayed up till 3am fixing one bug" |
| Emotion description | "I feel betrayed by my best friend" |
| Situation description | "My boss emailed at 11pm on a Friday" |
| Pasted conversation | [copy of WhatsApp chat] |
| Movie/show quote | "I am the one who knocks" |
| Lyric / song reference | "this is fine" |
| Meme description | "the one where the lady is screaming at a cat" |

**Output:** Top 3–5 meme cards, ranked by relevance score

**AI Pipeline:**
```
User Input
   ↓
LLM Context Extractor (Groq / Llama 3.1 — free)
   → emotion, situation, tone, keywords, format_hint
   ↓
Text Embedding (MiniLM-L6-v2 — local, free)
   → 384-dimension query vector
   ↓
Vector Search (Qdrant — cosine similarity)
   → top-10 candidate memes
   ↓
Re-ranker (popularity boost + emotion match)
   → top-5 final memes
   ↓
Response with URLs (CDN-served files)
```

**Smart Search Modes (auto-detected):**
1. **Vibe Match** — emotion-heavy inputs → finds memes with matching emotional tone
2. **Situation Match** — scenario descriptions → finds relatable reaction memes
3. **Quote Match** — famous quotes, movie lines → finds memes that reference them
4. **Conversation Match** — pasted chat → understands full context and overall vibe
5. **Template Search** — describes a meme ("the fine dog") → finds exact template

---

### Feature 2: Multi-Format Meme Export

Every meme available in all possible formats:

| Format | Extension | Max Size | Use Case |
|---|---|---|---|
| Animated GIF | `.gif` | 2 MB | WhatsApp, Discord, Slack, Twitter |
| Static Image | `.jpg` / `.png` | 300 KB | iMessage, Reddit, email |
| Video Clip | `.mp4` | 5 MB | Instagram Reels, TikTok, Stories |
| Web-optimized | `.webp` | 100 KB | Websites, web sharing |
| Copy Image | clipboard | — | Paste directly into chat |
| Copy Link | URL | — | Share the MemeGPT page |
| Embed Code | HTML iframe | — | For developers / blogs |

**Format auto-selection logic:**
- User sets preference (GIF / Image / Video) — remembered per device
- If preferred format not available for a meme, next best format is shown
- GIF is default (most universally shareable)

---

### Feature 3: Chat Interface (Multi-Turn)

Users can refine results in a conversational way:

```
User:   "I just submitted my project at 11:59pm"
MemeGPT: [Shows 5 memes — stressed + relief themed]

User:   "Give me something more triumphant"
MemeGPT: [Re-searches with triumph + success filter]

User:   "Now show me a GIF version of the third one"
MemeGPT: [Returns GIF for meme #3]

User:   "Download it"
MemeGPT: [Triggers download]
```

**Supported follow-up commands:**
- "Give me something funnier"
- "More relatable"
- "I want a classic meme, not a new one"
- "Show this as a GIF"
- "Something from SpongeBob"
- "More options"
- "Explain why you picked this one"

---

### Feature 4: Feedback & Personalization

**Per-session signals:**
- 👍 / 👎 on each result (affects re-ranking in real time)
- Click = implicit positive signal
- Skip = implicit negative signal
- "More like this" → clones the session filter

**User account signals (after login):**
- Favorite memes saved to library
- Past download history
- Preferred format remembered
- Category preferences (work / gaming / relationship / etc.)

---

### Feature 5: Trending Memes Section

A real-time trending feed updated hourly:
- Top memes from Reddit (`r/memes`, `r/dankmemes`, `r/ProgrammerHumor`)
- Filtered by category: Work | Gaming | Relationships | Tech | General
- Trending keywords shown as chips (clickable search)
- "Meme Calendar" — seasonal memes (Monday, exam season, holidays)
- New memes indexed daily (automated pipeline)

---

### Feature 6: User Library

For logged-in users:
- Save any meme to personal library
- Create custom collections ("Monday Memes", "Work Replies", "Cricket Memes")
- Download history
- Shareable collection links
- Export collection as ZIP

---

### Feature 7: Individual Meme Pages (SEO Feature)

Each meme gets a standalone web page:
- URL: `memegpt.com/meme/drake-pointing`
- Shows meme image + GIF + video (if available)
- Shows related memes
- Download buttons (all formats)
- "Use this meme" → opens search pre-filled
- Meme history / origin / cultural context (generated by LLM)
- This creates **10,000+ SEO-indexed pages** automatically

---

## User Personas

### Persona 1: "The Group Chat Hero" (Primary)
- 18–28 years old, heavy WhatsApp / Telegram / Discord user
- Wants the right reaction meme in < 10 seconds
- Uses mobile app primarily
- Shares 5–10 memes per day

### Persona 2: "The Content Creator"
- Social media manager, meme page admin, influencer
- Needs trending + format-flexible memes
- Uses web app, needs high-res downloads
- Values fresh content that isn't overused

### Persona 3: "The Developer / Marketer"
- Wants API access
- Uses memes in blog posts, Slack, product marketing
- Values embed code + link sharing

---

## MVP Scope (Build in Order)

### MVP Phase 1 — Core Search (Weeks 1–4)
- [ ] Web app: text input → meme results
- [ ] 5,000 meme database (imgflip + Reddit dataset)
- [ ] PNG + GIF download
- [ ] Copy to clipboard
- [ ] Basic dark-mode UI
- [ ] Deployed to Vercel + Railway

### MVP Phase 2 — Polish & Mobile (Weeks 5–8)
- [ ] Mobile app (React Native — iOS + Android)
- [ ] MP4 / video format support
- [ ] User accounts + saved library
- [ ] Share link with OG image preview
- [ ] Trending section
- [ ] App store submission

### MVP Phase 3 — Growth (Month 3+)
- [ ] Individual meme SEO pages
- [ ] Meme blog (auto-generated content)
- [ ] Browser extension
- [ ] Developer API
- [ ] Analytics dashboard
- [ ] Multi-language (Hindi, Spanish, Portuguese)

---

## Industry-Level Non-Functional Requirements

### Performance
| Metric | Target |
|---|---|
| Search response time (P50) | < 1.5 seconds |
| Search response time (P95) | < 3 seconds |
| Image load time from CDN | < 200ms |
| App cold start (mobile) | < 2 seconds |
| App warm start (mobile) | < 0.5 seconds |
| Uptime | 99.5% |

### Scalability
- Stateless API — horizontal scaling ready
- CDN-served media — no server load for images
- Redis caching for top 1000 queries (cache hit ratio > 60%)
- Vector search scales to 1M+ memes without architecture change

### Security
- Rate limiting: 60 req/min per IP (unauthenticated), 300/min (authenticated)
- Input sanitization: max 2000 characters per query
- NSFW filter: mandatory, opt-out only for verified adult accounts
- No PII stored: sessions are anonymous by default
- GDPR compliant: data deletion on request

### Content Moderation
- Pre-screening: all memes reviewed before indexing
- NSFW classifier (CLIP-based) rejects adult content
- Community flagging: users can report inappropriate memes
- Auto-removal: memes flagged 5+ times go to review queue
- Manual review dashboard for admin

### Accessibility
- All meme images have AI-generated alt text
- Keyboard navigation (Tab + Enter)
- Screen reader support (ARIA labels)
- Color contrast ratio > 4.5:1
- Font size minimum 14px on mobile

### Legal / Copyright
- Only index memes from: Creative Commons, Fair Use meme templates, original content
- DMCA takedown process: `legal@memegpt.com` → 48-hour response
- No watermark stripping
- Terms of service: meme templates are transformative works (fair use)
- Do NOT redistribute copyrighted movie clips as MP4 — GIF/image only for those

---

## Monetization Roadmap (Future)

| Tier | Price | Features |
|---|---|---|
| Free | $0 | 20 searches/day, GIF + PNG, basic formats |
| Pro | $5/month | Unlimited searches, all formats, HD downloads, library |
| Team | $15/month | Everything Pro + API access, team library, custom branding |
| API | Pay-per-use | $0.001 per search call, for developers |

> **Launch strategy:** 100% free at launch. No paywalls. Get users first.
