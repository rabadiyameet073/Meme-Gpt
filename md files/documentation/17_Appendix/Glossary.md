# MemeGPT — Glossary

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Alphabetical glossary of all technical terms, abbreviations, and domain-specific concepts used across MemeGPT documentation.

---

| Term | Definition |
|---|---|
| **ANN** | Approximate Nearest Neighbor — search algorithm for finding similar vectors without checking every point |
| **API Key** | Secret token for authenticating developer API access (Phase 2) |
| **ASO** | App Store Optimization — optimizing app listings for App Store/Google Play visibility |
| **BLIP** | Bootstrapping Language-Image Pre-training — Salesforce model for generating image captions |
| **CDN** | Content Delivery Network — distributes media files globally for fast loading |
| **CLIP** | Contrastive Language-Image Pre-training — OpenAI model for image → vector embedding |
| **CORS** | Cross-Origin Resource Sharing — browser security mechanism controlling which domains can call your API |
| **Cosine Similarity** | Mathematical measure of similarity between two vectors (0.0 = unrelated, 1.0 = identical) |
| **CSR** | Client-Side Rendering — page rendered in the browser (used for search results) |
| **DistilRoBERTa** | Distilled version of RoBERTa model — MemeGPT uses it for emotion detection |
| **Embedding** | Dense vector representation of text or images for semantic search |
| **FastAPI** | Python web framework — MemeGPT's backend technology |
| **GIN Index** | Generalized Inverted Index — PostgreSQL index type for array columns |
| **Groq** | LLM inference provider using custom LPU hardware for fast inference |
| **HNSW** | Hierarchical Navigable Small World — graph-based ANN algorithm used by Qdrant |
| **ISR** | Incremental Static Regeneration — Next.js feature for periodically rebuilding pages |
| **JWT** | JSON Web Token — compact token format for authentication (Phase 3) |
| **L2 Normalization** | Scaling a vector to unit length — required for cosine similarity |
| **LLM** | Large Language Model — AI model for understanding/generating text (Llama 3.1 8B) |
| **LPU** | Language Processing Unit — Groq's custom hardware for LLM inference |
| **MiniLM** | Lightweight sentence transformer model — generates 384-dim text embeddings |
| **Named Vector** | Qdrant feature allowing multiple vector spaces per collection point |
| **NSFW** | Not Safe For Work — content that may be inappropriate |
| **OCR** | Optical Character Recognition — extracting text from images (Tesseract) |
| **ORM** | Object-Relational Mapping — Prisma maps database tables to code objects |
| **P50/P95** | Percentile latency — P50 = median, P95 = 95th percentile |
| **PII** | Personally Identifiable Information — user data that must not be logged |
| **Pydantic** | Python library for data validation using type annotations |
| **Qdrant** | Vector database — stores and searches meme embeddings |
| **R2** | Cloudflare R2 — S3-compatible object storage for media files |
| **RAG** | Retrieval-Augmented Generation — pattern of retrieving relevant data to augment AI output |
| **RBAC** | Role-Based Access Control — authorization model (Phase 3) |
| **Redis** | In-memory key-value store — used for caching search results |
| **Slug** | URL-safe identifier (e.g., `this-is-fine` for "This Is Fine") |
| **SSR** | Server-Side Rendering — page rendered on server before sending to client (used for SEO) |
| **Supabase** | Open-source Firebase alternative — provides PostgreSQL hosting |
| **Token Bucket** | Rate limiting algorithm — allows burst traffic within limits |
| **Upstash** | Serverless Redis provider — MemeGPT's cache service |
| **Vector** | Array of numbers representing text/image semantics in embedding space |
| **Vector Space** | Mathematical space where semantically similar items are close together |
| **WebP** | Modern image format — smaller files, used for thumbnails |

---

> **Related Documents:**
> - [16_References/Technology_Stack.md](../16_References/Technology_Stack.md) — Tech stack details
> - [02_Project_Architecture/Architecture_Decisions.md](../02_Project_Architecture/Architecture_Decisions.md) — Why decisions were made
