# MemeGPT — 100% FastAPI + React AI Meme Engine

Turn life situations into the perfect meme. **100% Python FastAPI backend, 100% local, runs offline.**

- **Backend:** Python FastAPI (`backend/app/main.py`)
- **Frontend:** React (Vite) (`frontend/src/`)
- **Database:** SQLite via SQLAlchemy (`backend/memegpt.db`)
- **AI Engine:** Rule matcher + TF-IDF semantic vector search (+ optional `sentence-transformers` embeddings)

---

## Quick Start

### 1. Backend Setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
python seed.py
```

Optional (generate/cache transformer embeddings):
```bash
python generate_embeddings.py
```

Start FastAPI API server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (React)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

### Or run both from root:

```bash
npm install
npm run setup          # pip install + seed SQLite DB
npm run dev            # FastAPI :8000 + React :5173
```

---

## Features

| Feature | Tab / Endpoint | Description |
|---------|----------------|-------------|
| **AI Situation Matcher** | 🎭 Analyze | Input any scenario → get top match, top 5, alternatives, gifs, viral picks |
| **Full Meme Search** | 🔍 Search | Paged search by name, catchphrase, or category filter |
| **Trending & Popularity** | 🔥 Trending | Real-time ranks based on usage & community upvotes |
| **Favorites Collection** | ❤️ Favorites | Save memes locally & persist across sessions in SQLite |
| **System Analytics** | 📊 Stats | System dashboard (meme count, total searches, votes, avg latency) |
| **Admin Controls** | ⚙️ Admin | Add new memes or remove entries from database |
| **Export Options** | 📄 Export | Export match results to TXT, JSON, or Markdown |

---

## FastAPI API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Run rule + semantic engine matching |
| `GET` | `/api/memes` | Search & list memes (paged) |
| `GET` | `/api/memes/{id}` | Get meme details |
| `GET` | `/api/trending` | Get top trending memes |
| `GET` | `/api/categories` | Get category list |
| `GET` | `/api/favorites` | Get saved favorites for session |
| `POST` | `/api/favorites/toggle` | Toggle favorite state for a meme |
| `POST` | `/api/vote` | Upvote (+1) or Downvote (-1) a meme |
| `POST` | `/api/admin/memes` | Add new meme |
| `DELETE` | `/api/admin/memes/{id}` | Delete meme |
| `POST` | `/api/export` | Export result as TXT / JSON / Markdown |
| `GET` | `/api/stats` | System usage & performance metrics |
| `GET` | `/api/health` | FastAPI health check & total count |

---

## Project Structure

```text
meme gpt/
├── backend/                  # 🐍 100% Python FastAPI Backend
│   ├── app/
│   │   ├── config.py         # Config & logging
│   │   ├── database.py       # SQLAlchemy SQLite models & sanitization
│   │   ├── main.py           # FastAPI routes & CORS setup
│   │   ├── meme_matcher.py   # AI scoring & match aggregator
│   │   ├── rule_engine.py    # Pattern & tag rule engine
│   │   └── semantic_search.py# TF-IDF + SentenceTransformers vector engine
│   ├── data/                 # Meme dataset & embeddings
│   ├── seed.py               # Seed 520+ memes into SQLite
│   └── requirements.txt
├── frontend/                 # ⚛️ React + Vite Frontend
│   ├── src/
│   │   ├── api.ts            # FastAPI HTTP client
│   │   ├── App.tsx           # React UI with 6 tabs & toast notifications
│   │   └── index.css         # Glassmorphism dark design system
│   └── package.json
└── package.json              # Monorepo runner
```

---

## Example Test Query

**Input:**
```text
I worked for 3 months on a project and accuracy is only 12%. Can you make it 100%?
```

**Expected Top Matches:**
- **Khwab Dekho Raat Bhar**
- **Aukat Me Reh**
- **12% Accuracy Fix**
