# MemeGPT — Deployment, Launch & Growth Strategy
> Everything you need to go from code on your laptop to live product in users' hands.

---

## 🏗️ Infrastructure Map (All Free)

```
┌─────────────────────────────────────────────────────────────────┐
│                     DOMAIN & CDN                                 │
│          Cloudflare (Free) — DNS, SSL, DDoS protection          │
│     memegpt.app  →  Vercel      api.memegpt.app  →  Render      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┴─────────────────┐
          │                                   │
┌─────────▼──────────┐            ┌───────────▼───────────┐
│  FRONTEND (Vercel) │            │  BACKEND (Render.com)  │
│                    │            │                         │
│  memegpt.app       │◄──────────►│  FastAPI + Uvicorn     │
│  Next.js landing   │   API      │  Python 3.11            │
│                    │   calls    │  512MB RAM              │
│  app.memegpt.app   │            │  0.1 CPU (free tier)   │
│  Next.js web app   │            └────────────┬────────────┘
│                    │                         │
│  Vercel CDN        │            ┌────────────▼────────────┐
│  (Auto-scaled)     │            │      DATA SERVICES       │
└────────────────────┘            │                         │
                                  │  Qdrant Cloud (vectors) │
┌────────────────────┐            │  Supabase (metadata)    │
│  MEDIA STORAGE     │            │  Upstash Redis (cache)  │
│  Cloudflare R2     │            └─────────────────────────┘
│  10GB free         │
│  CDN: cdn.memegpt  │
└────────────────────┘
```

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Set Up Cloudflare (Day 1)
```
1. Buy domain: memegpt.app (Namecheap ~$12/yr)
   Alternative free: use a subdomain on a free domain registrar

2. Go to cloudflare.com → Add site → Choose FREE plan

3. Update your domain's nameservers to Cloudflare's nameservers

4. In Cloudflare DNS, add:
   Type  Name    Content               Proxy
   CNAME  @      cname.vercel-dns.com  ✅ (proxied)
   CNAME  app    cname.vercel-dns.com  ✅ (proxied)
   CNAME  api    your-render-app.onrender.com  ✅ (proxied)
   CNAME  cdn    your-bucket.r2.cloudflarestorage.com  ✅

5. Enable in Cloudflare settings:
   - Always HTTPS: ON
   - Minimum TLS Version: 1.2
   - Auto Minify: JS + CSS + HTML
   - Browser Cache TTL: 1 day
```

### Step 2: Set Up Qdrant Cloud
```
1. Go to cloud.qdrant.io
2. Click "Create cluster" → Choose FREE tier (1GB, 1 cluster)
3. Choose region: us-east-1 (closest to Render free tier)
4. Copy your cluster URL and API key
5. Set environment variable: QDRANT_URL and QDRANT_API_KEY

# Run collection creation (ONE TIME):
cd backend
python -c "from scripts.setup_qdrant import create_meme_collection; create_meme_collection()"
```

### Step 3: Set Up Supabase
```
1. Go to supabase.com → New Project
2. Choose a region (match with Render region)
3. Copy: Project URL, anon key, service role key
4. Go to SQL Editor → paste schema from 04_DESIGN doc → Run
5. Set environment variables accordingly
```

### Step 4: Set Up Upstash Redis
```
1. Go to upstash.com → Create Database
2. Choose: Redis → Free tier → us-east-1 region
3. Copy Redis URL (starts with redis://)
4. Set REDIS_URL environment variable
```

### Step 5: Set Up Cloudflare R2 (Media Storage)
```
1. Cloudflare Dashboard → R2 → Create Bucket
2. Bucket name: memegpt-media
3. Go to R2 Settings → Create API Token → Read+Write permissions
4. Copy: Access Key ID, Secret Access Key
5. Configure public access:
   R2 → memegpt-media → Settings → Public Access → Enable
   Set custom domain: cdn.memegpt.app

# Test upload:
aws s3 cp test.gif s3://memegpt-media/ \
  --endpoint-url https://ACCOUNT_ID.r2.cloudflarestorage.com
```

### Step 6: Deploy Backend to Render
```
1. Go to render.com → New → Web Service
2. Connect your GitHub repository
3. Settings:
   - Name: memegpt-api
   - Root Directory: backend
   - Environment: Python
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   - Plan: FREE

4. Add all environment variables in Render dashboard:
   QDRANT_URL, QDRANT_API_KEY, SUPABASE_URL, SUPABASE_KEY,
   REDIS_URL, GROQ_API_KEY, GIPHY_API_KEY, REDDIT_CLIENT_ID,
   REDDIT_CLIENT_SECRET, CLOUDFLARE_R2_ACCESS_KEY, etc.

5. Click Deploy!

⚠️ Render Free Tier Note:
   - Service sleeps after 15 minutes of inactivity
   - Solution: Set up a cron job to ping /api/v1/health every 10 minutes
   - Use cron-job.org (free) or UptimeRobot (free) for this

# Add to UptimeRobot:
Monitor Type: HTTP(s)
URL: https://api.memegpt.app/api/v1/health
Interval: every 5 minutes
Alert: email if down (free)
```

### Step 7: Deploy Frontend to Vercel
```
1. Go to vercel.com → Add New Project
2. Import your GitHub repo
3. Configure:
   - Framework: Next.js (auto-detected)
   - Root Directory: apps/web
   - Build Command: pnpm build
   - Output Directory: .next

4. Add environment variables:
   NEXT_PUBLIC_API_URL=https://api.memegpt.app

5. Add custom domain: app.memegpt.app

6. Deploy!

# Landing site (same steps but):
   - Root Directory: apps/landing
   - Custom domain: memegpt.app
```

### Step 8: Deploy Mobile App

#### Android (Google Play Store)
```bash
# 1. Install EAS CLI
npm install -g eas-cli

# 2. Log in to Expo account (free)
eas login

# 3. Configure EAS (in apps/mobile/)
eas build:configure

# 4. Build for Android
eas build --platform android --profile production

# 5. Submit to Play Store
# - Create Google Play Console account ($25 one-time fee)
# - Create new app
# - eas submit --platform android
```

#### iOS (Apple App Store)
```bash
# 1. Build for iOS
eas build --platform ios --profile production

# 2. Submit (requires Apple Developer account — $99/year)
eas submit --platform ios
```

#### eas.json
```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "apk",
        "gradleCommand": ":app:bundleRelease"
      },
      "ios": {
        "distribution": "store"
      }
    }
  },
  "submit": {
    "production": {
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "production"
      }
    }
  }
}
```

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

### `.github/workflows/deploy.yml`
```yaml
name: Deploy MemeGPT

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: 9
      - run: pnpm install
      - run: pnpm run test
      - run: pnpm run build

  # Render and Vercel auto-deploy on push to main
  # No manual deploy step needed — they hook into GitHub directly
  
  notify:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: success()
    steps:
      - name: Deployment successful
        run: echo "✅ All tests passed. Vercel and Render will auto-deploy."
```

---

## 🔍 SEO Implementation Checklist

### Next.js SEO Setup
```tsx
// app/layout.tsx — Global metadata
import { Metadata } from 'next';

export const metadata: Metadata = {
  metadataBase: new URL('https://memegpt.app'),
  title: {
    default: 'MemeGPT — Find the Perfect Meme for Anything',
    template: '%s | MemeGPT'
  },
  description: 'AI-powered meme search engine. Type anything, get the perfect meme instantly. GIFs, images, and videos.',
  keywords: ['meme finder', 'ai meme', 'gif search', 'meme gpt', 'find meme by description'],
  openGraph: {
    type: 'website',
    url: 'https://memegpt.app',
    siteName: 'MemeGPT',
    images: [{ url: '/og-image.png', width: 1200, height: 630 }]
  },
  twitter: {
    card: 'summary_large_image',
    creator: '@memegpt'
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true }
  }
};
```

### Sitemap Generation
```tsx
// app/sitemap.ts
import { MetadataRoute } from 'next';

export default function sitemap(): MetadataRoute.Sitemap {
  const categories = [
    'programming', 'relationships', 'work', 'food',
    'gaming', 'monday', 'motivation', 'weekend'
  ];
  
  const categoryPages = categories.map(cat => ({
    url: `https://memegpt.app/memes/${cat}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.8
  }));
  
  return [
    { url: 'https://memegpt.app', priority: 1.0 },
    { url: 'https://memegpt.app/features', priority: 0.9 },
    { url: 'https://memegpt.app/api', priority: 0.7 },
    { url: 'https://memegpt.app/blog', priority: 0.6 },
    ...categoryPages
  ];
}
```

### Structured Data (Schema.org)
```tsx
// Add to app/page.tsx
const structuredData = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "MemeGPT",
  "description": "AI-powered meme recommendation engine",
  "url": "https://app.memegpt.app",
  "applicationCategory": "EntertainmentApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "operatingSystem": "Web, iOS, Android"
};

// In component:
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
/>
```

### Core Web Vitals Checklist
```
✅ LCP (Largest Contentful Paint) < 2.5s
   → Next.js Image component with priority prop for above-fold images
   → Preload critical fonts
   → CDN for all static assets (Cloudflare)

✅ CLS (Cumulative Layout Shift) < 0.1
   → Always set width + height on images
   → Use aspect-ratio CSS for meme cards
   → Reserve space for dynamic content

✅ INP (Interaction to Next Paint) < 200ms
   → No heavy JavaScript on main thread
   → Use React.memo for MemeCard components
   → Debounce search input (300ms)
```

---

## 📊 Monitoring & Observability (All Free)

### Error Tracking — Sentry
```typescript
// apps/web/sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,  // 10% sampling (stay in free tier)
  environment: process.env.NODE_ENV,
});
```

### Product Analytics — PostHog
```typescript
// Track key events
posthog.capture('meme_searched', {
  query_length: query.length,
  format_filter: filter,
  result_count: results.length
});

posthog.capture('meme_copied', {
  meme_id: meme.id,
  meme_format: meme.format,
  result_position: position
});

posthog.capture('meme_downloaded', {
  meme_id: meme.id,
  download_format: format
});
```

### Uptime Monitoring — UptimeRobot (Free)
- Monitor: `https://api.memegpt.app/api/v1/health` every 5 min
- Monitor: `https://memegpt.app` every 5 min
- Alert: email + SMS if down > 2 min

### Performance Monitoring
- **Vercel Analytics** (built-in, free): Web Vitals dashboard per page
- **Render Metrics** (built-in, free): CPU, Memory, Response time graphs

---

## 🎯 Pre-Launch Checklist

### Technical (Week Before Launch)
```
□ All environment variables set in production
□ Health check endpoint returns 200
□ Search returns results in < 2 seconds
□ Copy button works in Chrome, Firefox, Safari
□ Download works (GIF, PNG formats)
□ Mobile app runs on both iOS simulator and Android emulator
□ No console errors in production
□ SSL certificates valid (Cloudflare handles this)
□ Sitemap accessible at memegpt.app/sitemap.xml
□ Robots.txt in place
□ OG image renders correctly (test with opengraph.xyz)
□ 100K memes indexed in Qdrant
□ Redis cache working (test /health?cache=true)
□ Error reporting active (trigger a test error in Sentry)
□ Analytics active (verify PostHog receiving events)
□ UptimeRobot monitoring configured
□ Render keep-alive ping configured (cron-job.org)
```

### Content (Week Before Launch)
```
□ Landing page copywriting complete
□ 5 category pages live (/memes/programming, etc.)
□ Blog post: "Introducing MemeGPT"
□ App Store screenshots (6 screenshots for iOS)
□ Google Play screenshots (8 screenshots for Android)
□ App Store preview video (30 seconds)
□ Social media accounts created (@memegpt on Twitter/X, Instagram)
□ Demo video recorded (screen recording, no editing needed for launch)
```

---

## 📣 Launch Strategy (Solo Founder Playbook)

### Day 1: Soft Launch (Friends + Family)
- Share link in WhatsApp groups
- Goal: 50 users, find obvious bugs
- Fix bugs same day

### Week 1: Community Launch
```
Reddit posts (most important for meme product):
  - r/InternetIsBeautiful: "I made an AI meme search engine"
  - r/memes: "Tired of not finding the right meme? I built this"
  - r/SideProject: Show HN-style post
  - r/webdev: Technical post about the ML approach

Product Hunt:
  - Schedule for Tuesday-Thursday (highest traffic)
  - Collect hunters: find active PH hunters on their website
  - Prepare: tagline, gallery images, first comment
  - Goal: Top 5 Product of the Day

Twitter/X:
  - Post demo GIF (show the wow moment: type → perfect meme)
  - Tag relevant accounts: @ProductHunt, meme pages
  - Use hashtags: #buildinpublic #indiedev #AI #memes

LinkedIn:
  - Technical journey post: "How I built MemeGPT alone in 2 months"
  - Describe the ML approach (developers love this)
```

### Week 2-4: Sustained Growth
```
Content Strategy (SEO + organic):
  - Weekly blog posts: "Top 10 memes for [specific situation]"
  - Each post auto-generated using your own API
  - Target: "best memes for [x]" keywords with low competition

Community Building:
  - Discord server for power users + developers
  - Weekly "Meme of the Week" post on Twitter
  - Reply to everyone who mentions MemeGPT

Developer Growth:
  - Post about free API in r/webdev, r/programming
  - Share API docs on HackerNews Show HN
  - Create simple CodePen demos using the API
```

---

## 📱 App Store Optimization (ASO)

### Google Play Store
```
App Name: MemeGPT - AI Meme Finder (50 chars max)
Short Description: Find the perfect meme for anything, instantly (80 chars)
Long Description: 4000 chars — include all keywords naturally

Keywords to include in description:
meme finder, gif search, ai meme, reaction gif, meme generator,
funny memes, meme app, best memes, meme search engine

Category: Entertainment
Content Rating: Everyone (or Teen if you allow edgy content)
```

### Apple App Store
```
App Name: MemeGPT (30 chars max)
Subtitle: AI Meme Finder & GIF Search (30 chars max)
Keywords field (100 chars): meme,gif,funny,reaction,ai,search,finder,humor,viral,image
```

---

## 🔄 Ongoing Data Pipeline (Weekly Cron Job)

Set up this script to run every Sunday at 2am (GitHub Actions scheduled):

```yaml
# .github/workflows/weekly-index.yml
name: Weekly Meme Indexing

on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 2am UTC
  workflow_dispatch:       # Allow manual trigger

jobs:
  index-new-memes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - name: Collect new memes from Reddit
        run: python backend/scripts/01_collect_reddit.py --limit 500
        env:
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
      - name: Generate embeddings and index
        run: python backend/scripts/05_generate_embeddings.py && python backend/scripts/06_index_to_qdrant.py
        env:
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
          QDRANT_API_KEY: ${{ secrets.QDRANT_API_KEY }}
```

This adds ~500 fresh memes per week automatically, keeping the database current.

---

## 💡 Scaling Plan (When You Hit Free Tier Limits)

| When | Upgrade | Monthly Cost |
|---|---|---|
| >1GB vectors in Qdrant | Qdrant Cloud Starter | $25/mo |
| >750hr/mo compute on Render | Render Starter | $7/mo |
| >10GB media storage | Cloudflare R2 (pay as you go) | ~$5/mo |
| >10K Redis ops/day | Upstash Pro | $10/mo |
| >500MB Supabase DB | Supabase Pro | $25/mo |
| **Total at scale** | | **~$72/mo** |

You can support roughly **100K daily active users** before hitting $100/month. 
By that point, monetization (ads, API subscriptions, Pro tier) easily covers costs.

---

## 🎉 You're Ready to Ship!

```
Timeline for Solo Developer:
─────────────────────────────────────────────────────
Week 1-2:   Set up infrastructure, collect 50K memes, 
            get backend search working
            
Week 3-4:   Build web app, polish UI, write tests

Week 5-6:   Build mobile app (reuses most web logic)

Week 7:     Build landing site, write landing copy

Week 8:     SEO setup, app store submission, soft launch

Week 9-10:  Fix launch bugs, Product Hunt prep

Week 10:    🚀 LAUNCH DAY
─────────────────────────────────────────────────────
Total: 10 weeks solo development  (working nights + weekends)
Total cost: $25 (domain) + $99 (Apple Dev) = $124 one-time
Monthly cost: $0 until scale
```

---

*Document Version: 1.0 | Last Updated: 2026 | Owner: Founder*
