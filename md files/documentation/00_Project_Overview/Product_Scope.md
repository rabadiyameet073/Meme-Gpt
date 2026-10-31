# MemeGPT — Product Scope

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Defines what MemeGPT includes and excludes — clear scope boundaries for MVP and future phases.

---

## In Scope (MVP — Phase 1)

| Feature | Description | Priority |
|---|---|---|
| AI Meme Search | Natural language → ranked meme results | P0 |
| Emotion Detection | Detect user emotion, match to memes | P0 |
| Multi-Format Support | GIF, PNG, MP4, WebP per meme | P1 |
| Copy to Clipboard | One-click copy via Clipboard API | P1 |
| Download | Direct file download via CDN redirect | P1 |
| Trending Memes | Hourly-refreshed trending list | P1 |
| Suggestion Chips | Quick-search tags below input | P1 |
| Feedback System | 👍/👎 to improve results | P1 |
| Responsive Web App | Desktop + mobile responsive | P0 |
| SEO Meme Pages | Individual pages per meme (SSR) | P1 |

---

## Out of Scope (MVP)

| Feature | Why Excluded | Phase |
|---|---|---|
| User accounts / login | Adds friction, not needed for search | Phase 2 |
| Meme creation/editing | Different product entirely | Phase 3 |
| Social features | Not core to meme finding | Phase 3 |
| Meme commenting | Not core feature | Phase 3 |
| Payment / Pro tier | Needs user accounts first | Phase 2 |
| Admin dashboard | Manual DB management for now | Phase 2 |
| Content moderation AI | Manual review sufficient for 10K memes | Phase 2 |
| Multi-language UI | English only for launch | Phase 3 |
| Real-time notifications | No user accounts = no notifications | Phase 3 |

---

## Phase Roadmap Summary

| Phase | Scope | Timeline |
|---|---|---|
| **Phase 1 (MVP)** | Search, download, trending, feedback | Months 1-4 |
| **Phase 2 (Growth)** | User accounts, API keys, analytics, moderation | Months 5-8 |
| **Phase 3 (Scale)** | Collections, chat refinement, mobile app, i18n | Months 9-12 |
| **Phase 4 (Expand)** | Meme creation, social features, premium tier | Year 2 |

---

> **Related Documents:**
> - [Vision.md](./Vision.md) — Product vision
> - [Goals.md](./Goals.md) — Measurable goals
> - [13_Project_Management/Roadmap.md](../13_Project_Management/Roadmap.md) — Detailed roadmap
