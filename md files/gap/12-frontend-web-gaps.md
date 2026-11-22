# 12 — Frontend (Web) Gaps

**Source requirements:** `md files/documentation/04_Frontend/*` (Frontend_Overview, Routing, Components, Styling_System, State_Management), `md files/upgraded_docs/10_Frontend_Missing_Features.md`, `md files/completion_fixes/07_NextJS_Web_App_Completion.md`, `10_Frontend_Library_Upgrades.md`
**Related:** [01-architecture-consolidation-gaps](01-architecture-consolidation-gaps.md) · [13-user-workflow-gaps](13-user-workflow-gaps.md) · [14-ui-ux-accessibility-responsive-gaps](14-ui-ux-accessibility-responsive-gaps.md) · [15-seo-marketing-gaps](15-seo-marketing-gaps.md)

## Context
- `frontend/` (Vite + React 19): the **more complete** app. It has search, chat, trending, favorites/collections, admin, theme toggle, skip link, lazy tabs and Vitest tests. It uses hash routing (`App.tsx:~67-102`).
- `apps/web/` (Next.js): the marketing, blog, SEO and category pages are good; its `(app)` routes are a thinner duplicate.

## Verified as fully implemented
Next.js metadata/OG/Twitter/JSON-LD (`apps/web/app/layout.tsx:24-62`, `meme/[slug]/page.tsx:11-104`); blog, features, download and category pages; sitemap/robots; SearchInput with char limit, ⌘↵ and `role="alert"` errors (`SearchInput.tsx:40-104`); format preference persisted with `radiogroup` semantics; Vite theme toggle (`ThemeToggle.tsx`), skip link, lazy tabs, collections CRUD (`FavoritesTab.tsx:52-108`).

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| FE-01 | One canonical web architecture | Incorrectly implemented | Duplicate apps (see [01](01-architecture-consolidation-gaps.md) ARC-02) | Decision D-1 | Critical |
| FE-02 | Real URLs (not hash routes) for app views | Needs improvement | `window.location.hash = '#/meme/...'` in Vite | React Router / Next routes, so pages can be shared and indexed | Medium |
| FE-03 | Routes `/about`, `/privacy`, `/api/health` (`Routing.md:21-23`) | Not implemented (apps/web) | Only `(app)`, `(marketing)`, `api/auth`, `meme`, `memes` exist | Add the pages (privacy is legally required) | High |
| FE-04 | `/trending` uses ISR with 1h revalidation (`Routing.md:20`) | Incorrectly implemented | `apps/web/app/(app)/trending/page.tsx:1` `'use client'` + `useEffect` | Server component, `revalidate=3600` | Medium |
| FE-05 | Static generation of meme pages (`Routing.md:80`) | Not implemented | No `generateStaticParams` in `meme/[slug]` | Add with ISR | Medium |
| FE-06 | Meme detail completeness (`08_Features/Multi_Format.md`) | Partially implemented | No related-memes carousel or origin/usage section in `MemeDetailClient.tsx` | Add both (needs a backend related endpoint) | Medium |
| FE-07 | Layout on all pages | Not implemented | `app/meme/*`, `app/memes/*` are outside the route groups, so no Header/Footer | Shared root layout | Medium |
| FE-08 | Working nav links | Incorrectly implemented | `Footer.tsx:7-8` and `(marketing)/page.tsx:403` link to `/app/trending` and `/app/library`, which don't exist | Fix the hrefs | High |
| FE-09 | Single footer | Incorrectly implemented | `(marketing)/layout.tsx:10` plus an inline footer in `page.tsx:393-407` | Remove the duplicate | Low |
| FE-10 | React Query for data fetching (`Frontend_Overview.md`, `completion_fixes/10`) | Not implemented (apps/web) / Partially implemented (Vite) | apps/web has no `@tanstack/react-query`; Vite has `useQueryHooks.ts` but the tabs call `api.*` directly (`SearchTab.tsx:41`, `ChatTab.tsx:57`) | Adopt it consistently | Low |
| FE-11 | Request cancellation / no double fetch | Incorrectly implemented | The `AbortController` signal is never passed (`useMemeSearch.ts:70-71`); `?q=` triggers two searches (`useMemeSearch.ts:120-126` + `app/page.tsx:17-24`) | Pass the signal; single effect | Medium |
| FE-12 | Search contract fields forwarded | Incorrectly implemented | `apps/web/lib/api.ts:151-158` drops `limit`, `nsfw`, `session_id` | Forward them | High |
| FE-13 | Dead components wired or removed | Needs improvement | `MemeModal`, `ShareButton`, `DownloadButton`, `ui/Toast`, `ui/Badge`, `ui/Button` are not imported anywhere in apps/web | Connect or delete | Low |
| FE-14 | Real data, no placeholders | Needs improvement | Hardcoded "5,000+ memes", "<1.5s" (`(marketing)/page.tsx:89-93`); fake random latency in `landing.html:1042`; `'google-site-verification-token'` fallback (`layout.tsx:53`) | Live `/stats`; remove fakes | Medium |
| FE-15 | Dark/light theme in apps/web | Not implemented | `layout.tsx:71` hardcodes `className="dark"` | Toggle + `prefers-color-scheme` | Low |
| FE-16 | PWA in the canonical app | Partially implemented | Vite has `manifest.json` + `sw.js`; apps/web `public/icons/` has only `.gitkeep` | Icons + manifest for the canonical app | Low |
| FE-17 | Analytics events wired | Partially implemented | See [17](17-reporting-analytics-monitoring-gaps.md) RPT-03 | — | Medium |
| FE-18 | Frontend tests run in CI | Partially implemented | 7 test files; only `workflows-upgraded/ci.yml:95` runs `npm test` | See [19](19-testing-gaps.md) | Medium |
