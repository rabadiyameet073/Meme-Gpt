# MemeGPT — SEO Strategy (Complete Implementation)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete SEO playbook for MemeGPT — technical SEO implementation in Next.js 14, content strategy, keyword targeting, App Store Optimization (ASO), and structured data markup.

---

## Background — Why SEO is Critical for MemeGPT

- **10,000+ individual meme pages** = 10,000+ Google-indexed pages from day one
- **"Drake pointing meme download"** gets ~8,000 searches/month — each meme page captures this
- **Blog content** ("Best Monday Memes 2025") drives permanent organic traffic
- **No paid ads needed** — SEO compounds over time, free forever
- **Compounding asset** — every new meme page adds to the content flywheel

---

## Technical SEO Implementation (Next.js 14)

### Root Layout Metadata

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
    description: 'AI-powered meme recommendations. Type anything, get the perfect meme.',
    images: [{ url: '/og-image.jpg', width: 1200, height: 630, alt: 'MemeGPT' }]
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
    index: true, follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large', 'max-snippet': -1 }
  },
  verification: { google: 'YOUR_GOOGLE_SEARCH_CONSOLE_TOKEN' },
  alternates: { canonical: 'https://memegpt.com' },
}

export const viewport: Viewport = {
  themeColor: '#7C3AED',
  width: 'device-width',
  initialScale: 1,
}
```

---

### Individual Meme SEO Pages (The SEO Goldmine)

Each meme gets a fully static page with rich metadata, JSON-LD structured data, and download buttons.

```typescript
// apps/web/app/meme/[slug]/page.tsx
import type { Metadata } from 'next'

export async function generateStaticParams() {
  const slugs = await getAllMemeSlugs()
  return slugs.map(slug => ({ slug }))
}

export async function generateMetadata({ params }): Promise<Metadata> {
  const meme = await getMemeBySlug(params.slug)
  return {
    title: `${meme.name} Meme — Download GIF, PNG, MP4`,
    description: `${meme.description}. Download the ${meme.name} meme as GIF, PNG, or MP4. Free, no watermark.`,
    keywords: [
      `${meme.name} meme`, `${meme.name} gif`, `${meme.name} download`,
      ...meme.keywords, 'meme download', 'free meme'
    ],
    openGraph: {
      title: `${meme.name} Meme`,
      description: meme.description,
      images: [{ url: meme.image_url, width: 800, height: 600 }],
      type: 'article',
    },
    alternates: { canonical: `https://memegpt.com/meme/${params.slug}` }
  }
}

export default async function MemePage({ params }) {
  const meme = await getMemeBySlug(params.slug)
  
  // JSON-LD Structured Data (Schema.org)
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
      <script type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <MemeDetailPage meme={meme} />
    </>
  )
}
```

---

### Sitemap Generation (Auto-Updated)

```typescript
// apps/web/app/sitemap.ts
import type { MetadataRoute } from 'next'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://memegpt.com'
  
  const staticPages: MetadataRoute.Sitemap = [
    { url: baseUrl,                   changeFrequency: 'daily',   priority: 1.0 },
    { url: `${baseUrl}/download`,     changeFrequency: 'weekly',  priority: 0.9 },
    { url: `${baseUrl}/features`,     changeFrequency: 'monthly', priority: 0.7 },
    { url: `${baseUrl}/app`,          changeFrequency: 'daily',   priority: 0.9 },
    { url: `${baseUrl}/app/trending`, changeFrequency: 'hourly',  priority: 0.8 },
    { url: `${baseUrl}/blog`,         changeFrequency: 'daily',   priority: 0.8 },
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
  
  return [...staticPages, ...memePages]
}
```

### Robots.txt

```typescript
// apps/web/app/robots.ts
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

## Core Web Vitals (Must Pass for Google Rankings)

| Metric | Target | Implementation |
|---|---|---|
| **LCP** (Largest Contentful Paint) | <2.5s | Next.js Image component, CDN thumbnails |
| **FID** (First Input Delay) | <100ms | No blocking scripts, async hydration |
| **CLS** (Cumulative Layout Shift) | <0.1 | Fixed aspect-ratio meme cards |
| **TTFB** (Time to First Byte) | <600ms | Vercel Edge Network |
| **FCP** (First Contentful Paint) | <1.8s | Static generation + CDN |

```typescript
// Optimized MemeCard image — always use Next.js Image
import Image from 'next/image'

function MemeCard({ meme }) {
  return (
    <div className="relative aspect-square">  {/* Fixed ratio prevents CLS */}
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

## SEO Content Strategy

### Content Type 1: Meme Category Pages

| Page | URL | Target Keyword |
|---|---|---|
| Best Work Memes | `/memes/work-memes` | "work memes" (12K/month) |
| Monday Memes | `/memes/monday-memes` | "monday memes" (8K/month) |
| Programming Memes | `/memes/programming-memes` | "programmer memes" (6K/month) |
| Relationship Memes | `/memes/relationship-memes` | "relationship memes" (5K/month) |

### Content Type 2: Blog Posts (LLM Auto-Generated Weekly)

```python
# Generate SEO blog posts automatically every Monday
# Run via GitHub Actions cron

BLOG_TOPICS = [
    "Monday Morning", "Work From Home", "Programmer", "Exam Season",
    "Friday Feeling", "Online Gaming", "Relationship", "Cricket Fans",
    "Startup Life", "College Student", "Remote Work", "AI and Tech"
]

def generate_blog_post(topic: str) -> str:
    trending_memes = get_trending_memes_for_topic(topic)
    prompt = f"""
    Write an SEO-optimized blog post titled "Top 20 {topic} Memes of This Week".
    
    Include:
    - 300-word introduction (natural, conversational)
    - 20 meme sections, each with: meme name, why it's funny, when to use it
    - Conclusion with CTA to try MemeGPT
    
    Target keyword: "{topic.lower()} memes"
    Tone: funny, relatable, internet-native
    """
    return llm_generate(prompt)
```

---

## Target Keywords by Traffic Potential

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

## App Store Optimization (ASO)

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
finds exactly the right meme. Download as GIF, PNG, or video.

★ FEATURES
• AI-powered meme search — not just keyword matching
• 10,000+ memes and GIFs
• All formats: GIF, PNG, MP4, WebP
• Instant copy to clipboard
• Save favorites to your personal library
• Zero ads. Zero watermarks.

App Screenshots (5 screens):
1. Home screen with search bar (show the UI)
2. Search results in 2 seconds (show speed)
3. Meme card with download options (show formats)
4. Share sheet (show usability)
5. Library / trending (show value)
```

### Google Play Store

```
App Name:   MemeGPT: AI Meme Finder & Download
Short Desc: Type anything → AI finds your perfect meme. Download GIF, PNG, video free!
Category:   Entertainment
Tags:       meme, funny, gif, ai, humor
```

---

## SEO Monitoring

| Metric | Tool | Frequency | Target |
|---|---|---|---|
| Indexed pages | Google Search Console | Weekly | 10K+ pages |
| Organic traffic | Umami Analytics | Daily | Growth month-over-month |
| Core Web Vitals | PageSpeed Insights | Monthly | All green |
| Keyword rankings | Free SERP tracker | Weekly | Top 10 for brand terms |
| Backlinks | Google Search Console | Monthly | Quality over quantity |

---

## Best Practices

1. **Every meme page has unique title, description, and canonical URL**
2. **Use `generateStaticParams` for SSG** — pre-render all meme pages at build time
3. **AI-generated alt text for all images** — accessibility + image search SEO
4. **Compress OG images** — 1200×630, <200KB for fast social card loading
5. **Internal linking** — every meme page links to related memes
6. **URL slugs are permanent** — never change a slug after indexing
7. **Submit sitemap to Google Search Console** within 24 hours of launch

---

> **Related Documents:**
> - [Marketing_Plan.md](./Marketing_Plan.md) — Launch strategy
> - [04_Frontend/Performance.md](../04_Frontend/Performance.md) — Core Web Vitals
> - [08_Features/Smart_Meme_Search.md](../08_Features/Smart_Meme_Search.md) — Search feature
