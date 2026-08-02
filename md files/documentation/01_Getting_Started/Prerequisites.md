# MemeGPT — Prerequisites

> **Document Version:** 1.0  
> **Last Updated:** 2026-08-01  
> **Related Documents:** [Installation.md](./Installation.md) · [Environment_Variables.md](./Environment_Variables.md)

---

## Purpose

This document lists all software, tools, accounts, and API keys required to develop, run, and deploy MemeGPT. Complete this checklist before starting the installation process.

---

## Required Software

### Runtime Environments

| Software | Minimum Version | Purpose | Installation |
|---|---|---|---|
| **Node.js** | 20.x LTS | Frontend build system, server runtime | [nodejs.org](https://nodejs.org) |
| **Python** | 3.11+ | Backend API server, ML pipeline | [python.org](https://python.org) |
| **Git** | 2.40+ | Version control | [git-scm.com](https://git-scm.com) |

### Package Managers

| Tool | Purpose | Installation |
|---|---|---|
| **npm** (bundled with Node.js) | JavaScript package management | Comes with Node.js |
| **pnpm** (recommended) | Faster alternative to npm, workspace support | `npm install -g pnpm` |
| **pip** | Python package management | Comes with Python |
| **venv** | Python virtual environments | Comes with Python 3.3+ |

### Development Tools (Optional but Recommended)

| Tool | Purpose | Installation |
|---|---|---|
| **VS Code** | Code editor with extensions | [code.visualstudio.com](https://code.visualstudio.com) |
| **Docker** | Containerized development | [docker.com](https://docker.com) |
| **Tesseract OCR** | Text extraction from meme images | See platform-specific instructions below |
| **Expo CLI** | Mobile app development | `npm install -g @expo/cli` |

---

## Tesseract OCR Installation

Tesseract is required for the offline meme indexing pipeline (extracting text from meme images).

### macOS
```bash
brew install tesseract
```

### Ubuntu / Debian
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

### Windows
```powershell
# Using Chocolatey
choco install tesseract

# Or download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH after installation
```

### Verify Installation
```bash
tesseract --version
# Expected: tesseract 5.x.x
```

---

## Required Accounts (All Free)

### Cloud Services

| Service | Purpose | Free Tier | Signup URL |
|---|---|---|---|
| **GitHub** | Code hosting, CI/CD | Unlimited public repos | [github.com](https://github.com) |
| **Vercel** | Frontend deployment | 100GB bandwidth/month | [vercel.com](https://vercel.com) |
| **Render.com** | Backend deployment | 750 hrs/month | [render.com](https://render.com) |
| **Railway** | Backend deployment (alternative) | $5/month credit | [railway.app](https://railway.app) |
| **Supabase** | PostgreSQL database | 500MB DB, 2GB bandwidth | [supabase.com](https://supabase.com) |
| **Qdrant Cloud** | Vector database | 1GB storage, 1 cluster | [cloud.qdrant.io](https://cloud.qdrant.io) |
| **Upstash** | Redis cache | 10K commands/day | [upstash.com](https://upstash.com) |
| **Cloudflare** | DNS, CDN, R2 storage | 10GB R2 storage | [cloudflare.com](https://cloudflare.com) |

### API Keys

| API | Purpose | Free Limit | Signup URL |
|---|---|---|---|
| **Groq** | LLM inference (Llama 3.1) | 6K req/day, 30 req/min | [console.groq.com](https://console.groq.com) |
| **Giphy** | GIF meme source | 42 req/hour | [developers.giphy.com](https://developers.giphy.com) |
| **Tenor** (Google) | GIF meme source | 300 req/min | [developers.google.com/tenor](https://developers.google.com/tenor) |
| **Reddit** | Meme data source | 60 req/min | [reddit.com/prefs/apps](https://reddit.com/prefs/apps) |

> [!TIP]
> You don't need ALL API keys to start development. The minimum set is:
> - **Groq API key** (for LLM context parsing)
> - **Qdrant Cloud** credentials (for vector search)
> - Everything else can be mocked or added later.

---

## API Key Setup Instructions

### Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with Google or email
3. Navigate to API Keys
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)

### Reddit API Credentials
1. Go to [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Click "create another app..."
3. Select "script" as the app type
4. Set redirect URI to `http://localhost:8000`
5. Note the `client_id` (below the app name) and `client_secret`

### Qdrant Cloud Setup
1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create account
3. Click "Create Cluster" → Select FREE tier
4. Choose region: `us-east-1` (closest to Render/Railway)
5. Copy: Cluster URL and API Key

### Supabase Setup
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Choose region (match with backend hosting region)
4. Copy: Project URL and `anon` key

### Upstash Redis Setup
1. Go to [upstash.com](https://upstash.com)
2. Create database → Select Redis
3. Choose: Free tier → `us-east-1` region
4. Copy: Redis URL (starts with `redis://` or `rediss://`)

---

## VS Code Recommended Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "prisma.prisma",
    "humao.rest-client",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

---

## Verification Checklist

Run this checklist to verify all prerequisites are installed:

```bash
# Runtime versions
node --version          # Expected: v20.x.x or higher
python --version        # Expected: Python 3.11.x or higher
git --version           # Expected: git version 2.40+ 

# Package managers
npm --version           # Expected: 10.x.x
pip --version           # Expected: pip 24.x

# Optional tools
tesseract --version     # Expected: tesseract 5.x.x
docker --version        # Expected: Docker version 24+
```

- [ ] Node.js 20+ installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Groq API key obtained
- [ ] At least one cloud database account created
- [ ] VS Code (or preferred editor) ready

---

> **Next Document:** [Installation.md](./Installation.md) — Step-by-step installation guide.
