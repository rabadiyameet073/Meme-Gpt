import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Blog — MemeGPT | AI Memes, Vector Search & Meme Culture',
  description:
    'Explore MemeGPT engineering insights: AI vector search, emotion detection, meme trends, and how we built an AI-powered meme recommendation engine. Updated regularly.',
  openGraph: {
    title: 'MemeGPT Blog — AI Memes & Engineering',
    description: 'Engineering blog from the team behind the AI meme recommendation engine.',
    type: 'website',
  },
};

const BLOG_POSTS = [
  {
    slug: 'how-ai-finds-the-perfect-meme',
    title: 'How AI Finds the Perfect Meme for Any Situation',
    excerpt:
      'We built a 5-stage AI pipeline combining Groq LLM intent parsing, DistilRoBERTa emotion detection, MiniLM embeddings, Qdrant vector search, and business-logic re-ranking. Here\'s exactly how it works.',
    date: 'August 2, 2026',
    readTime: '8 min read',
    category: 'Engineering',
    emoji: '🤖',
    color: 'border-violet-700/40 bg-violet-900/10',
    badge: 'border-violet-700 text-violet-400',
  },
  {
    slug: 'vector-search-vs-keyword-search-memes',
    title: 'Why Keyword Search Fails for Memes (And What We Did Instead)',
    excerpt:
      'Keyword search returns "monday morning" when you search "monday morning". Semantic vector search returns the exact meme you\'re thinking of — even if you can\'t describe it precisely. Here\'s the difference.',
    date: 'July 28, 2026',
    readTime: '6 min read',
    category: 'AI/ML',
    emoji: '🔍',
    color: 'border-blue-700/40 bg-blue-900/10',
    badge: 'border-blue-700 text-blue-400',
  },
  {
    slug: 'emotion-detection-meme-matching',
    title: 'Using Emotion Detection to Match Memes: A Deep Dive',
    excerpt:
      'We run j-hartmann/emotion-english-distilroberta-base locally (250MB, CPU, ~100ms) on every query. Seven emotions. The emotion signal boosts matching memes by up to 23% in the ranking layer.',
    date: 'July 22, 2026',
    readTime: '7 min read',
    category: 'AI/ML',
    emoji: '💜',
    color: 'border-pink-700/40 bg-pink-900/10',
    badge: 'border-pink-700 text-pink-400',
  },
  {
    slug: 'building-memegpt-on-zero-dollars',
    title: 'Building MemeGPT on $0/Month: Our Free-Tier Stack',
    excerpt:
      'Groq (free LLM API), Qdrant Cloud (1M vectors free), Supabase (PostgreSQL free), Cloudflare R2 (10GB free), Upstash Redis (free), Vercel (frontend free), Railway (backend). Total: $0.',
    date: 'July 15, 2026',
    readTime: '5 min read',
    category: 'Startup',
    emoji: '💰',
    color: 'border-green-700/40 bg-green-900/10',
    badge: 'border-green-700 text-green-400',
  },
  {
    slug: 'top-memes-for-programmers-2026',
    title: 'Top 50 Programming Memes of 2026 — Ranked by AI',
    excerpt:
      'We ran our own AI ranking engine on the top 50 programming memes of 2026. "It works on my machine", "Stack Overflow copy-paste", and "Friday deploy" memes dominate the charts.',
    date: 'July 8, 2026',
    readTime: '4 min read',
    category: 'Meme Culture',
    emoji: '😂',
    color: 'border-amber-700/40 bg-amber-900/10',
    badge: 'border-amber-700 text-amber-400',
  },
  {
    slug: 'meme-data-pipeline-explained',
    title: 'MemeGPT Data Pipeline: From Reddit to Vector DB in 5 Steps',
    excerpt:
      'How we collect, clean, OCR, caption (via BLIP), embed (via CLIP + MiniLM), and index 10,000+ memes into Qdrant. The offline pipeline that powers the entire recommendation engine.',
    date: 'July 1, 2026',
    readTime: '10 min read',
    category: 'Engineering',
    emoji: '⚙️',
    color: 'border-orange-700/40 bg-orange-900/10',
    badge: 'border-orange-700 text-orange-400',
  },
];

const CATEGORIES = ['All', 'Engineering', 'AI/ML', 'Startup', 'Meme Culture'];

export default function BlogPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 space-y-16">

      {/* Header */}
      <div className="space-y-4">
        <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">Blog</p>
        <h1 className="text-4xl sm:text-5xl font-display font-extrabold text-gradient leading-tight">
          Engineering, AI &amp; Memes
        </h1>
        <p className="text-neutral-400 text-lg max-w-2xl">
          Deep dives into how MemeGPT works — from AI pipelines to meme culture analysis.
          Written by the team building the AI meme engine.
        </p>
      </div>

      {/* Category filter — static for now, interactive requires client component */}
      <div className="flex flex-wrap gap-2" aria-label="Blog categories">
        {CATEGORIES.map((cat) => (
          <span
            key={cat}
            className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition-all cursor-default
              ${cat === 'All'
                ? 'bg-violet-600/20 border-violet-600/50 text-violet-300'
                : 'bg-neutral-900 border-neutral-800 text-neutral-500'
              }`}
          >
            {cat}
          </span>
        ))}
      </div>

      {/* Featured post */}
      <Link
        href={`/blog/${BLOG_POSTS[0].slug}`}
        className="block group"
        aria-label={`Read: ${BLOG_POSTS[0].title}`}
      >
        <article
          className={`border ${BLOG_POSTS[0].color} rounded-3xl p-8 sm:p-10 space-y-4
                       card-hover hover:border-violet-600/50 transition-all`}
        >
          <div className="flex items-center gap-3">
            <span className="text-4xl" aria-hidden="true">{BLOG_POSTS[0].emoji}</span>
            <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 
                             rounded-full border ${BLOG_POSTS[0].badge} bg-transparent`}>
              {BLOG_POSTS[0].category}
            </span>
            <span className="text-xs text-neutral-600 ml-auto hidden sm:block">✦ Featured</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-display font-bold text-neutral-100 
                          group-hover:text-violet-300 transition-colors leading-snug">
            {BLOG_POSTS[0].title}
          </h2>
          <p className="text-neutral-400 leading-relaxed">{BLOG_POSTS[0].excerpt}</p>
          <div className="flex items-center gap-4 text-xs text-neutral-600 pt-1">
            <span>{BLOG_POSTS[0].date}</span>
            <span>·</span>
            <span>{BLOG_POSTS[0].readTime}</span>
            <span className="ml-auto text-violet-400 font-semibold group-hover:translate-x-1 transition-transform">
              Read →
            </span>
          </div>
        </article>
      </Link>

      {/* Post grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {BLOG_POSTS.slice(1).map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="group block"
            aria-label={`Read: ${post.title}`}
          >
            <article
              className={`h-full border ${post.color} rounded-2xl p-6 space-y-3
                           card-hover hover:border-violet-600/40 transition-all`}
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl" aria-hidden="true">{post.emoji}</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${post.badge} bg-transparent`}>
                  {post.category}
                </span>
              </div>
              <h2 className="font-display font-bold text-neutral-100 leading-snug
                              group-hover:text-violet-300 transition-colors">
                {post.title}
              </h2>
              <p className="text-sm text-neutral-500 leading-relaxed line-clamp-3">
                {post.excerpt}
              </p>
              <div className="flex items-center gap-3 text-xs text-neutral-600 pt-1">
                <span>{post.date}</span>
                <span>·</span>
                <span>{post.readTime}</span>
                <span className="ml-auto text-violet-500 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </article>
          </Link>
        ))}
      </div>

      {/* CTA */}
      <div className="text-center border-t border-neutral-800 pt-12 space-y-4">
        <p className="text-neutral-500 text-sm">
          Building something with memes? Try the AI search engine.
        </p>
        <Link
          href="/app"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                     text-white font-bold px-8 py-4 rounded-2xl text-base
                     transition-all hover:scale-[1.03] active:scale-[0.97]"
        >
          Try MemeGPT free →
        </Link>
      </div>
    </div>
  );
}
