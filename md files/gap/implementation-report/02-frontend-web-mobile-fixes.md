# 02 — Frontend / Web / Mobile Fixes (acceptance checklists)

## Vite SPA `frontend/` — Bauabnahme (currently ~95% ✅)
- [ ] `VITE_API_URL` correct per env (dev `:8000`, prod `https://api.memegpt.com`); status pill shows `FastAPI v2.0 · N memes`.
- [ ] All 6 tabs + `meme/:slug` + About + Privacy render; hash routes deep-linkable; tab keys `1–6`, `/` focuses search.
- [ ] Search E2E: type → Enter → top-5 with % bars + emotion badges + format badges <1.5s; empty query blocked with inline validation; 422 maps to field messages; 429 shows rate banner with retry timer; offline shows cached error state.
- [ ] Meme actions: copy (clipboard + fallback toast) · download picker (GIF/PNG/MP4/WebP → CDN) · share (native or link copy) · 👍/👎 persists + updates counts · star → Favorites survives reload (200 cap) · collections CRUD + recent lists.
- [ ] Chat tab multi-turn ("more sarcastic", "like #1 but GIF") refines without retyping; history drawer lists last 20.
- [ ] Perf/a11y: skeletons on throttled 3G; axe clean; contrast ≥4.5:1 both themes; focus-trap in modal; skip-link; `role=tablist|alert`; `aria-invalid` on errors.
- [ ] Gates: `npm run build` clean · `npx vitest run` 8/8 green · Lighthouse perf ≥90 desktop.
- **If red:** check `src/lib/api.ts` base/token/session → Network tab status → `src/lib/store.ts` persistence → backend CORS origins.

## Next.js `apps/web/` — Fertigstellung (~80% 🟡 → 100%)
1. [ ] Copy root `vercel.json` into `apps/web/` (headers/rewrites per spec); set `NEXT_PUBLIC_API_URL`; `npm run build` clean, no ESLint errors.
2. [ ] OG image: generate 1200×630 via `sharp` (meme collage + wordmark) → `/og-image.jpg` referenced in `layout.tsx`; verify with social card validator.
3. [ ] `/meme/[slug]`: valid JSON-LD `ImageObject` (Rich Results test), canonical URL, `preview_url` absolute, alt text from `generate_alt_text`.
4. [ ] Sitemap: `sitemap.ts` emits static + top-50k memes by `popularity_score`; submit to GSC; `robots.ts` allows `/meme/` + `/blog/`, disallows `/app`.
5. [ ] CWV: `next/image` fixed-aspect + lazy + blur placeholders; font preload; LCP<2.5s CLS<0.1 on `/` and `/meme/[slug]`.
6. [ ] Blog cron: weekly `generate_weekly_blog_post` → `/blog/[slug]` MDX renders with meme grids + internal links.

## Mobile `apps/mobile/` (~85% 🟡 → 100%)
1. [ ] `EXPO_PUBLIC_API_URL=http://<LAN-IP>:8000` (never localhost on device); `npx expo start`; open iOS simulator + Android emulator + physical Expo Go.
2. [ ] Search tab: suggestions + format filter + 2-col grid load; Trending tab ranks match backend; Library shows saved/offline; `meme/[id]` detail renders.
3. [ ] Actions: share sheet opens with image+link; download saves to camera roll (media-library permission flow); double-tap votes; haptics fire; offline-50 list survives app restart (async-storage); push token registers (`usePushNotifications`) without crash when denied.
4. [ ] `app.json` icons/splash/bundle IDs final → `eas build --platform all` green → submit (Play $25 once, Apple $99/yr) → store listings from `docs/ASO_Store_Listing.md`.
5. [ ] Deferred (document, don't block): home-screen widget, scheduled Meme-of-the-Day push campaign.

## Effort + tooling
| Surface | Effort | Commands |
|---|---|---|
| Vite acceptance | 0.5d | `npm run build`, `npx vitest run`, `npx axe` (or Lighthouse CI), throttled-3G pass |
| Next completion | 1d | `npm run build`, Rich-Results test, card validator, `next lint` |
| Mobile completion | 2d + store waits | `npx expo start --tunnel` (fallback for LAN issues), `eas build --platform all`, `eas submit` |
