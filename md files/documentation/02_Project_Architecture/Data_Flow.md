# MemeGPT — Data Flow

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete data flow documentation — how data moves through MemeGPT in both the **offline pipeline** (indexing) and **online pipeline** (search), including transformations at each stage.

---

## Two Pipelines

MemeGPT has two distinct data pipelines that serve different purposes:

| Pipeline | When | Speed | Purpose |
|---|---|---|---|
| **Offline** | Weekly (cron) | ~30 min for 10K memes | Index new memes, generate embeddings |
| **Online** | Every search request | <1.5 seconds | Search, rank, return results |

---

## Offline Data Flow (Indexing Pipeline)

```mermaid
flowchart TD
    subgraph "Step 1: Data Collection"
        S1["Imgflip API"] --> RAW["data/raw/<br/>10,000+ meme images"]
        S2["Reddit API<br/>(r/memes, r/dankmemes)"] --> RAW
        S3["Tenor/Giphy API<br/>(GIFs)"] --> RAW
    end

    subgraph "Step 2: Preprocessing"
        RAW --> OCR["Tesseract OCR<br/>Extract text from image<br/>'ONE DOES NOT SIMPLY...'"]
        RAW --> BLIP["BLIP Captioning<br/>Generate visual description<br/>'a man pointing at camera'"]
        RAW --> GROQ["Groq LLM<br/>Generate tags/emotions<br/>{emotions, situations, keywords}"]
        OCR --> PROC["data/processed/<br/>Enriched JSON metadata"]
        BLIP --> PROC
        GROQ --> PROC
    end

    subgraph "Step 3: Embedding"
        PROC --> MINILM["MiniLM-L6-v2<br/>Text → 384-dim vector"]
        RAW --> CLIP["CLIP ViT-B/32<br/>Image → 512-dim vector"]
        MINILM --> COMBINE["Weighted Concatenation<br/>text×0.65 + image×0.35<br/>→ 896-dim combined"]
        CLIP --> COMBINE
    end

    subgraph "Step 4: Indexing"
        COMBINE --> QD["Qdrant Cloud<br/>Upsert vectors + payload"]
        PROC --> PG["Supabase PostgreSQL<br/>Insert meme metadata"]
        RAW --> R2["Cloudflare R2<br/>Upload media files"]
    end
```

### Offline Pipeline Duration

| Step | Duration (10K memes) | Bottleneck |
|---|---|---|
| Data collection | ~10 min | API rate limits |
| OCR (Tesseract) | ~15 min | CPU-bound |
| Captioning (BLIP) | ~30 min | GPU/CPU-bound |
| Tag generation (Groq) | ~20 min | API rate limits (30/min) |
| Embedding (MiniLM) | ~2 min | Fast on CPU |
| Embedding (CLIP) | ~10 min | CPU-bound (no GPU) |
| Qdrant upsert | ~5 min | Network I/O |
| R2 upload | ~15 min | Network I/O |
| **Total** | **~60-90 min** | |

---

## Online Data Flow (Search Pipeline)

```mermaid
flowchart LR
    subgraph "Client"
        USER["User types query<br/>'when the code finally works'"]
    end

    subgraph "API Server"
        CACHE{"Redis<br/>Cache hit?"}
        LLM["Groq LLM<br/>Parse intent<br/>(~300ms)"]
        EMO["Emotion Model<br/>Detect emotion<br/>(~100ms)"]
        EMB["MiniLM<br/>Generate embedding<br/>(~50ms)"]
        RANK["Re-ranker<br/>Score + sort<br/>(~10ms)"]
    end

    subgraph "Data Stores"
        QD2["Qdrant<br/>Vector search<br/>(~50ms)"]
        RD2["Redis<br/>Cache result<br/>(~5ms)"]
    end

    USER -->|POST /search| CACHE
    CACHE -->|HIT| RESULT["Return cached<br/>(~15ms)"]
    CACHE -->|MISS| LLM
    CACHE -->|MISS| EMO
    LLM --> EMB
    EMO --> EMB
    EMB --> QD2
    QD2 --> RANK
    RANK --> RD2
    RD2 --> RESULT2["Return fresh<br/>(~560ms)"]
```

---

## Data Transformations

| Stage | Input | Output | Model/Process |
|---|---|---|---|
| OCR | Meme image (PNG/JPG) | Raw text string | Tesseract |
| Captioning | Meme image | Natural language description | BLIP |
| Tagging | Name + OCR + Caption | JSON {emotions, situations, keywords} | Groq LLM |
| Text Embedding | Composed text (name+ocr+tags) | 384-dim float vector | MiniLM |
| Image Embedding | Meme image | 512-dim float vector | CLIP |
| Combination | 384-dim + 512-dim | 896-dim combined vector | Weighted concat |
| Intent Parsing | User query text | JSON {emotion, situation, tone} | Groq LLM |
| Emotion Detection | User query text | {primary, secondary, confidence} | DistilRoBERTa |
| Query Embedding | Enriched query text | 384-dim float vector | MiniLM |
| Vector Search | 384-dim query vector | Top 10 memes + scores | Qdrant HNSW |
| Re-ranking | 10 candidates + metadata | Top 5 ranked results | Python scoring |

---

## Data Storage Summary

| Data | Size per Meme | Total (10K) | Storage |
|---|---|---|---|
| Image file (original) | ~500KB | ~5GB | R2 / local |
| GIF file | ~1MB | ~10GB | R2 |
| WebP thumbnail | ~50KB | ~500MB | R2 |
| Text embedding (384-dim) | 1.5KB | ~15MB | Qdrant |
| Image embedding (512-dim) | 2KB | ~20MB | Qdrant |
| Combined embedding (896-dim) | 3.5KB | ~35MB | Qdrant |
| Metadata JSON | ~2KB | ~20MB | Supabase |
| **Total per meme** | **~1.5MB** | **~15GB** | |

---

## Best Practices

1. **Run offline pipeline on local machine** — not on the production server (saves RAM/CPU)
2. **Keep `data/processed/` directory** — it's your re-indexing source (skip OCR/BLIP/Groq)
3. **Use batch upserts** — 100 points per batch to Qdrant
4. **Cache online results** — 1-hour TTL, >60% hit rate expected
5. **Parallel I/O in online pipeline** — intent parsing + emotion detection run concurrently

---

> **Related Documents:**
> - [Request_Flow.md](./Request_Flow.md) — Detailed request lifecycle
> - [05_AI_System/AI_Pipeline.md](../05_AI_System/AI_Pipeline.md) — Full pipeline code
> - [Folder_Structure.md](./Folder_Structure.md) — Where data files live
