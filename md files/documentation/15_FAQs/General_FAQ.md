# MemeGPT — Frequently Asked Questions

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## General FAQ

### What is MemeGPT?
MemeGPT is an AI-powered meme recommendation engine. You describe a situation, emotion, or context in natural language, and MemeGPT uses AI to find the most relevant memes — no keyword hunting required.

### How is MemeGPT different from Giphy or Google Image Search?
Traditional meme search requires exact keywords ("sad dog meme"). MemeGPT understands natural language — you can type "when your code compiles but the output is completely wrong" and it finds contextually perfect memes. It uses emotion detection, semantic search, and LLM-powered intent parsing.

### Is MemeGPT free?
Yes. The MVP is completely free with no account required. Future Pro tiers may add higher rate limits and exclusive features for $5/month.

### Do I need to create an account?
No. MemeGPT is fully anonymous by default. No login, no signup, no tracking. You can optionally create an account in Phase 3 to sync favorites across devices.

### What meme formats are supported?
GIF, PNG/JPG (static images), MP4 (video), and WebP (stickers). Each meme is available in multiple formats when possible.

### How many memes does MemeGPT have?
MVP launches with ~1,000 curated memes. Phase 2 expands to 5,000, Phase 3 to 25,000, and Phase 4 targets 100,000+ memes.

### Is there a mobile app?
A React Native (Expo) mobile app is planned for Phase 2, targeting both iOS and Android.

### Does MemeGPT work offline?
Not currently. Search requires the backend API. However, the mobile app will cache the last 50 viewed memes for offline access.

---

## Technical FAQ

### What AI models does MemeGPT use?

| Model | Purpose | Size |
|---|---|---|
| MiniLM-L6-v2 | Text embedding (semantic search) | 22MB |
| DistilRoBERTa | Emotion detection | 250MB |
| Llama 3.1 8B (Groq) | Intent parsing | Cloud |
| BLIP | Image captioning (offline) | 446MB |
| CLIP ViT-B/32 | Image embedding (offline) | 400MB |
| Tesseract | OCR text extraction (offline) | 30MB |

### Why FastAPI instead of Express.js?
FastAPI was chosen for:
1. **Python ML ecosystem** — sentence-transformers, transformers, pytorch all run natively
2. **Automatic documentation** — Swagger UI + ReDoc generated from code
3. **High performance** — comparable to Go/Node.js for I/O-bound workloads
4. **Type safety** — Pydantic validation with auto-generated schemas

### Why Qdrant instead of Pinecone?
1. **Generous free tier** — 1GB free (vs Pinecone's starter limits)
2. **Named vectors** — store text, image, combined embeddings separately
3. **Payload filtering** — filter by NSFW, format, category during search
4. **Open source** — can self-host for full control

### Why Groq instead of OpenAI?
1. **Free tier** — 6,000 requests/day (vs OpenAI's pay-per-token)
2. **Speed** — ~200ms inference (vs ~1s for GPT-3.5)
3. **Adequate quality** — Llama 3.1 8B is sufficient for structured JSON extraction
4. **Fallback** — if Groq fails, system degrades gracefully without LLM

### How does the scoring algorithm work?
Each meme gets a composite score (0.0–1.0) from: keyword match (30%), semantic similarity (20%), popularity (20%), emotion match (15%+8%), recency (10%), and format preference (5% bonus). See [03_Backend/Business_Logic.md](../03_Backend/Business_Logic.md).

### What happens if an external service goes down?
MemeGPT degrades gracefully:
- **Groq down** → Skip intent parsing, use raw query embedding (still works, lower quality)
- **Qdrant down** → Return cached results or trending memes
- **Redis down** → Skip cache, process every request fresh
- **All down** → Return trending memes from database

### How do I add new memes?
Currently, memes are added through the offline indexing pipeline:
1. Add meme source data to `datasets/` folder
2. Run `python scripts/preprocess_memes.py`
3. Run `python scripts/generate_embeddings.py`
4. Run `python scripts/index_qdrant.py`

### What is the maximum query length?
2,000 characters. This accommodates multi-line conversation pastes while preventing abuse.

---

## API FAQ

### What is the API rate limit?
- **Free (no key):** 60 requests/minute per IP, 30/minute for search
- **Developer (API key):** 300 requests/minute

### How do I get an API key?
API keys will be available in Phase 2. Sign up at `memegpt.com/developer` with your email.

### Is the API RESTful?
Yes. All endpoints follow REST conventions with JSON request/response bodies, standard HTTP status codes, and versioned URLs (`/api/v1/`).

### Can I use MemeGPT in my Discord bot?
Yes! The REST API can be called from any language. A pre-built Discord bot integration is planned for Phase 3.

### Is there a WebSocket API for real-time?
Not currently. The REST API handles search well since each query is a discrete request. WebSocket support may be added for chat-style refinement in Phase 3.

---

> **Related Documents:**
> - [14_Troubleshooting/Common_Issues.md](../14_Troubleshooting/Common_Issues.md) · [07_APIs/API_Overview.md](../07_APIs/API_Overview.md)
