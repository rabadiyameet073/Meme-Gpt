# MemeGPT

Turn life situations into the perfect meme. **100% free, runs locally.**

- **Frontend:** React (Vite) — basic UI, improve later
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **AI:** Rule engine + local semantic search (+ optional sentence-transformers embeddings)

## Quick start

### 1. Backend setup

```bash
cd backend
pip install -r requirements.txt
python seed.py
```

Optional (better semantic search):

```bash
python generate_embeddings.py
```

Start API:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

### Or run both from root

```bash
npm install
npm run setup          # pip install + seed DB
npm run dev            # API :8000 + React :5173
```

## Features

| Feature | Status |
|---------|--------|
| Situation input | Chat tab |
| Top 5 memes + alternatives | Chat results |
| Confidence scores | % on each meme |
| Explanation | Auto-generated |
| Categories | Rule engine |
| Trending / votes / usage | SQLite |
| Admin panel | Add/delete memes |
| Search | By name, dialogue, category |
| Export | TXT, JSON, Markdown |

## API (FastAPI)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyze` | Match memes to situation |
| GET | `/api/memes` | Search memes |
| GET | `/api/trending` | Trending memes |
| POST | `/api/admin/memes` | Add meme |
| DELETE | `/api/admin/memes/{id}` | Delete meme |
| POST | `/api/export` | Export results |
| GET | `/api/health` | Health check |

## Project structure

```
meme gpt/
├── backend/
│   ├── app/           # FastAPI + AI pipeline
│   ├── data/          # Meme dataset + embeddings
│   ├── seed.py        # Seed 500+ memes
│   └── requirements.txt
├── frontend/
│   └── src/           # React app (basic UI)
└── package.json       # Run both servers
```

## Testing example

Input:
```
I worked for 3 months on a project and accuracy is only 12%. Can you make it 100%?
```

Expected memes: **Khwab Dekho Raat Bhar**, **Aukat Me Reh**, **12% Accuracy Fix**

## Notes

- No paid APIs, no cloud — everything local
- UI is intentionally minimal — customize `frontend/src/` later
- Embeddings use `all-MiniLM-L6-v2` via sentence-transformers (optional)
