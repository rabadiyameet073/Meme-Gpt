# 07 — Next.js Web App Completion Guide
> Complete the SEO meme pages, blog system, features page, download page, JSON-LD, and OG images.

---

## Problem Statement

The `apps/web/` Next.js app has:
- ✅ Root layout with SEO metadata
- ✅ Marketing landing page (19.5KB)
- ✅ Sitemap generation
- ✅ Robots.txt
- ❌ Meme detail pages are skeletons
- ❌ Blog system not built
- ❌ Features page incomplete
- ❌ Download page incomplete
- ❌ No JSON-LD structured data
- ❌ No OG image file
- ❌ Framer Motion not installed

---

## Step 1: Install Missing Dependencies

```powershell
cd "d:\Meme GPT\apps\web"
npm install framer-motion@^11.0.0
```

---

## Step 2: Create the Meme Detail SEO Page

This is the **most important page for SEO** — every meme gets its own URL.

**File (create/replace):** `apps/web/app/meme/[slug]/page.tsx`

```tsx
import React from 'react';
import { Metadata } from 'next';
import { notFound } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface MemeData {
  id: string;
  name: string;
  slug: string;
  explanation: string;
  categories: string[];
  emotions: string[];
  keywords: string[];
  image_url: string;
  gif_url?: string;
  mp4_url?: string;
}

async function getMeme(slug: string): Promise<MemeData | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/memes/${slug}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

// Dynamic metadata for each meme
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const meme = await getMeme(params.slug);
  if (!meme) return { title: 'Meme Not Found' };

  return {
    title: `${meme.name} — Download GIF, PNG, MP4`,
    description: `${meme.explanation || meme.name} — ${meme.emotions?.join(', ')} meme. Download as GIF, PNG, or MP4. Perfect for: ${meme.keywords?.join(', ')}.`,
    keywords: [...(meme.keywords || []), meme.name, 'meme', 'download meme', 'reaction meme'],
    openGraph: {
      title: `${meme.name} — MemeGPT`,
      description: meme.explanation || `Download ${meme.name} meme`,
      images: [{ url: meme.image_url, width: 600, height: 600, alt: meme.name }],
      type: 'article',
    },
    twitter: {
      card: 'summary_large_image',
      title: meme.name,
      images: [meme.image_url],
    },
  };
}

export default async function MemePage({ params }: { params: { slug: string } }) {
  const meme = await getMeme(params.slug);
  if (!meme) notFound();

  // JSON-LD Structured Data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ImageObject',
    name: meme.name,
    description: meme.explanation || meme.name,
    contentUrl: meme.gif_url || meme.image_url,
    thumbnailUrl: meme.image_url,
    keywords: meme.keywords?.join(', '),
    creator: { '@type': 'Organization', name: 'MemeGPT' },
    encodingFormat: meme.gif_url ? 'image/gif' : 'image/png',
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />

      <main className="min-h-screen bg-neutral-950 text-neutral-100">
        <div className="max-w-4xl mx-auto px-4 py-12">
          {/* Breadcrumb */}
          <nav className="text-sm text-neutral-500 mb-6">
            <a href="/" className="hover:text-purple-400">Home</a>
            {' / '}
            <a href={`/memes/${meme.categories?.[0] || 'all'}`} className="hover:text-purple-400">
              {meme.categories?.[0] || 'Memes'}
            </a>
            {' / '}
            <span className="text-neutral-300">{meme.name}</span>
          </nav>

          {/* Meme Image */}
          <div className="rounded-2xl overflow-hidden bg-neutral-900 border border-neutral-800">
            <img
              src={meme.gif_url || meme.image_url}
              alt={meme.name}
              className="w-full max-h-[600px] object-contain"
              loading="eager"
            />
          </div>

          {/* Title & Description */}
          <h1 className="text-3xl font-bold mt-8 mb-3">{meme.name}</h1>
          {meme.explanation && (
            <p className="text-neutral-400 text-lg leading-relaxed mb-6">{meme.explanation}</p>
          )}

          {/* Download Buttons */}
          <div className="flex flex-wrap gap-3 mb-8">
            {meme.image_url && (
              <a
                href={meme.image_url}
                download
                className="inline-flex items-center px-5 py-2.5 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors"
              >
                📷 Download PNG
              </a>
            )}
            {meme.gif_url && (
              <a
                href={meme.gif_url}
                download
                className="inline-flex items-center px-5 py-2.5 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
              >
                🎬 Download GIF
              </a>
            )}
            {meme.mp4_url && (
              <a
                href={meme.mp4_url}
                download
                className="inline-flex items-center px-5 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
              >
                🎥 Download MP4
              </a>
            )}
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mb-8">
            {meme.emotions?.map((e: string) => (
              <span key={e} className="px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-sm border border-purple-500/20">
                {e}
              </span>
            ))}
            {meme.categories?.map((c: string) => (
              <span key={c} className="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-full text-sm border border-blue-500/20">
                {c}
              </span>
            ))}
          </div>

          {/* Keywords for SEO */}
          <section className="mt-8 pt-6 border-t border-neutral-800">
            <h2 className="text-lg font-semibold mb-3">Related searches</h2>
            <div className="flex flex-wrap gap-2">
              {meme.keywords?.map((k: string) => (
                <a
                  key={k}
                  href={`/?q=${encodeURIComponent(k)}`}
                  className="px-3 py-1 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-sm text-neutral-300 transition-colors"
                >
                  {k}
                </a>
              ))}
            </div>
          </section>
        </div>
      </main>
    </>
  );
}
```

---

## Step 3: Create Category Pages

**File (create):** `apps/web/app/memes/[category]/page.tsx`

```tsx
import React from 'react';
import { Metadata } from 'next';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const CATEGORIES = [
  { slug: 'work-memes', title: 'Work & Office Memes', emoji: '💼' },
  { slug: 'coding-memes', title: 'Programming & Coding Memes', emoji: '💻' },
  { slug: 'college-memes', title: 'College & Student Memes', emoji: '🎓' },
  { slug: 'gaming-memes', title: 'Gaming Memes', emoji: '🎮' },
  { slug: 'relationship-memes', title: 'Relationship & Dating Memes', emoji: '❤️' },
  { slug: 'reaction-memes', title: 'Reaction Memes', emoji: '😂' },
  { slug: 'wholesome-memes', title: 'Wholesome & Positive Memes', emoji: '🥰' },
  { slug: 'food-memes', title: 'Food & Cooking Memes', emoji: '🍕' },
];

export async function generateStaticParams() {
  return CATEGORIES.map(c => ({ category: c.slug }));
}

export async function generateMetadata({ params }: { params: { category: string } }): Promise<Metadata> {
  const cat = CATEGORIES.find(c => c.slug === params.category);
  const title = cat?.title || 'Memes';
  return {
    title: `${title} — Best ${title} to Download Free`,
    description: `Browse and download the best ${title.toLowerCase()}. GIF, PNG, and MP4 formats. AI-curated collection updated daily.`,
  };
}

export default async function CategoryPage({ params }: { params: { category: string } }) {
  const cat = CATEGORIES.find(c => c.slug === params.category);
  const categoryName = params.category.replace(/-memes?$/, '').replace(/-/g, ' ');

  let memes: any[] = [];
  try {
    const resp = await fetch(`${API_BASE}/api/v1/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: categoryName, limit: 20, filters: { categories: [categoryName] } }),
      next: { revalidate: 3600 },
    });
    const data = await resp.json();
    memes = data.results || [];
  } catch { /* fallback to empty */ }

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-2">{cat?.emoji} {cat?.title || 'Memes'}</h1>
        <p className="text-neutral-400 mb-8">
          AI-curated {cat?.title?.toLowerCase() || 'memes'} — download as GIF, PNG, or MP4.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {memes.map((meme: any) => (
            <a key={meme.id} href={`/meme/${meme.slug}`} className="group">
              <div className="rounded-xl overflow-hidden bg-neutral-900 border border-neutral-800 hover:border-purple-500/50 transition-colors">
                <img
                  src={meme.thumb_url || meme.image_url}
                  alt={meme.name}
                  className="w-full aspect-square object-cover group-hover:scale-105 transition-transform"
                  loading="lazy"
                />
                <div className="p-3">
                  <p className="text-sm font-medium text-neutral-200 truncate">{meme.name}</p>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}
```

---

## Step 4: Create Blog System

### 4.1 Blog Layout

**File (create):** `apps/web/app/(marketing)/blog/page.tsx`

```tsx
import React from 'react';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'MemeGPT Blog — Meme Culture, AI & Trends',
  description: 'Read about meme culture, AI in meme search, trending memes, and tips for finding the perfect meme.',
};

// Static blog posts — later replace with CMS or API
const POSTS = [
  {
    slug: 'how-ai-finds-perfect-meme',
    title: 'How AI Finds the Perfect Meme for Any Situation',
    excerpt: 'Dive into how MemeGPT uses vector search, emotion detection, and LLMs to match you with memes.',
    date: '2026-09-01',
    readTime: '5 min',
    category: 'Technology',
  },
  {
    slug: 'top-50-work-memes-2026',
    title: 'Top 50 Work Memes of 2026 (So Far)',
    excerpt: 'The best memes about office life, meetings, emails, and that one coworker.',
    date: '2026-08-15',
    readTime: '8 min',
    category: 'Trending',
  },
  {
    slug: 'meme-formats-explained',
    title: 'Meme Formats Explained: GIF vs PNG vs MP4',
    excerpt: 'Which format should you use? Here is everything you need to know.',
    date: '2026-08-01',
    readTime: '4 min',
    category: 'Guide',
  },
];

export default function BlogPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-2">📝 MemeGPT Blog</h1>
        <p className="text-neutral-400 text-lg mb-12">Meme culture, AI tech, and trending memes.</p>

        <div className="space-y-8">
          {POSTS.map(post => (
            <a key={post.slug} href={`/blog/${post.slug}`} className="block group">
              <article className="p-6 rounded-2xl bg-neutral-900/50 border border-neutral-800 hover:border-purple-500/40 transition-colors">
                <div className="flex items-center gap-3 text-sm text-neutral-500 mb-3">
                  <span className="px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded-full text-xs">{post.category}</span>
                  <span>{post.date}</span>
                  <span>· {post.readTime} read</span>
                </div>
                <h2 className="text-xl font-semibold mb-2 group-hover:text-purple-400 transition-colors">{post.title}</h2>
                <p className="text-neutral-400">{post.excerpt}</p>
              </article>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}
```

---

## Step 5: Create OG Image

Place a 1200×630 image at `apps/web/public/og-image.jpg`.

You can auto-generate one or create with any design tool. Key requirements:
- 1200×630 pixels
- Brand colors (purple #7C3AED gradient)
- Text: "MemeGPT — Find the Perfect Meme with AI"
- Logo or meme emoji

---

## Step 6: Add `vercel.json` Inside `apps/web/`

**File (create):** `apps/web/vercel.json`

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    },
    {
      "source": "/meme/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=3600, s-maxage=86400" }
      ]
    }
  ],
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.memegpt.com/api/:path*" }
  ]
}
```

---

## Step 7: Add Environment Variables

**File:** `apps/web/.env.local`

```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Verification Checklist

- [ ] `/meme/[slug]` pages render with full SEO metadata
- [ ] JSON-LD structured data present on meme pages
- [ ] `/memes/work-memes` category pages work
- [ ] `/blog` lists blog posts
- [ ] `og-image.jpg` exists in `apps/web/public/`
- [ ] `vercel.json` exists in `apps/web/`
- [ ] `npm run build` succeeds for `apps/web`
- [ ] Framer Motion is installed
