# MemeGPT — Installation Guide

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01  
> **Related Documents:** [Prerequisites.md](./Prerequisites.md) · [Environment_Variables.md](./Environment_Variables.md) · [Quick_Start.md](./Quick_Start.md)

---

## Purpose

Step-by-step installation guide for setting up the complete MemeGPT development environment from scratch.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/memegpt.git
cd memegpt
```

---

## Step 2: Install Frontend Dependencies

```bash
# From project root
npm install
```

This installs dependencies for the root workspace and the `frontend/` package (configured via npm workspaces in `package.json`).

---

## Step 3: Set Up Python Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Return to project root
cd ..
```

### Backend Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.111.0 | API framework |
| `uvicorn[standard]` | 0.29.0 | ASGI server |
| `pydantic` | 2.7.0 | Request/response validation |
| `sentence-transformers` | 3.0.0 | MiniLM text embeddings |
| `transformers` | 4.40.0 | CLIP, BLIP, emotion models |
| `torch` | 2.3.0 (CPU) | ML runtime |
| `Pillow` | 10.3.0 | Image processing |
| `pytesseract` | 0.3.10 | OCR text extraction |
| `qdrant-client` | 1.9.0 | Vector database client |
| `supabase` | 2.4.0 | PostgreSQL client |
| `redis` | 5.0.4 | Cache client |
| `httpx` | 0.27.0 | Async HTTP client |
| `groq` | 0.9.0 | Groq LLM API client |

---

## Step 4: Configure Environment Variables

```bash
# Copy the example environment file
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env and fill in your API keys
```

See [Environment_Variables.md](./Environment_Variables.md) for the complete reference of all required variables.

**Minimum required for local development:**

```env
DATABASE_URL="file:./memegpt.db"
GROQ_API_KEY=gsk_your_groq_api_key_here
```

---

## Step 5: Initialize the Database

```bash
# From project root — seed the SQLite database with sample memes
npm run seed
```

This runs `backend/seed.py` which:
1. Creates the SQLite database (`backend/memegpt.db`)
2. Populates it with sample meme data
3. Sets up initial categories and metadata

---

## Step 6: Generate Embeddings (Optional for Dev)

```bash
# Generate text embeddings for all memes in the database
npm run embeddings
```

This runs `backend/generate_embeddings.py` which:
1. Loads the MiniLM-L6-v2 model (~80MB, downloaded on first run)
2. Generates 384-dimensional embeddings for each meme's text
3. Stores embeddings in the local database

> [!NOTE]
> First run will download the MiniLM model (~80MB). Subsequent runs use the cached model.

---

## Step 7: Start Development Servers

### Option A: Start Both Together (Recommended)

```bash
# From project root
npm run dev
```

This uses `concurrently` to start both servers:
- **Backend** at `http://localhost:8000` (FastAPI + Uvicorn)
- **Frontend** at `http://localhost:5173` (Vite dev server)

### Option B: Start Separately

```bash
# Terminal 1 — Backend
npm run dev:backend
# Or manually:
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
npm run dev:frontend
# Or manually:
cd frontend && npm run dev
```

---

## Step 8: Verify Installation

### Backend Verification

Open `http://localhost:8000/docs` in your browser. You should see the FastAPI Swagger UI with all available endpoints.

Test the health endpoint:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### Frontend Verification

Open `http://localhost:5173` in your browser. You should see the MemeGPT web interface with a search box.

### End-to-End Verification

1. Type a query like "when your code works first try" in the search box
2. Click "Find Meme" (or press Enter)
3. Verify that meme results appear
4. Try the copy and download buttons

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError` in Python | Virtual environment not activated | Run `.\venv\Scripts\Activate.ps1` (Windows) |
| `ENOENT: no such file or directory` | Dependencies not installed | Run `npm install` from project root |
| Port 8000 already in use | Another process on the port | Kill the process or use `--port 8001` |
| Port 5173 already in use | Another Vite instance running | Kill existing process |
| Model download fails | Network/firewall issue | Check internet, try manual HuggingFace download |
| `pytesseract.TesseractNotFoundError` | Tesseract not installed | See [Prerequisites.md](./Prerequisites.md) |
| `DATABASE_URL` error | Missing .env file | Copy `.env.example` to `.env` |

### Reset Development Environment

```bash
# Full reset
rm -rf node_modules frontend/node_modules backend/venv backend/memegpt.db
npm install
cd backend && python -m venv venv && pip install -r requirements.txt
cd .. && npm run seed
```

---

## Project Structure After Installation

```
memegpt/
├── .env                    # Your environment variables
├── .env.example            # Template for environment variables
├── package.json            # Root workspace configuration
├── tsconfig.json           # TypeScript configuration
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Database operations
│   │   ├── meme_matcher.py # Meme matching logic
│   │   ├── rule_engine.py  # Rule-based scoring
│   │   └── semantic_search.py # Vector search
│   ├── data/               # Meme data files
│   ├── memegpt.db          # SQLite database (after seed)
│   ├── requirements.txt    # Python dependencies
│   ├── seed.py             # Database seeder
│   └── generate_embeddings.py # Embedding generator
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main application component
│   │   ├── api.ts          # API client
│   │   ├── index.css       # Global styles
│   │   ├── main.tsx        # React entry point
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # Utility libraries
│   │   └── types/          # TypeScript type definitions
│   ├── index.html          # HTML template
│   ├── vite.config.ts      # Vite configuration
│   └── package.json        # Frontend dependencies
├── prisma/
│   ├── schema.prisma       # Database schema
│   └── seed.ts             # Prisma seeder
├── server/
│   └── src/                # Node.js server
├── scripts/
│   └── generate_embeddings.py # Embedding generation script
└── node_modules/           # Dependencies (gitignored)
```

---

> **Next Document:** [Environment_Variables.md](./Environment_Variables.md) — Complete environment variable reference.
