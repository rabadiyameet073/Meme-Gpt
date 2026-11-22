# 07 — Meme Corpus & Ingestion Pipeline Gaps

**Source requirements:** `md files/completion_fixes/02_Meme_Database_Population.md`, `md files/upgraded_docs/06_Meme_Indexing_Pipeline.md`, `15_Seed_Data_Expansion.md`, `md files/implementation_guides/04_Meme_Data_Pipeline.md`, `03_Cloudflare_R2_CDN_Setup.md`, `md files/upgraded_docs/09_CDN_R2_Setup.md`
**Related:** [04-ai-pipeline-gaps](04-ai-pipeline-gaps.md) · [10-content-moderation-gaps](10-content-moderation-gaps.md) · [16-integrations-gaps](16-integrations-gaps.md) · [15-seo-marketing-gaps](15-seo-marketing-gaps.md)

## Verified facts
| Metric | Documented target | Actual (counted in repo files) |
|---|---|---|
| Memes in `backend/data/memes.json` | 5,000+ (`completion_fixes/02`, `upgraded_docs/15:6`); 50K+ (`impl_guides/04:633`); 10K+ (SEO); ~1,000 (FAQ) | **145** |
| Embeddings in `backend/data/embeddings.json` | = corpus | **142** (3 missing) |
| `data/raw`, `data/processed`, `data/embeddings` | populated | **empty** (`.gitkeep` only) |
| Sources | Imgflip, Reddit, Giphy, Tenor | All 145 are `source=master_catalog`, all images hotlinked from `i.imgflip.com` |
| Prior report `GAP-ANALYSIS-2026-10-31.md` | — | claimed 195. Several corpus files disagree; treat 145 (`memes.json`) as authoritative pending a DB check (ASSUMPTION) |

Collectors **exist and look functional** in the code: `backend/scripts/collect_giphy_full.py`, `collect_reddit_full.py` (PRAW), `collect_imgflip_full.py` / `scrape_imgflip.py`, `scripts/build_huge_dataset.py`. They have never produced output in the repo.

## Gaps
| Gap ID | Requirement | Status | Evidence | Required change | Priority |
|---|---|---|---|---|---|
| DATA-01 | ≥5,000 indexed memes | Not implemented | 145 in `memes.json` | Run the collectors with API keys, dedupe (perceptual hash), ingest, index. Agree on one target per phase (see [22](22-documentation-and-stub-endpoint-gaps.md) DOC-04) | Critical |
| DATA-02 | Multi-source provenance | Partially implemented | Single `master_catalog` source | Store `source`, `source_id`, `license` per meme | High |
| DATA-03 | Embedding coverage 100% | Partially implemented | 142/145 | Regenerate; add a coverage assertion to `scripts/verify_index.py` and CI | Medium |
| DATA-04 | Media on R2 behind a CDN | Not implemented | Every `image_url` is on `i.imgflip.com`; `config.py:122` `CDN_BASE_URL` defaults to `https://cdn.memegpt.com` with nothing uploaded | Run `backend/scripts/upload_to_r2_full.py`, rewrite URLs, run `scripts/verify_cdn_urls.py` | High |
| DATA-05 | Thumbnails / multi-format assets (GIF, PNG, MP4, WebP) | Not implemented | `generate_thumbnails_full.py` exists; no output | Generate per-format variants during ingestion | High |
| DATA-06 | NSFW + moderation at ingestion | Not implemented | No ingestion script calls `nsfw_service` | See [10](10-content-moderation-gaps.md) MOD-03 | High |
| DATA-07 | Alt-text / captions (BLIP) for every meme | ASSUMPTION – needs runtime validation | `scripts/backfill_alt_text.py` exists; output not present in `memes.json` | Run the backfill as part of the pipeline | Medium |
| DATA-08 | Scheduled refresh | Partially implemented | Only Giphy is scheduled (`.github/workflows/weekly_reindex.yml:44`, `continue-on-error`) | Weekly Imgflip + Reddit too; fail loudly | Medium |
| DATA-09 | One canonical pipeline | Needs improvement | Three script trees (see [01](01-architecture-consolidation-gaps.md) ARC-07) | `scripts/full_index_pipeline.py` = collect → dedupe → moderate → caption → embed → upload → index → verify | Medium |

## Dependencies
Needs API keys (GIPHY, Reddit, Groq, R2), which the user must supply. Unblocks SEO (10k pages), honest landing-page stats and meaningful AI evaluation.
