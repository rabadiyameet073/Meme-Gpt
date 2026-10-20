# 03 — Backend, AI & Data (production reference)

## 3.1 App wiring
- Entry `backend/app/main.py`: `FastAPI(title="MemeGPT API", version="2.0.0")` + `lifespan` (init_db → Qdrant `create_collection(recreate=False)` → background `embedding_service.load_models()` thread → APScheduler daily 03:00 UTC retention). Mounts `v1_router` at `/api/v1` (+ legacy `/api`, `/v1`, `/`), `/static` for `data/images`. Middleware order: CORS → tiered rate-limit (anon 60 / free 120 / pro 300 / internal 1000, `429` + `X-RateLimit-*`) → request logger → global error handler (`{success:false, error, message, details, retry_after}` + 400/404/422/429/500/502/503/504). Security headers (CSP, `X-Frame-DENY`, HSTS); `Cache-Control` for `/media|/trending`.

## 3.2 Endpoint catalog (34 routers in `backend/app/api/v1/__init__.py`)
| Method + path | Handler | Notes |
|---|---|---|
| `POST /api/v1/search` (+ legacy `POST /search`, `POST /analyze`, `POST /api/analyze`) | `search.py:58-138` | Core pipeline; `SearchRequest{query, format_preference, nsfw, limit 1-20, session_id, filters}` (`models/search.py`); `BackgroundTasks` log + usage |
| `GET /api/v1/memes` (paged/filter) · `GET /api/v1/memes/{slug_or_id}` · `GET /api/v1/memes/{slug}/download` | `memes.py:57/139/169`, `download.py:22` | 307 redirect to R2/CDN + telemetry |
| `GET /api/v1/trending` | `trending.py` | Hourly score, category/period/offset |
| `GET /api/v1/categories` · `GET /api/v1/stats` | `categories.py:26/56` | Category list + platform stats |
| `POST /api/v1/feedback` · `POST /api/v1/vote` · `POST /api/v1/export` | `feedback.py:76/111/147` | Weights §3.4; export TXT/JSON/MD |
| `GET|POST /api/v1/favorites` · full `/collections*` CRUD + recent-viewed/copied + limits | `collections.py`, `collections_full.py` | Session anon → user-synced P1 |
| `POST /api/v1/chat/refine|/search` · `GET|DELETE /sessions/{id}` | `chat.py` | Multi-turn refinement |
| Auth: `POST /register|login|refresh|logout`, `GET|PUT /me`, `POST|GET|DELETE /api-keys`, `GET /tier`, `GET /google|github/login|callback`, jobs `recalculate-popularity|warm-up|analytics` | `auth.py` | OAuth service + JWT + `ApiKey.key_hash` DB lookup |
| `POST /flag` · `GET /queue` · `POST /review` · `POST /classify` (CLIP NSFW) | `moderation.py` | Flag model + admin review |
| `GET /api/v1/memes/{slug}/download`, `GET /health*` (+ `/health/sentry-test|error|stats`) | `download.py`, `health.py` | CDN + diagnostics |
| Info routers (static JSON manifests): deployment/dev/testing/security/privacy/validation/rate_limiting/project_management/troubleshooting/faq/mobile/references/marketing/appendix/users/developer/email/features/share/suggestion_chips/webhooks/sitemap | various | Real endpoints serving doc manifests; verify content freshness quarterly |

## 3.3 AI pipeline (6 stages, target <1.5s)
`services/recommendation_service.py:47-185` — cache (`make_cache_key`, TTL 3600) → `asyncio.gather(llm.parse_intent, emotion)` → `build_query_text` → `embed_text` (executor) → `vector_search top-15` → DB enrich/augment → `rerank` → Giphy live GIFs + viral picks → cache set.
- **Intent** (`llm_service.py`): Groq JSON `{situation, emotion_hint(joy|sadness|anger|surprise|fear|disgust|neutral), tone, keywords[:5], meme_format, intensity, categories}`; code-block extraction + schema validation; fallback `_rule_based_intent` (multilingual keywords, stop-word strip). Helpers: `clean_llm_json`, `generate_meme_tags`, `generate_alt_text`, `generate_weekly_blog_post`, `generate_test_dataset`.
- **Embedding+emotion** (`embedding_service.py`): `load_models()` once (torch threads=2, CPU); `embed_text` 384d L2 (fallback: SHA256-deterministic unit-norm); `detect_emotion` → `{primary, secondary, confidence, all}` (fallback keyword 6-class); `build_query_text`; `get_combined_embedding` 896d (0.65/0.35).
- **Retrieval** (`search_service.py`): singleton Qdrant (graceful `None` → DB fallback); collection `memes` named vectors text384/image512/combined896 cosine; `build_point` (MD5 string→int IDs, `[0.05]`-fill missing vectors, enriched payload `has_gif/has_video/nsfw/scores`); `upsert_memes batch 100`; `build_search_filter`; `vector_search` + threshold cascade + `adaptive_vector_search` + `_db_fallback_search` (popularity order) + `get_trending_memes`; formatters `format_search_meme_result` / `build_search_response_payload` (dual camel+snake keys).
- **Rules** (`rule_engine.py`): 20 category regex rules (coding/startup/exam/college/job/motivation/ai/business/gaming/bollywood/…) + 11 emotion patterns, confidence `min(0.65+n*0.1, 0.95)`, fallback `funny/general:0.3`, `humor:0.60`.
- **Offline matcher** (`meme_matcher.py`): `kw*0.30 + sem*0.20 + pop*0.20 + recency*0.10 + emotion 0.15+0.08 + format 0.05`, clamp [0,1], dedupe by name, threshold >0.05, confidence [0.15,0.99].
- **Images** (`image_processing_service.py`, offline only): BLIP caption + CLIP 512d + Tesseract OCR (`--psm 6 --oem 3`, grayscale+sharpen, win32 path handled) → `process_meme_image()`.

## 3.4 Scoring & feedback math
- Final: `min(1.0, cosine + 0.15*primary_match + 0.08*secondary_match + 0.10*popularity + 0.05*format)`.
- Popularity (weekly cron, 30d window): `(0.1*view + 0.5*click + 1.0*copy + 2.0*download + 3.0*share + 2.0*up − 1.0*down) / 10000`.
- Feedback actions → same weights (`SIGNAL_WEIGHTS`: view .1, click .5, copy 1, download 2, share 3, thumbs_up 2, thumbs_down −1, skip −0.3).

## 3.5 Database (`app/database.py`, `config.py`)
- Engine: SQLite WAL (`journal_mode=WAL, synchronous=NORMAL, busy_timeout 5000`, pool 5/overflow 10, pre_ping, recycle 1800) dev → Postgres via `DATABASE_URL`; `init_db()` auto-migrates missing cols; `sanitize_input/is_valid_input/is_valid_meme_id`.
- Tables: `Meme` (UUID PK, name/slug, categories/emotions/dialogue/explanation/keywords JSON, 5 media URLs + legacy refs, source/nsfw/alt_text/flag_count/moderation_status, view/download/usage/up/down, viral/popularity, timestamps, hybrids, dual-key `to_dict()`), `MemeUsage`, `MemeVote` (UQ meme+session), `FavouriteMeme`, `MemeFlag`, `User` (email/username/OAuth, plan/prefs/rate_limit, theme/format/nsfw/categories, admin), `SavedMeme`, `Feedback`, `SearchLog` (query_hash MD5, no PII, latency, cache_hit, model, emotion), `ApiKey` (key_hash/prefix/tier/revoked/rate_limit).
- Rules: nullable-add safe migrations; GIN on JSON arrays (prod); never log raw queries (hash only); 30-day retention purge via APScheduler.

## 3.6 Data runbook (scripts: root `scripts/` 25 + `backend/scripts/` 16)
1. `download_datasets.py` / `collect_imgflip_full.py` (templates, easiest) → `collect_giphy_full.py` (20k, 100 terms, ≤100 req/hr) → `collect_reddit_full.py` (PRAW r/memes/dankmemes, `.gifv→.gif`).
2. `preprocess_memes.py` (NSFW skip, 5KB–10MB, hash dedup). 3. `generate_embeddings.py` (BLIP+OCR+MiniLM+CLIP, batch 50). 4. `index_qdrant.py` / `reindex_all_to_qdrant.py` (+ `index_to_qdrant.py`). 5. `upload_to_r2*.py` + `generate_thumbnails*.py` (WebP). 6. `seed.py` (+ `seed_extended.py`, `build_huge_dataset.py` → 5k→50k target; current 145). 7. `verify_index.py`, `verify_env.py`/`check_env.py`, `evaluate.py` (+ backend variant) P@3/R@10/NDCG@5; `migrate_sqlite_to_postgres.py` for prod cutover.

## 3.7 Worked example (contract)
Request:
```json
POST /api/v1/search
{"query": "my code worked locally but fails in production", "format_preference": "gif", "limit": 5, "session_id": "s_abc123"}
```
Response (truncated):
```json
{"success": true, "query_id": "q_9f3a1c2e", "detected_emotion": "fear",
 "intent_parsed": {"emotion": "fear", "situation": "production deploy failure", "tone": "frustrated"},
 "results": [{"id": "m_042", "name": "This Is Fine", "slug": "this-is-fine",
   "relevance_score": 0.91, "confidence": 0.91, "emotion_match": "fear",
   "preview_url": "https://cdn.memegpt.com/gifs/this-is-fine.gif",
   "share_url": "https://memegpt.com/meme/this-is-fine",
   "formats": {"image": ".../this-is-fine.png", "gif": ".../this-is-fine.gif", "mp4": null, "thumb": ".../this-is-fine.webp"}}],
 "total_results": 5, "response_time_ms": 612, "cached": false}
```

## 3.8 Error catalog (all endpoints)
| HTTP | `error` code | When | Client action |
|---|---|---|---|
| 400 | `bad_request` | Empty query, bad enum | Fix input, show inline |
| 404 | `meme_not_found` | Unknown slug/id | Link trending fallback |
| 422 | `validation_error` | Pydantic fail (detail[] field+msg) | Map to form fields |
| 429 | `rate_limit_exceeded` | Tier quota hit (`retry_after` secs) | Banner + countdown + retry |
| 502 | `llm_unavailable` | Groq down (rule fallback already used, degraded flag true) | Show "simplified match" notice |
| 503 | `vector_unavailable` | Qdrant + DB both down | Trending cache page |
| 504 | `upstream_timeout` | Model inference > timeouts | Retry once, then fallback |

## 3.9 Rate-limit matrix
| Caller | Search `/search` | General reads | Writes (vote/feedback/admin) |
|---|---|---|---|
| Anonymous IP | 30/min | 60/min | 60/min (no admin) |
| Free API key | 100/min | 120/min | 120/min |
| Pro key ($9, future) | 500/min | 1000/min | 300/min |
| Internal | 1000/min | 1000/min | 1000/min |

## 3.10 Core DDL sketch (Postgres prod)
```sql
CREATE TABLE memes (
  id UUID PRIMARY KEY, slug TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
  categories JSONB DEFAULT '["general"]', emotions JSONB DEFAULT '[]',
  dialogue TEXT DEFAULT '', explanation TEXT DEFAULT '', keywords JSONB DEFAULT '[]',
  image_url TEXT, gif_url TEXT, mp4_url TEXT, webp_url TEXT, thumb_url TEXT,
  source TEXT DEFAULT 'manual', nsfw BOOLEAN DEFAULT FALSE, alt_text TEXT,
  flag_count INT DEFAULT 0, moderation_status TEXT DEFAULT 'approved',
  view_count INT DEFAULT 0, download_count INT DEFAULT 0, usage_count INT DEFAULT 0,
  upvotes INT DEFAULT 0, downvotes INT DEFAULT 0,
  viral_score DOUBLE PRECISION DEFAULT 0, popularity_score DOUBLE PRECISION DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now(), indexed_at TIMESTAMPTZ
);
CREATE INDEX idx_memes_slug ON memes(slug);
CREATE INDEX idx_memes_pop ON memes(popularity_score DESC);
CREATE INDEX idx_memes_cats ON memes USING GIN (categories);
CREATE TABLE search_logs (id UUID PRIMARY KEY, query_hash CHAR(32) NOT NULL, session_id TEXT,
  result_count INT, top_meme_id UUID, latency_ms INT, cache_hit BOOLEAN, model_used TEXT,
  emotion_detected TEXT, created_at TIMESTAMPTZ DEFAULT now());
```
