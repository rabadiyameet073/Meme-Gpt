# 04 — AI / ML Pipeline Gaps (LLM, emotion, embeddings, Qdrant, rerank, image)

**Source requirements:** `md files/documentation/05_AI_System/*` (AI_Pipeline, LLM_Workflow, Embeddings, Vector_Database, Scoring_Logic, Image_Analysis, Future_AI), `md files/upgraded_docs/03_Qdrant_Vector_Search.md`, `05_AI_Pipeline_Fix.md`, `md files/completion_fixes/03_BLIP_CLIP_Image_Pipeline.md`, `md files/implementation_guides/01_Qdrant_Setup_And_Indexing.md`, v1/v2 `02_TECH_STACK_AND_MODELS.md`, `03_ML_PIPELINE_AND_TRAINING.md`
**Related:** [03-search-api-gaps](03-search-api-gaps.md) · [07-data-corpus-pipeline-gaps](07-data-corpus-pipeline-gaps.md) · [05-trending-feedback-gaps](05-trending-feedback-gaps.md) · [21-performance-gaps](21-performance-gaps.md)

## Verified as fully implemented
| Item | Evidence |
|---|---|
| Pipeline order: cache → Groq intent + DistilRoBERTa emotion (parallel `asyncio.gather`) → MiniLM embedding → Qdrant `top_k=15` → rerank → cache | `backend/app/services/recommendation_service.py` |
| Groq `llama-3.1-8b-instant` with a rule-based fallback | `config.py:89`, `llm_service.py:91` |
| MiniLM-L6-v2 (384-d) + `j-hartmann/distilroberta` emotion model | `embedding_service.py:31-32` |
| Qdrant remote → embedded → none fallback; named vectors text 384 / image 512 / combined 896; `query_points` API | `search_service.py:34-95, 132-160, 520-560` |
| Hybrid reranker (semantic + lexical + emotion + popularity + recency + format) | `rerank_service.py:39-47` |

**This is the strongest part of the product: real retrieval, not a mock.**

## Gaps
| Gap ID | Requirement | Status | Evidence | Expected | Required change | Priority |
|---|---|---|---|---|---|---|
| AI-01 | Image understanding used for retrieval (`completion_fixes/03`) | Partially implemented | CLIP/BLIP vectors are generated at index time, but `vector_search(... vector_name="text")` is the default (`search_service.py:590`) and no caller uses `image` or `combined` | Query uses CLIP text→image similarity or the combined vector | Encode the query with the CLIP text tower; search `combined` or fuse text and image scores | High |
| AI-02 | Single image-analysis service | Needs improvement | `image_processing_service.py` and `image_analysis_service.py` both wrap BLIP/CLIP | One module | Merge them | Medium |
| AI-03 | No silent fake embeddings | Incorrectly implemented (risk) | `embedding_service.py:101-107` `_fallback_embed` returns a SHA-256 pseudo-vector when the model is missing; `upsert_memes` doesn't check `is_text_model_loaded()` | Indexing aborts when the model isn't loaded | Raise inside the indexing scripts; keep the fallback only for tests. ASSUMPTION: no index has been poisoned yet, needs runtime check via `scripts/verify_index.py` | High |
| AI-04 | Single embedding model instance | Needs improvement | `semantic_search.py:26` loads its own `SentenceTransformer("all-MiniLM-L6-v2")` for the legacy `meme_matcher`/`rule_engine` path | One shared model (memory) | Reuse `embedding_service`; delete the legacy TF-IDF matcher if it isn't used | Medium |
| AI-05 | Scoring formula as documented (`Scoring_Logic.md:40-90`: cosine + 0.15/0.08/0.10/0.05 bonuses) | Incorrectly implemented relative to the doc (deliberately) | `rerank_service.py:39-47`: semantic 0.34, lexical 0.30, primary 0.14, secondary 0.06, popularity 0.08, recency 0.03, format 0.05; a code comment explains the saturation fix | Doc and code agree | Update `Scoring_Logic.md`; tune with `scripts/optimize_rerank_weights.py` against a larger golden set | Medium |
| AI-06 | Personalised ranking from feedback | Not implemented | `rerank_service.personalized_rerank` (`:357`) is never called; `SIGNAL_WEIGHTS` (`recommendation_service.py:35`) is unused; `session_id` never reaches `recommend` | Session/user category affinity boosts | Pass `session_id`; build an affinity map from `Feedback`; call `personalized_rerank` | Medium |
| AI-07 | Latency < 1.5s (vision §1.3) | At risk | Synchronous `requests.get(timeout=5)` ×2 in `giphy_service.py:43,92`, called inline from async `recommend` | No blocking I/O in the event loop | `httpx.AsyncClient` + `gather`, ~800ms timeout, cache the Giphy results. ASSUMPTION – latency needs a benchmark | High |
| AI-08 | Index stays in sync with the DB | Partially implemented | Admin create/patch does not embed or upsert to Qdrant (`admin.py:~95-146`); only delete removes the point | Every write path re-indexes | Call the embedding + `upsert_memes` on create/update | High |
| AI-09 | Popularity signal reaches the vector payload | Partially implemented | `viral_score` is updated in SQL; Qdrant payload sync only via the manual `scripts/sync_popularity_scores.py` | Scheduled sync | Add to the hourly `trending.yml` cron | Medium |
| AI-10 | Evaluation harness with Precision@5 (`Future_AI.md:41,188`, `10_Testing/AI_Evaluation`) | Partially implemented | `data/eval/golden_queries.json` has **3** queries, `test_queries.json` 15; `evaluate.py` exists in 4 places (root, `backend/`, `scripts/`, `backend/scripts/`) | ≥100 labelled queries, P@5 tracked in CI | Build the golden set; keep one `evaluate.py`; add a CI job that fails if P@5 regresses | Medium |
| AI-11 | Cross-encoder / learned reranker (v2 `03_ML_PIPELINE`, Future_AI) | Not implemented | No `CrossEncoder` anywhere | Optional P2 | Plan after the corpus reaches ≥5k | Low |
| AI-12 | Fine-tuning / retraining loop (v2 `03_ML_PIPELINE_AND_TRAINING.md`, `completion_fixes/15`) | Not implemented | `backend/app/jobs/` contains only `retention.py`; no training scripts | Periodic retraining from feedback | Defer to Phase 4; document as a future item | Low |
| AI-13 | Dead duplicate pipelines | Needs improvement | `rag_service`, `smart_search_service` and `services/api/*` are unused | Removed | See [01](01-architecture-consolidation-gaps.md) ARC-08 | Medium |

## Dependencies
AI-01 and AI-10 only become meaningful after the corpus grows ([07](07-data-corpus-pipeline-gaps.md) DATA-01). AI-08 is shared with [11](11-admin-panel-gaps.md).
