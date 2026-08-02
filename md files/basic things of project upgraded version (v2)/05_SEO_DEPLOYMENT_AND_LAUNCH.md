# 05 — MemeGPT: SEO, Deployment, Launch & Growth
> Everything from zero to live — deployment configs, SEO playbook, CI/CD, launch strategy, and full cost breakdown.

---

## Part 1: Technical SEO (Next.js)

### Why SEO Matters for MemeGPT
- 10,000+ individual meme pages = 10,000+ Google-indexed pages from day one
- "Drake pointing meme download" gets ~8,000 searches/month — each meme page captures this
- Blog content ("Best Monday Memes 2025") drives organic traffic permanently
- No paid ads needed: SEO compounds over time

---

### 1.1 Root Layout Metadata

```typescript
// apps/web/app/layout.tsx
import type { Metadata, Viewport } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })
const spaceGrotesk = Space_Grotesk({ subsets: ['latin'], variable: '--font-display' })

export const metadata: Metadata = {
  metadataBase: new URL('https://memegpt.com'),
  
  title: {
    default: 'MemeGPT — AI Meme Finder & Recommender',
    template: '%s | MemeGPT'
  },
  description: 'Find the perfect meme for any situation using AI. Type anything — a conversation, a feeling, a situation — and get instant meme recommendations. Download GIF, PNG, or MP4.',
  keywords: [
    'AI meme finder', 'meme recommender', 'meme GPT', 'find a meme',
    'meme generator AI', 'best meme for situation', 'download meme GIF',
    'meme search engine', 'funny meme finder', 'meme AI tool'
  ],
  
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://memegpt.com',
    siteName: 'MemeGPT',
    title: 'MemeGPT — Find the Perfect Meme Instantly with AI',
    description: 'AI-powered meme recommendations. Type anything, get the perfect meme. Download as GIF, PNG, or MP4.',
    images: [{
      url: '/og-image.jpg',
      width: 1200,
      height: 630,
      alt: 'MemeGPT — AI Meme Finder'
    }]
  },
  
  twitter: {
    card: 'summary_large_image',
    site: '@memegpt',
    creator: '@memegpt',
    title: 'MemeGPT — AI Meme Finder',
    description: 'Type anything → get the perfect meme. Download as GIF, PNG, or MP4.',
    images: ['/og-image.jpg']
  },
  
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
    }
  },
  
  verification: {
    google: 'YOUR_GOOGLE_SEARCH_CONSOLE_TOKEN',
  },
  
  alternates: {
    canonical: 'https://memegpt.com',
  },
}

export const viewport: Viewport = {
  themeColor: '#7C3AED',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

---

### 1.2 Individual Meme SEO Pages (The SEO Goldmine)

Each meme gets a fully static page with rich metadata. With 10,000 memes = 10,000 pages.

```typescript
// apps/web/app/meme/[slug]/page.tsx
import type { Metadata } from 'next'
import { getMemeBySlug, getAllMemeSlugs } from '@/lib/api'

// Static generation: build all meme pages at deploy time
export async function generateStaticParams() {
  const slugs = await getAllMemeSlugs()
  return slugs.map(slug => ({ slug }))
}

export async function generateMetadata({ params }): Promise<Metadata> {
  const meme = await getMemeBySlug(params.slug)
  
  return {
    title: `${meme.name} Meme — Download GIF, PNG, MP4`,
    description: `${meme.description}. Download the ${meme.name} meme as GIF, PNG, or MP4. Free download, no watermark.`,
    keywords: [
      `${meme.name} meme`,
      `${meme.name} gif`,
      `${meme.name} download`,
      ...meme.keywords,
      'meme download', 'free meme', 'meme template'
    ],
    openGraph: {
      title: `${meme.name} Meme`,
      description: meme.description,
      images: [{ url: meme.image_url, width: 800, height: 600 }],
      type: 'article',
    },
    alternates: {
      canonical: `https://memegpt.com/meme/${params.slug}`
    }
  }
}

export default async function MemePage({ params }) {
  const meme = await getMemeBySlug(params.slug)
  
  // JSON-LD Structured Data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ImageObject',
    name: `${meme.name} Meme`,
    description: meme.description,
    contentUrl: meme.image_url,
    thumbnailUrl: meme.thumb_url,
    url: `https://memegpt.com/meme/${params.slug}`,
    keywords: meme.keywords.join(', '),
    creator: { '@type': 'Organization', name: 'MemeGPT' }
  }
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {/* Page content */}
      <MemeDetailPage meme={meme} />
    </>
  )
}
```

---

### 1.3 Sitemap Generation (Auto-Updated)

```typescript
// apps/web/app/sitemap.ts
import type { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://memegpt.com'
  
  // Core pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: baseUrl,                    changeFrequency: 'daily',   priority: 1.0 },
    { url: `${baseUrl}/download`,      changeFrequency: 'weekly',  priority: 0.9 },
    { url: `${baseUrl}/features`,      changeFrequency: 'monthly', priority: 0.7 },
    { url: `${baseUrl}/app`,           changeFrequency: 'daily',   priority: 0.9 },
    { url: `${baseUrl}/app/trending`,  changeFrequency: 'hourly',  priority: 0.8 },
    { url: `${baseUrl}/blog`,          changeFrequency: 'daily',   priority: 0.8 },
  ]
  
  // Dynamic meme pages (10,000+ pages)
  const memes = await fetch(`${process.env.API_URL}/api/v1/memes?limit=50000`)
    .then(r => r.json())
  
  const memePages: MetadataRoute.Sitemap = memes.map((meme: any) => ({
    url: `${baseUrl}/meme/${meme.slug}`,
    changeFrequency: 'monthly' as const,
    priority: Math.min(0.9, 0.5 + meme.popularity_score * 0.4),
    lastModified: meme.created_at,
  }))
  
  // Blog pages
  const blogs = await fetch(`${process.env.API_URL}/api/v1/blog`).then(r => r.json())
  
  const blogPages: MetadataRoute.Sitemap = blogs.map((post: any) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    changeFrequency: 'monthly' as const,
    priority: 0.7,
    lastModified: post.published_at,
  }))
  
  return [...staticPages, ...memePages, ...blogPages]
}
```

---

### 1.4 Robots.txt

```typescript
// apps/web/app/robots.ts
import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: '*', allow: '/' },
      { userAgent: '*', disallow: ['/api/', '/app/library', '/_next/'] }
    ],
    sitemap: 'https://memegpt.com/sitemap.xml',
  }
}
```

---

### 1.5 Performance — Core Web Vitals (Must Pass for Google Rankings)

| Metric | Target | Implementation |
|---|---|---|
| **LCP** (Largest Contentful Paint) | < 2.5s | Next.js Image component, CDN thumbnails |
| **FID** (First Input Delay) | < 100ms | No blocking scripts |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Fixed aspect-ratio meme cards |
| **TTFB** (Time to First Byte) | < 600ms | Vercel Edge Network |
| **FCP** (First Contentful Paint) | < 1.8s | Static generation + CDN |

```typescript
// Meme image optimization — always use Next.js Image
import Image from 'next/image'

function MemeCard({ meme }) {
  return (
    <div className="relative aspect-square">  {/* Fixed aspect ratio prevents CLS */}
      <Image
        src={meme.thumb_url}          // WebP thumbnail from CDN (fast)
        alt={meme.alt_text}           // AI-generated alt text (accessibility + SEO)
        fill
        sizes="(max-width: 768px) 50vw, 33vw"
        loading="lazy"                // Lazy load below fold
        placeholder="blur"
        blurDataURL={meme.blur_hash}  // Tiny blur preview while loading
      />
    </div>
  )
}
```

---

### 1.6 SEO Content Strategy

**Content Type 1: Meme Category Pages**
- `/memes/work-memes` — "100 Best Work Memes" (static, auto-generated)
- `/memes/monday-memes` — "50 Funniest Monday Memes"
- `/memes/programming-memes` — "Best Programmer Memes"
- `/memes/relationship-memes` — "Top Relationship Memes"

**Content Type 2: Blog Posts (LLM Auto-Generated Weekly)**
```python
# Generate SEO blog posts automatically every Monday
# Run via GitHub Actions cron

def generate_blog_post(topic: str) -> str:
    trending_memes = get_trending_memes_for_topic(topic)
    
    prompt = f"""
    Write an SEO-optimized blog post titled "Top 20 {topic} Memes of This Week".
    
    Include:
    - 300-word introduction (natural, conversational)
    - 20 meme sections, each with: meme name, why it's funny, when to use it
    - Conclusion with CTA to try MemeGPT
    
    Target keyword: "{topic.lower()} memes"
    Secondary keywords: "funny {topic.lower()}", "best {topic.lower()} memes 2025"
    
    Tone: funny, relatable, internet-native
    """
    return llm_generate(prompt)

# Topics rotated weekly:
BLOG_TOPICS = [
    "Monday Morning", "Work From Home", "Programmer", "Exam Season",
    "Friday Feeling", "Online Gaming", "Relationship", "Cricket Fans",
    "Startup Life", "College Student", "Remote Work", "AI and Tech"
]
```

**Target Keywords by Traffic Potential:**

| Keyword | Monthly Searches | Difficulty | Strategy |
|---|---|---|---|
| meme generator | 450,000 | Very High | Blog posts, meme pages |
| funny memes 2025 | 180,000 | High | Trending meme pages |
| ai meme generator | 40,000 | Medium | Homepage |
| find a meme | 22,000 | Low | Feature page |
| meme gpt | 8,000 | Very Low | Brand keyword |
| download meme gif | 6,000 | Very Low | Meme pages |
| best monday memes | 4,500 | Low | Blog content |
| meme for situation | 2,000 | Very Low | Homepage copy |

---

## Part 2: App Store Optimization (ASO)

### iOS App Store
```
App Name:    MemeGPT – AI Meme Finder
Subtitle:    Find Perfect Meme Instantly

Primary Category:   Entertainment
Secondary Category: Utilities

Keywords (100 chars max):
meme,ai meme,meme finder,funny memes,meme generator,gpt meme,meme download,reaction meme,gif meme

Description (first 2 lines most important):
🤣 Find the PERFECT meme for any situation in seconds using AI!

Just type what's happening — "my boss called at midnight" — and MemeGPT 
finds exactly the right meme. Download as GIF, PNG, or video. Share instantly 
to WhatsApp, Instagram, Slack, or anywhere else.

★ HOW IT WORKS
1. Type anything — a feeling, a situation, a conversation
2. AI finds the best matching meme in 2 seconds
3. Download as GIF, PNG, or MP4 — or copy directly to clipboard
4. Share to any app with one tap

★ FEATURES
• AI-powered meme search — not just keyword matching
• 10,000+ memes and GIFs
• All formats: GIF, PNG, MP4, WebP
• Instant copy to clipboard
• Save favorites to your personal library
• Trending memes updated daily
• Zero ads. Zero watermarks.

App Screenshots Order (5 screens):
1. Home screen with search bar (show the UI)
2. Search result in 2 seconds (show speed)
3. Meme card with download options (show formats)
4. Share sheet (show usability)
5. Library / trending (show value)

Preview Video: 15-30 second screen recording showing the full flow
```

### Google Play Store
```
App Name:   MemeGPT: AI Meme Finder & Download
Short Desc: Type anything → AI finds your perfect meme. Download GIF, PNG, video free!

Category:   Entertainment
Tags:       meme, funny, gif, ai, humor

Full Description:
MEMEGPT uses artificial intelligence to find the perfect meme for any moment.

HOW IT WORKS:
→ Type how you feel: "I finally fixed that bug after 3 days"
→ AI understands your emotion and situation  
→ Get top 5 meme recommendations in under 2 seconds
→ Download as GIF, PNG, or MP4 — completely free

WHY MEMEGPT:
✓ Smarter than search — AI understands context, not just keywords
✓ 10,000+ memes across all categories  
✓ All formats supported: animated GIF, image, video
✓ Copy image directly to clipboard
✓ Trending memes updated every hour
✓ Zero watermarks. Zero forced sign-ups.

PERFECT FOR:
• Responding to group chats
• Finding reaction GIFs
• Content creators and meme page admins  
• Anyone who speaks fluent meme

Feature Graphic: Purple background, "Type anything. Get the perfect meme." + app screenshot
```

---

## Part 3: Deployment

### 3.1 Backend — Railway

```toml
# services/api/railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3

[environments.production]
numReplicas = 1
```

```dockerfile
# services/api/Dockerfile
FROM python:3.11-slim

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download ML models at build time (so startup is instant)
RUN python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('all-MiniLM-L6-v2')
from transformers import pipeline
pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base')
print('Models downloaded successfully')
"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Railway Setup Steps:**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Set environment variables
railway variables set GROQ_API_KEY=gsk_...
railway variables set QDRANT_URL=https://...
railway variables set QDRANT_API_KEY=...
railway variables set SUPABASE_URL=https://...
railway variables set SUPABASE_KEY=...
railway variables set UPSTASH_REDIS_URL=rediss://...
railway variables set CLOUDFLARE_R2_ACCESS_KEY=...
railway variables set CLOUDFLARE_R2_SECRET_KEY=...
railway variables set CLOUDFLARE_R2_BUCKET=memegpt-memes
railway variables set ALLOWED_ORIGINS=https://memegpt.com,https://app.memegpt.com

# 5. Deploy
railway up

# Your API: https://memegpt-production.up.railway.app
```

---

### 3.2 Frontend — Vercel

```json
// apps/web/vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "regions": ["bom1", "sin1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    },
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store" }
      ]
    },
    {
      "source": "/(.*)\\.gif",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/meme/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, s-maxage=3600, stale-while-revalidate=86400" }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/proxy/:path*",
      "destination": "https://api.memegpt.com/api/:path*"
    }
  ]
}
```

**Vercel Setup Steps:**
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy from web folder
cd apps/web
vercel --prod

# 3. Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://api.memegpt.com
NEXT_PUBLIC_CDN_URL=https://cdn.memegpt.com
NEXTAUTH_URL=https://memegpt.com
NEXTAUTH_SECRET=your_random_32_char_secret
GOOGLE_CLIENT_ID=...   # For Google OAuth
GOOGLE_CLIENT_SECRET=...
```

**Custom Domain Setup:**
```
memegpt.com         → Vercel (landing + web app)
app.memegpt.com     → Vercel (same deployment, different subdomain)
api.memegpt.com     → Railway (backend)
cdn.memegpt.com     → Cloudflare R2 (meme files)
```

---

### 3.3 Mobile App — EAS Build (Expo)

```json
// apps/mobile/eas.json
{
  "cli": { "version": ">= 10.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal",
      "channel": "preview"
    },
    "production": {
      "channel": "production",
      "android": {
        "buildType": "apk",
        "gradleCommand": ":app:assembleRelease"
      },
      "ios": {
        "credentialsSource": "remote"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "YOUR_APP_STORE_ID",
        "appleTeamId": "YOUR_TEAM_ID"
      },
      "android": {
        "serviceAccountKeyPath": "./google-services.json",
        "track": "production"
      }
    }
  }
}
```

```json
// apps/mobile/app.json
{
  "expo": {
    "name": "MemeGPT",
    "slug": "memegpt",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "dark",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#0A0A0A"
    },
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "com.memegpt.app",
      "buildNumber": "1",
      "infoPlist": {
        "NSPhotoLibraryAddUsageDescription": "MemeGPT needs access to save memes to your photos."
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#7C3AED"
      },
      "package": "com.memegpt.app",
      "versionCode": 1,
      "permissions": ["WRITE_EXTERNAL_STORAGE", "READ_EXTERNAL_STORAGE"]
    },
    "extra": {
      "apiUrl": "https://api.memegpt.com",
      "cdnUrl": "https://cdn.memegpt.com",
      "eas": { "projectId": "YOUR_EAS_PROJECT_ID" }
    }
  }
}
```

**Mobile Build Commands:**
```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure (run once)
eas build:configure

# Build for testing (internal distribution)
eas build --platform all --profile preview

# Build for production (app stores)
eas build --platform all --profile production

# Submit to app stores
eas submit --platform ios --profile production
eas submit --platform android --profile production

# Push OTA update (no app store review needed for JS changes)
eas update --branch production --message "Fix search latency"
```

---

## Part 4: CI/CD Pipeline (GitHub Actions)

### `.github/workflows/test.yml`
```yaml
name: Run Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── Backend Tests ───────────────────────────────────────────────
  test-backend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd services/api
          pip install -r requirements.txt
          sudo apt-get install -y tesseract-ocr
      
      - name: Run tests
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          QDRANT_URL: ${{ secrets.QDRANT_TEST_URL }}
          QDRANT_API_KEY: ${{ secrets.QDRANT_TEST_API_KEY }}
        run: |
          cd services/api
          pytest tests/ -v --tb=short --timeout=30
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  # ─── Frontend Tests ──────────────────────────────────────────────
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: 'apps/web/package-lock.json'
      
      - name: Install and test
        run: |
          cd apps/web
          npm ci
          npm run type-check    # TypeScript check
          npm run lint          # ESLint
          npm run test          # Jest unit tests
          npm run build         # Ensure it builds
```

### `.github/workflows/deploy.yml`
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:  # Allow manual trigger

jobs:
  # ─── Deploy Backend ──────────────────────────────────────────────
  deploy-api:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          cd services/api
          railway up --service api --detach
      
      - name: Wait for deployment
        run: sleep 30
      
      - name: Health check
        run: |
          curl -f https://api.memegpt.com/api/v1/health || exit 1
          echo "✅ API is healthy"

  # ─── Deploy Frontend ─────────────────────────────────────────────
  deploy-web:
    runs-on: ubuntu-latest
    environment: production
    needs: deploy-api
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Vercel CLI
        run: npm install -g vercel@latest
      
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          cd apps/web
          vercel pull --yes --environment=production
          vercel build --prod
          vercel deploy --prebuilt --prod

  # ─── Notify on Success ───────────────────────────────────────────
  notify:
    runs-on: ubuntu-latest
    needs: [deploy-api, deploy-web]
    if: always()
    
    steps:
      - name: Send Discord notification
        if: ${{ github.event_name == 'push' }}
        run: |
          STATUS="${{ needs.deploy-web.result }}"
          curl -H "Content-Type: application/json" \
               -d "{\"content\": \"🚀 MemeGPT deploy: **$STATUS** — $(date)\"}" \
               ${{ secrets.DISCORD_WEBHOOK_URL }}
```

### `.github/workflows/weekly-ml-update.yml`
```yaml
name: Weekly ML Pipeline Update

on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 2 AM UTC
  workflow_dispatch:

jobs:
  update-meme-database:
    runs-on: ubuntu-latest
    timeout-minutes: 120
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r services/api/requirements.txt
      
      - name: Fetch new trending memes
        env:
          TENOR_API_KEY: ${{ secrets.TENOR_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: python scripts/fetch_new_memes.py --limit 200
      
      - name: Generate embeddings for new memes
        run: python scripts/generate_embeddings.py --new-only
      
      - name: Index new memes in Qdrant
        env:
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
          QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
        run: python scripts/index_qdrant.py --new-only
      
      - name: Update popularity scores
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
          QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
        run: python scripts/update_popularity_scores.py
      
      - name: Generate weekly blog post
        run: python scripts/generate_blog_post.py
      
      - name: Run evaluation
        run: python scripts/evaluate.py --save-report
```

---

## Part 5: Environment Variables (Complete List)

```bash
# ════════════════════════════════════════════
# services/api/.env
# ════════════════════════════════════════════

# AI / LLM
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Backup LLM (if Groq rate limit hit)
GOOGLE_AI_API_KEY=AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Vector Database
QDRANT_URL=https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
QDRANT_COLLECTION=memes

# PostgreSQL (Supabase)
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres

# Cache (Upstash Redis)
UPSTASH_REDIS_URL=rediss://default:xxxxxxxxxxxx@xx-xxx-xxxxx.upstash.io:6379

# File Storage (Cloudflare R2)
CLOUDFLARE_R2_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLOUDFLARE_R2_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLOUDFLARE_R2_BUCKET=memegpt-memes
CLOUDFLARE_R2_ACCOUNT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLOUDFLARE_R2_ENDPOINT=https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.r2.cloudflarestorage.com

# Third-party Data APIs
TENOR_API_KEY=LIVDSRZULELA
IMGFLIP_USERNAME=your_username
IMGFLIP_PASSWORD=your_password
GIPHY_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# App Config
ENVIRONMENT=production
API_VERSION=v1
ALLOWED_ORIGINS=https://memegpt.com,https://app.memegpt.com
MAX_QUERY_LENGTH=2000
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_DAY_ANON=500
RATE_LIMIT_PER_DAY_AUTH=5000
LOG_LEVEL=INFO

# ════════════════════════════════════════════
# apps/web/.env.local
# ════════════════════════════════════════════

NEXT_PUBLIC_API_URL=https://api.memegpt.com
NEXT_PUBLIC_CDN_URL=https://cdn.memegpt.com
NEXT_PUBLIC_APP_URL=https://memegpt.com

# Auth (NextAuth)
NEXTAUTH_URL=https://memegpt.com
NEXTAUTH_SECRET=generate_with_openssl_rand_base64_32

# OAuth Providers (free)
GOOGLE_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxx

# Analytics (Umami — self-hosted or cloud free tier)
NEXT_PUBLIC_UMAMI_URL=https://analytics.umami.is
NEXT_PUBLIC_UMAMI_WEBSITE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Supabase (for client-side auth)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Part 6: Monitoring & Error Tracking

### Error Tracking — Sentry (Free: 5,000 errors/month)

```python
# services/api/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxxxxxxxxx@oXXXXXXX.ingest.sentry.io/XXXXXXX",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of requests tracked
    environment=os.environ.get("ENVIRONMENT", "development"),
    release=os.environ.get("GIT_SHA", "unknown")
)
```

```typescript
// apps/web/app/layout.tsx
import * as Sentry from "@sentry/nextjs"
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
})
```

### Uptime Monitoring — Better Uptime (Free: 3 monitors)
Set up monitors for:
1. `https://memegpt.com` — Landing page
2. `https://api.memegpt.com/api/v1/health` — Backend API
3. `https://cdn.memegpt.com` — CDN

### Analytics Dashboard — Umami
```sql
-- Key metrics to track in Umami
-- (all privacy-first, no cookies, GDPR compliant)

Pageviews per day
Unique visitors per day
Top pages (which meme pages get most traffic)
Search queries (via custom events)
Download events by format
Geographic distribution
Device breakdown (mobile vs desktop)
```

### Custom Metrics Logging
```python
# Track these in your search logs table
{
  "query": "...",
  "latency_ms": 847,
  "cache_hit": false,
  "groq_latency_ms": 312,
  "qdrant_latency_ms": 43,
  "rerank_latency_ms": 8,
  "result_count": 5,
  "top_score": 0.94,
  "model_version": "minilm-v6"
}
```

---

## Part 7: Launch Strategy

### Pre-Launch Checklist

**Technical:**
- [ ] All 5,000+ memes indexed in Qdrant
- [ ] Search returns results for 50 test queries (manually verified)
- [ ] P95 latency < 3 seconds (load tested)
- [ ] Download works for PNG + GIF
- [ ] Copy to clipboard works on Chrome, Safari, Firefox
- [ ] NSFW filter tested and working
- [ ] Mobile app tested on iOS 16+ and Android 12+
- [ ] Sentry error tracking configured
- [ ] Rate limiting configured (60/min unauthenticated)
- [ ] Google Search Console verified
- [ ] Sitemap submitted to Google
- [ ] OG image renders correctly (test with opengraph.xyz)
- [ ] All forms of HTTPS working
- [ ] App store listings complete with screenshots

**Content:**
- [ ] 10 blog posts written and published
- [ ] 500 individual meme SEO pages live
- [ ] FAQ page written
- [ ] Privacy Policy + Terms of Service written

---

### Launch Day Playbook (In This Order)

**Hour 0 — Go Live**
```
1. Merge main → production
2. Verify all services healthy
3. Do one end-to-end test: search → download → share
4. Monitor Sentry for errors
```

**Hour 1 — Community Launch**
```
Post to Reddit (use different accounts or post authentically):
  r/webdev:       "I built MemeGPT — type anything, get the perfect meme"
  r/artificial:   "I used free AI models to build a meme recommender"
  r/memes:        "New tool: describe your situation, AI finds the meme"
  r/SideProject:  "Launched MemeGPT today — here's how I built it alone"

Title formula that works on Reddit:
"I built [PRODUCT] using [TECHNOLOGY]. Here's what I learned."
```

**Hour 2 — Product Hunt**
```
Go live on Product Hunt:
Name: MemeGPT — AI-Powered Meme Finder
Tagline: Type anything. Get the perfect meme. Download as GIF/PNG/MP4.
Topics: Artificial Intelligence, Humor, Design Tools

Ask 10–15 friends/colleagues to upvote first thing in the morning
(Product Hunt ranks by votes in the first few hours)
```

**Hour 3 — Twitter / X**
```
Tweet thread format:
1/ I spent 4 weeks building MemeGPT — an AI meme finder.
   Type anything → get the perfect meme.
   Here's how it works 🧵

2/ The problem: Finding the right meme takes forever. 
   You know the vibe but can't find it.

3/ The solution: Type how you feel → AI understands the emotion 
   and situation → returns top 5 memes in 2 seconds.

4/ Tech stack (all free):
   → Groq (free LLM API) for context parsing
   → MiniLM for text embeddings
   → Qdrant for vector search
   → Next.js + Railway + Vercel

5/ Try it free: memegpt.com
   iOS + Android apps also available.

   RT if you're going to use this 🔁
```

**Day 2 — Dev Community**
```
Post on Dev.to / Hashnode:
Title: "How I Built a Meme Recommendation Engine with Free AI Models"

Article covers:
- The problem
- Vector embeddings explained simply
- Architecture diagram
- Free tools used (Groq, Qdrant, MiniLM, Vercel, Railway)
- Lessons learned building solo
- Link to GitHub (open source the data pipeline at least)
```

**Week 1 — Maintain Momentum**
```
Day 3: Hacker News "Show HN: MemeGPT – type anything, get a meme"
Day 4: LinkedIn post (targeting Product Managers, marketers)
Day 5: Discord communities (r/webdev Discord, Indie Hackers Discord)
Day 6: Respond to all Reddit comments, Product Hunt comments
Day 7: Write launch retrospective blog post on memegpt.com/blog
```

---

## Part 8: Complete Cost Analysis

### Month 0 (Launch — MVP): $0

| Service | Free Limit | Expected Usage | Cost |
|---|---|---|---|
| Vercel | 100GB bandwidth | ~3GB | $0 |
| Railway | $5/month credit | ~$3 | $0 |
| Supabase | 500MB DB | ~50MB | $0 |
| Qdrant Cloud | 1M vectors, 1GB | 10K vectors, 200MB | $0 |
| Cloudflare R2 | 10GB storage | ~2GB | $0 |
| Upstash Redis | 10K req/day | ~3K req/day | $0 |
| Groq API | 6K req/day | ~500 req/day | $0 |
| EAS Build | 30 builds/month | ~5 builds | $0 |
| GitHub Actions | 2,000 min/month | ~300 min | $0 |
| Sentry | 5K errors/month | ~100 errors | $0 |
| **TOTAL** | | | **$0/month** |

---

### Scaling Cost Roadmap

| Users/Month | Daily Searches | Monthly Cost | Action Required |
|---|---|---|---|
| 1,000 | ~200 | **$0** | Stay on free tier |
| 10,000 | ~2,000 | **~$10** | Railway Pro ($5) |
| 50,000 | ~10,000 | **~$40** | Qdrant Starter ($25), Upstash paid |
| 200,000 | ~40,000 | **~$120** | Vercel Pro ($20), Supabase Pro ($25), Railway ($40) |
| 1,000,000 | ~200,000 | **~$400** | Dedicated VPS for ML models |

**Revenue to cover costs:**
- 50 Pro users ($5/month each) = $250/month → covers all costs at 200K user scale
- This is very achievable

---

## Part 9: GitHub Repository Setup

```markdown
# README.md structure

# MemeGPT 🎭
> AI-powered meme recommendation engine. Type anything, get the perfect meme.

[![Deploy Status](badge)] [![License: MIT](badge)] [![Made with ❤️](badge)]

## Demo
[GIF of app in action]

## Features
- AI-powered semantic search (not just keywords)
- 10,000+ memes in GIF, PNG, MP4 formats  
- Copy to clipboard / direct download
- Web app + iOS + Android

## Tech Stack
- **AI:** MiniLM-L6-v2 (embeddings) + Groq Llama 3.1 (context)
- **Vector DB:** Qdrant Cloud
- **Backend:** FastAPI (Python)
- **Frontend:** Next.js 14
- **Mobile:** React Native + Expo
- **Hosting:** Vercel + Railway (free tier)

## Getting Started
[Setup instructions from 02_TECH_STACK.md]

## Architecture
[Link to 04_DESIGN_AND_DEVELOPMENT.md]

## Contributing
[Contribution guidelines]

## License
MIT — free to use and modify
```

**Repository Labels to Create:**
```
bug (red), feature (blue), ml-pipeline (purple),
good-first-issue (green), help-wanted (yellow),
frontend (cyan), backend (orange), mobile (pink)
```

---

## Quick Reference: Important Links to Bookmark

| Service | Sign Up URL | Free Tier Notes |
|---|---|---|
| Groq | https://console.groq.com | 6K req/day, fastest free LLM |
| Qdrant Cloud | https://cloud.qdrant.io | 1GB, 1M vectors free |
| Supabase | https://supabase.com | 500MB PostgreSQL free |
| Railway | https://railway.app | $5 credit/month free |
| Vercel | https://vercel.com | Unlimited deployments free |
| Cloudflare R2 | https://dash.cloudflare.com | 10GB storage free |
| Upstash | https://upstash.com | 10K Redis req/day free |
| Expo EAS | https://expo.dev | 30 app builds/month free |
| Sentry | https://sentry.io | 5K errors/month free |
| HuggingFace | https://huggingface.co/datasets | All datasets free |
| Tenor API | https://developers.google.com/tenor | 300 req/min free |
| Imgflip API | https://imgflip.com/api | Unlimited GET, free |
