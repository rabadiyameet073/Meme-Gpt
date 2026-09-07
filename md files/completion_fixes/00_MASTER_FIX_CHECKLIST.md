# 00 — MemeGPT: Master Fix Checklist
> Complete roadmap to take MemeGPT from 55% → 100% completion.  
> Every guide in this folder is self-contained with exact file paths, code, and commands.

---

## Priority Legend

| Priority | Meaning | Effort |
|----------|---------|--------|
| 🔴 P0 | **Critical** — Project cannot ship without this | Hours |
| 🟠 P1 | **High** — Core feature or major gap | 1–2 days |
| 🟡 P2 | **Medium** — Improves quality, user experience | 1 day |
| 🟢 P3 | **Nice-to-have** — Polish, growth features | Hours |

---

## Fix Guide Index

Execute in this order (dependencies flow top-to-bottom):

| # | Guide File | Priority | Status | What It Fixes |
|---|-----------|----------|--------|---------------|
| 01 | [Architecture Consolidation](./01_Architecture_Consolidation.md) | 🔴 P0 | `[x]` | Dual backend (`backend/` vs `services/api/`), dual frontend (`frontend/` vs `apps/web/`), duplicate mobile app |
| 02 | [Meme Database Population](./02_Meme_Database_Population.md) | 🔴 P0 | `[x]` | Database has <1000 memes; need 5,000+ with real data from Imgflip, Reddit, Giphy |
| 03 | [BLIP + CLIP Image AI Pipeline](./03_BLIP_CLIP_Image_Pipeline.md) | 🟠 P1 | `[x]` | Missing BLIP captions, CLIP image embeddings, OCR text extraction in indexing scripts |
| 04 | [User Authentication & OAuth](./04_User_Authentication_OAuth.md) | 🟠 P1 | `[x]` | No Google/GitHub OAuth, no user registration, JWT is configured but not wired |
| 05 | [Content Moderation & NSFW](./05_Content_Moderation_NSFW.md) | 🟠 P1 | `[x]` | No CLIP-based NSFW classifier, no community flagging, no admin review queue |
| 06 | [Mobile App Completion](./06_Mobile_App_Completion.md) | 🟠 P1 | `[x]` | Missing push notifications, offline cache, Reanimated animations, native share, app store submission |
| 07 | [Next.js Web App Completion](./07_NextJS_Web_App_Completion.md) | 🟡 P2 | `[x]` | SEO meme pages are skeletons, blog system, features page, download page, JSON-LD structured data, OG images |
| 08 | [Production Deployment](./08_Production_Deployment.md) | 🔴 P0 | `[x]` | Not deployed live yet; Railway backend + Vercel frontend + R2 CDN + custom domain setup |
| 09 | [SEO & Marketing Completion](./09_SEO_Marketing_Completion.md) | 🟡 P2 | `[x]` | Category pages, auto-generated blog, Google Search Console, ASO for app stores |
| 10 | [Frontend Library Upgrades](./10_Frontend_Library_Upgrades.md) | 🟡 P2 | `[x]` | Add Zustand, TanStack Query, React Hook Form to match spec |
| 11 | [Accessibility & A11y](./11_Accessibility_A11y.md) | 🟡 P2 | `[x]` | AI-generated alt text, ARIA labels, keyboard navigation, screen reader support, color contrast |
| 12 | [Missing API Endpoints](./12_Missing_API_Endpoints.md) | 🟡 P2 | `[x]` | Download redirect endpoint, user profile CRUD, blog API, developer API portal |
| 13 | [Monitoring & Analytics](./13_Monitoring_Analytics.md) | 🟢 P3 | `[x]` | Umami self-hosted analytics, uptime monitoring, Resend email, performance dashboards |
| 14 | [Testing & CI Gaps](./14_Testing_CI_Gaps.md) | 🟢 P3 | `[x]` | Frontend tests, automated latency benchmarks, offline AI evaluation pipeline |
| 15 | [Non-Functional Requirements](./15_Non_Functional_Requirements.md) | 🟢 P3 | `[x]` | Performance budgets, GDPR compliance, weekly model retraining, multi-language support |

---

## Dependency Graph

```
01 Architecture Consolidation ──┐
                                ├──▶ 02 Meme Database Population ──▶ 03 BLIP/CLIP Pipeline
                                │
                                ├──▶ 04 User Auth/OAuth
                                │
                                ├──▶ 08 Production Deployment
                                │         │
                                │         ├──▶ 09 SEO & Marketing
                                │         └──▶ 13 Monitoring
                                │
                                ├──▶ 10 Frontend Libraries
                                │         └──▶ 07 Next.js Completion
                                │
                                ├──▶ 06 Mobile App ──▶ App Store Submission
                                │
                                ├──▶ 05 Content Moderation
                                │
                                └──▶ 11 Accessibility
```

---

## Quick Wins (< 1 Hour Each)

These small fixes from the guides can be done immediately:

1. **Run `scripts/build_huge_dataset.py`** to populate 5000+ memes (Guide 02)
2. **Install missing npm packages** in `apps/mobile/` — Reanimated, Paper (Guide 06)
3. **Copy `vercel.json`** into `apps/web/` directory (Guide 08)
4. **Generate OG image** and place in `apps/web/public/` (Guide 07)
5. **Add alt text generation** to meme seed script (Guide 11)

---

## How to Use These Guides

1. **Read Guide 01 first** — it resolves the dual-codebase confusion
2. **Each guide is self-contained** — has Prerequisites, Step-by-Step, Code, Verification
3. **All file paths are absolute** from project root `d:\Meme GPT\`
4. **Code blocks are copy-paste ready** — variable names match your existing codebase
5. **Each guide has a verification checklist** at the end

> ⚠️ **Important:** Complete Guide 01 (Architecture Consolidation) before starting any other guide. It determines which files you're editing.
