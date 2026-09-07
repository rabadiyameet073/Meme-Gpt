# 08 — Production Deployment Guide
> Deploy MemeGPT to Railway (backend) + Vercel (frontends) + Cloudflare R2 (CDN) with custom domains.

---

## Problem Statement

All deployment configs exist but nothing is actually deployed live:
- ✅ `railway.toml` — configured
- ✅ `Dockerfile` — builds correctly
- ✅ `vercel.json` — exists
- ✅ `.env.example` — comprehensive
- ❌ Not deployed to any platform
- ❌ No custom domain configured
- ❌ No production `.env` values set

---

## Architecture

```
User → memegpt.com (Vercel) ─────────────────→ Next.js Landing + SEO
User → app.memegpt.com (Vercel) ─────────────→ Vite SPA (search app)
User → api.memegpt.com (Railway) ────────────→ FastAPI Backend
CDN  → cdn.memegpt.com (Cloudflare R2) ──────→ Media files (GIF/PNG/MP4)
```

---

## Step 1: Deploy Backend to Railway

### 1.1 Install Railway CLI

```powershell
npm install -g @railway/cli
railway login
```

### 1.2 Initialize Railway Project

```powershell
cd "d:\Meme GPT"
railway init
```

Select "Empty Project" when prompted.

### 1.3 Add Railway Services

```powershell
# Add PostgreSQL
railway add -d postgresql

# Add Redis
railway add -d redis
```

### 1.4 Configure Environment Variables

Go to [railway.app](https://railway.app) → Your Project → Variables tab:

```
# Core
APP_ENV=production
APP_BASE_URL=https://api.memegpt.com
DEBUG=false
LOG_LEVEL=INFO

# Database (auto-set by Railway PostgreSQL plugin)
DATABASE_URL=${{RAILWAY_POSTGRESQL_URL}}

# Groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Qdrant
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key

# Redis (auto-set by Railway Redis plugin)
REDIS_URL=${{REDIS_URL}}

# Cloudflare R2
R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_key
R2_SECRET_KEY=your_secret
R2_BUCKET=memegpt-memes
CDN_BASE_URL=https://cdn.memegpt.com

# Security
SECRET_KEY=generate_a_strong_key_here

# ML Models
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMOTION_MODEL=j-hartmann/emotion-english-distilroberta-base

# CORS
CORS_ORIGINS=https://memegpt.com,https://app.memegpt.com
```

### 1.5 Deploy

```powershell
cd "d:\Meme GPT"
railway up
```

Railway reads `backend/Dockerfile` and `railway.toml` automatically.

### 1.6 Add Custom Domain

In Railway Dashboard → Your Service → Settings → Custom Domain:
- Add `api.memegpt.com`
- Railway gives you a CNAME record
- Add it to your DNS

---

## Step 2: Deploy Vite Frontend to Vercel

### 2.1 Install Vercel CLI

```powershell
npm install -g vercel
vercel login
```

### 2.2 Deploy the Vite SPA

```powershell
cd "d:\Meme GPT\frontend"
vercel --prod
```

When prompted:
- Set up and deploy: **Y**
- Scope: your account
- Link to existing project: **N** (create new)
- Project name: `memegpt-app`
- Build command: `npm run build`
- Output directory: `dist`

### 2.3 Set Environment Variables in Vercel

```powershell
vercel env add VITE_API_URL production
# Enter value: https://api.memegpt.com
```

### 2.4 Add Custom Domain

```powershell
vercel domains add app.memegpt.com
```

---

## Step 3: Deploy Next.js Web to Vercel

```powershell
cd "d:\Meme GPT\apps\web"
vercel --prod
```

When prompted:
- Project name: `memegpt-web`
- Framework: **Next.js** (auto-detected)

### 3.1 Set Environment Variables

```powershell
vercel env add NEXT_PUBLIC_API_URL production
# Enter value: https://api.memegpt.com

vercel env add NEXT_PUBLIC_APP_URL production
# Enter value: https://memegpt.com
```

### 3.2 Add Custom Domain

```powershell
vercel domains add memegpt.com
```

---

## Step 4: Setup Cloudflare R2 CDN

### 4.1 Create R2 Bucket

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. R2 → Create Bucket → Name: `memegpt-memes`
3. Settings → Public Access → Enable public access
4. Note the public URL: `https://pub-xxxxxxxx.r2.dev`

### 4.2 Custom Domain for CDN

1. In Cloudflare Dashboard → R2 → Your Bucket → Settings
2. Custom Domains → Add `cdn.memegpt.com`
3. Cloudflare auto-configures the DNS

### 4.3 Upload Memes to R2

```powershell
cd "d:\Meme GPT"
python scripts/upload_to_r2.py
```

---

## Step 5: Setup Qdrant Cloud

### 5.1 Create Cluster

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create Cluster → Free tier → US East
3. Note the URL and API key

### 5.2 Initialize Collection

```powershell
cd "d:\Meme GPT"
python scripts/create_collection.py
```

### 5.3 Index Memes

```powershell
cd "d:\Meme GPT"
python scripts/index_qdrant.py
```

---

## Step 6: DNS Configuration

Add these DNS records in your domain registrar:

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| CNAME | `@` or `memegpt.com` | `cname.vercel-dns.com` | Next.js landing |
| CNAME | `app` | `cname.vercel-dns.com` | Vite web app |
| CNAME | `api` | `your-service.up.railway.app` | FastAPI backend |
| CNAME | `cdn` | `pub-xxxxxxxx.r2.dev` | Media CDN |

---

## Step 7: Post-Deployment Verification

### 7.1 Health Check

```powershell
curl https://api.memegpt.com/api/v1/health
```

Expected: `{"status": "ok", "database": "connected", ...}`

### 7.2 Test Search

```powershell
curl -X POST https://api.memegpt.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "when the code finally works"}'
```

### 7.3 Test Frontend

Open `https://app.memegpt.com` — should load the Vite SPA and connect to the API.

### 7.4 Test SEO Pages

Open `https://memegpt.com/meme/distracted-boyfriend` — should render SSR meme page.

---

## Step 8: CI/CD Auto-Deploy

### 8.1 Vercel Auto-Deploy

Vercel auto-deploys on git push if connected to GitHub. Connect your repo:
```powershell
vercel git connect
```

### 8.2 Railway Auto-Deploy

Railway auto-deploys on push to `main` branch by default if connected to GitHub.

---

## Verification Checklist

- [ ] `https://api.memegpt.com/api/v1/health` returns 200
- [ ] `https://app.memegpt.com` loads the Vite SPA
- [ ] `https://memegpt.com` loads the Next.js landing page
- [ ] `https://cdn.memegpt.com/images/test.jpg` loads media
- [ ] Search endpoint returns results
- [ ] CORS allows cross-origin from frontends
- [ ] SSL/HTTPS on all subdomains
- [ ] Git push triggers auto-deploy
