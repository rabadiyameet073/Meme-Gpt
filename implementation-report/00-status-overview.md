# 00 — Status Overview (scored, with evidence)

## Methodology
Each MD requirement was checked against actual code (file:line), not docs claims. Ratings: ✅ = coded + paths verified · 🟡 = coded but needs live keys/data/run to prove · ❌ = missing or materially below MD target.

## Scoreboard (~52 tracked requirements)

| Area | ✅ Complete | 🟡 Partial | ❌ Missing | Evidence snapshot |
|---|---|---|---|---|
| Backend / API | 30 | 2 | 0 | 34 routers `api/v1/__init__.py:38-74`; core+admin+chat+collections+share+chips+download+users+developer+webhooks+sitemap all present |
| AI / ML pipeline | 12 | 1 | 1 | Groq/MiniLM/emotion/recommend/rerank/rules/TFIDF real; image service real but bulk unproven; retrain absent |
| Vector / cache / CDN | 4 | 2 | 1 | Qdrant named vectors + filters + cascade + DB fallback; Redis + in-mem; R2 scripts real, live serve unproven; live index empty locally |
| Vite SPA | 14 | 0 | 0 | 62 files; 6 tabs + detail/about/privacy; Zustand/Query/RHF present; 8 test suites |
| Next.js web | 8 | 3 | 0 | 40+ tsx/ts; routes + sitemap/robots/auth; OG/JSON-LD/CWV audit left |
| Mobile | 9 | 2 | 1 | Screens + offline/push/share hooks + full Expo deps; LAN + submit left; widget deferred |
| Data / scripts | 8 | 1 | 1 | 25 + 16 scripts real; volume 145/5000 |
| Infra / DevOps | 7 | 2 | 2 | Docker/compose/9 workflows/env template real; live URLs + domains left |
| Testing | 6 | 1 | 0 | 139 pytest + Vitest + Locust + evaluate; CI green not run here |
| Docs | 4 | 0 | 0 | This folder + visions replace 206 legacy files |
| Security / moderation | 7 | 1 | 0 | Sanitize/rate/GDPR/OAuth-code/moderation-4-routes; true-CLIP-NSFW check left |
| **Total** | **~109 sub-items ≈ 81%** | **~15 ≈ 15%** | **~6 ≈ 4%** | Code-complete; remainder is keys/data/deploy/proof |

## What changed since the old 55% report
1. **"services/api stubs" claim is false now:** 29 real files, no `[0.01]*384` mocks (only `Mocking-Spongebob` meme *name* matched the word "mock").
2. **Old gaps now coded:** OAuth Google/GitHub routes + JWT + ApiKey DB lookup · moderation 4 routes + Flag model · BLIP/CLIP/OCR service · Zustand/Query/RHF/Reanimated/Paper/offline/push hooks.
3. **Remaining is operational, not architectural:** fill env → `docker-compose up` → seed 5k+ → index → R2 → deploy → verify.

## Fix load & sequencing
- **~70% ops:** env + compose + collectors→embed→seed→index→R2 + Railway + Vercel ×2 + UptimeRobot + Sentry (≈2–4 days solo).
- **~20% verify:** CDN serve <200ms, search P50<1s/P95<3s, OG/JSON-LD, ARIA ≥4.5:1, CI green (≈1–2 days).
- **~10% build:** Prisma `seed.ts` rewrite, OG image generator, optional retrain cron + Ollama fallback (post-launch).
- **Order:** `01-backend-ai` (env→Qdrant→images→auth→moderation) → data volume → `02-frontend` (Vite→Next→mobile) → `03-release` gate. Details in files 01–03.

## Evidence & effort ledger (per area)
| Area | Verify command (proof) | Current | Effort to green |
|---|---|---|---|
| Backend routes | `grep -c "@router\." backend/app/api/v1/*.py` + hit each once | ✅ 34 routers live | 0.5d (hit-all script) |
| AI pipeline | search with `GROQ_API_KEY` unset → rule fallback + `intent_source` | ✅ | 0.5d (flag `intent_source`) |
| Qdrant live | `get_collection_info().points_count` | 🟡 0 local | 1d (cloud + index) |
| Redis live | 2nd identical search `cached:true` + <50ms | 🟡 in-mem only | 0.5d (Upstash bind) |
| R2/CDN live | 20-URL spot check 200 + <200ms | 🟡 scripts only | 1d (bucket + upload) |
| Data volume | `len(json.load(memes.json))` | ❌ 145/5000 | 2–3d (collectors run) |
| OAuth live | login→callback→me round-trip | 🟡 code only | 0.5d (keys + test users) |
| Moderation E2E | flag→queue→review→excluded | 🟡 code only | 0.5d (admin run-through) |
| Vite acceptance | build + vitest + manual §02 list | ✅~95% | 0.5d |
| Next OG/SEO | build + Rich-Results + card validator | 🟡 ~80% | 1d |
| Mobile submit | LAN run + eas build + store submit | 🟡 ~85% | 2d + store review wait |
| CI green | push PR → all workflows pass | 🟡 not run here | 0.5d |
| **Total to shippable** | — | **~81%** | **~10–12 solo days + review waits** |
