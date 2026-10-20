# 04 — Frontends & Mobile (production reference)

## 4.1 Vite SPA `frontend/` (primary app, 62 files)
- **Shell (`App.tsx`, 564 lines):** `ViewState tab: chat|search|trending|favorites|stats|admin + meme/:slug + about + privacy`, hash-routed (`#/chat`…), default `chat`. Top nav tabs with icons (`role=tablist`), code-split `lazy()` (ChatTab eager), `Suspense + AnimatePresence` 0.18s fade/slide. Shell: `Sidebar` (history/categories) + top-header (status pill `FastAPI v2.0 · N memes` from `api.health()`, audio toggle, `AuthModal`/avatar, `ThemeToggle`) + content (max 1200px) + footer (About/Privacy/landing, `/` shortcut hint) + toasts. OAuth `?token=` → `setStoredTokens()` → `fetchCurrentUser()`. Keys `1–6` tabs, `/` focus search.
- **Components (30):** `SearchInput` (textarea, 2000-char counter, paste, Ctrl/Cmd+Enter) + `SearchForm` + `SearchFormRHF` (validated) · `MemeCard` (preview, score %, emotion tags, GIF/PNG/MP4 badges, copy/download/share, 👍/👎, memo) · `ResultsGrid` (animated) · `FormatSelector` (sticky, localStorage) · `PreviewModal` (detail popup) · `ChatTab` (17KB ChatGPT-style multi-turn) · `SearchTab` · `TrendingTab` (18KB) + `TrendingSection` · `FavoritesTab` · `StatsTab` (analytics) · `AdminTab` (add/delete + bulk) · `MemeDetail` · `AboutView`/`PrivacyView` · `SuggestionChips` · `Sidebar` (recent) · `SkeletonCard` (pulse-solid) · `ThemeToggle` · `Canvas3DBackground` + `Tilt3D` · `ui/button|card|input` · `Icon` (17KB set).
- **Hooks (9):** `useSearchHistory` (localStorage, cap 20) · `useRecentSearches` · `useFormatPreference` (persisted) · `useSearch` / `useMemeSearch` / `useQueryHooks` (React Query: `useSearch` mutation, `useTrending` 5-min stale) · `useTrending` · `useToast` · `useValidation` · `useFocusTrap`.
- **Lib:** `lib/api.ts` (352 lines, re-exported by `api.ts`): `API_BASE = VITE_API_URL || NEXT_PUBLIC_API_URL || :8000`; `apiRequest<T>` (Bearer `memegpt_access_token`, `credentials:include`, `ValidationError` 422 field-mapping vs `ApiError` + `retry_after`); methods `search/getMeme/getTrending/trending/sendFeedback/analyze/searchMemes/categories/stats/favorites/toggleFavorite/createMeme/deleteMeme/vote/export/health/flagMeme/moderation-queue/review/classifyImage`; `getSessionId()` (`memegpt-session` or `crypto.randomUUID`). Plus `lib/auth|clipboard (ClipboardItem blob + URL fallback)|storage|store (Zustand)|analytics|audio (tap/click/success)|utils`.
- **Styling (`index.css`, 901 lines, vanilla — no Tailwind):** luxury-editorial solid system (ZERO gradients): dark `--bg-app:#0D0E11 --bg-sidebar:#131418 --bg-panel:#17181F --bg-card:#1C1E26 --text:#F1ECE6 --brand:#8D321F terracotta --gold:#C29B72 --teal:#035352` + `[data-theme=light]` alabaster; fonts Playfair Display / Space Grotesk / Outfit / JetBrains Mono; tactile solid shadows, radius 4–24px, shimmer/fade/slide, `@900px` single-column + sidebar hidden; `sr-only`, skip-link, focus-trap styles.
- **Build/test:** `dev: vite :5173 (proxy /api→:8000)` · `build: vite build` · `test: vitest run` (8 tests: a11y, analytics, SearchFormRHF, SearchInput, store, useMemeSearch, useQueryHooks). Envs: `.env.development VITE_API_URL=:8000`, `.env.production https://api.memegpt.com`.
- **Acceptance:** 6 tabs render; search <1.5s; copy/download/share/vote/favorites persist across reload; skeletons on throttled 3G; `npm run build` + `vitest run` green; axe clean, contrast ≥4.5:1.

## 4.2 Next.js `apps/web/` (SEO + marketing site)
- **Routes:** `/` SSR landing · `/app` CSR noindex search · `/meme/[slug]` SSG + `MemeDetailClient` + JSON-LD `ImageObject` · `/memes/[category]` category hubs · `/trending` ISR 1h · `/blog` + `/blog/[slug]` MDX (weekly cron) · `/download` · `/features` · `api/auth/[...nextauth]`. `layout.tsx` full metadata/OG/Twitter/canonical; `sitemap.ts` (static + 50k memes by popularity); `robots.ts`.
- **Components:** `layout/Header|Footer|Sidebar` · `meme/MemeCard|MemeGrid|MemeModal|DownloadButton|ShareButton|FormatSelector` · `search/SearchInput|SearchResults|SuggestionChips` · `ui/Badge|Button|Skeleton|Toast`. `lib/api.ts` (304 lines) typed client + `normalizeResult()` handling v1+v2 shapes; `lib/analytics|utils`, hooks `useDownload|useMemeSearch`.
- **Deps:** `next^14.1, react^18, framer-motion` (+ clsx, tailwind-merge). `NEXT_PUBLIC_API_URL` → backend.
- **Acceptance:** `npm run build` clean; `/meme/[slug]` valid JSON-LD + canonical + OG 1200×630; sitemap includes top memes; CWV LCP<2.5s CLS<0.1 (`next/image` fixed-aspect/lazy/blur + font preload).

## 4.3 Mobile `apps/mobile/` (Expo ~51, RN 0.74)
- **Screens:** `_layout` (Expo Router) → `(tabs)/index` (search UI: suggestions, format filter, 2-col grid, 10KB) · `(tabs)/trending` · `(tabs)/library` (saved) · `meme/[id]` detail.
- **Components/hooks:** `MemeCard (5.4KB) | SearchBar | FormatPicker | BottomSheet (6KB)`; `useMemeActions` (share/save) · `useMemeSearch` · `useOfflineCache` (offline-50 via async-storage) · `usePushNotifications` (expo-notifications) · `useShare|useShareAndDownload`; `lib/api.ts` (`search/trending/getMeme/submitFeedback/vote/getDownloadUrl` vs `${EXPO_PUBLIC_API_URL}/api/v1`).
- **Config:** `app.json` (dark theme, iOS/Android, ~29MB) · `eas.json` (development/preview/production) · full Expo deps (clipboard, device, file-system, haptics, image, linking, media-library, sharing, vector-icons, gesture-handler, paper, reanimated, safe-area, screens).
- **Run:** `npm install` → set `EXPO_PUBLIC_API_URL` to **LAN IP** (not localhost on device) → `npx expo start` → iOS sim / Android emu / Expo Go → `eas build` → submit (Play $25 once, Apple $99/yr).
- **Acceptance:** search/trending/library/detail all load from LAN backend; share sheet opens; download saves to camera roll; offline-50 survives restart; no red-box errors.

## 4.4 API client surface (what every frontend must implement)
| Method | HTTP | Purpose |
|---|---|---|
| `search(query, {format, limit})` | `POST /v1/search` | Ranked memes + intent + latency |
| `getMeme(slug)` | `GET /v1/memes/:slug` | Detail + formats + related |
| `getTrending({category, limit, period, offset})` | `GET /v1/trending` | Ranked trending w/ scores |
| `sendFeedback({query_id, meme_id, action})` | `POST /v1/feedback` | Fire-and-forget weights §03-3.4 |
| `vote(meme_id, ±1)` | `POST /v1/vote` | Thumbs with session dedupe |
| `toggleFavorite(meme_id, sessionId)` | `POST /v1/favorites` | 200-cap, sync P1 |
| `createMeme/deleteMeme` | `POST|DELETE /admin/memes` | Admin gated (401 otherwise) |
| `export(results, txt|json|md)` | `POST /v1/export` | File download |
| `health()` | `GET /health` | Status pill + warm ping |

## 4.5 Key component contracts
- `SearchInput(value, maxLength=2000, onSubmit, loading)` — counter, paste-normalize, `Ctrl/Cmd+Enter`, disabled+spinner states, `aria-invalid` on 422.
- `MemeCard(meme, score, onCopy/onDownload/onShare/onVote/onFavorite)` — memoized; badges from `formats` presence; preview prefers `gif_url → image_url → thumb_url`.
- `FormatSelector(value, onChange)` — persists to localStorage (`useFormatPreference`); sticky on results pages.
- `PreviewModal(meme, open, onClose)` — focus-trapped, Esc closes, share/copy inside.
- Mobile `MemeCard` adds double-tap vote + long-press preview; `BottomSheet` hosts download/share sheet.

## 4.6 Frontend test matrix (minimum)
| Suite | Cases | Gate |
|---|---|---|
| SearchInput | placeholder, counter, Ctrl+Enter, disabled, 422 mapping | vitest green |
| MemeCard | renders score/emotion/badges, copy fallback, memo | vitest green |
| Store/history | persist, 200-cap evict, recent-20 order | vitest green |
| Hooks | search mutation, trending stale-5min, toast queue | vitest green |
| a11y | axe no violations both themes, focus-trap, contrast | CI required |
| E2E smoke (manual until Playwright) | §02-frontend checklist in implementation-report | Release gate |
