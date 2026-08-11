import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

interface Props {
  params: { slug: string };
}

/* ── Static blog content keyed by slug ───────────────────────────────────── */

const POSTS: Record<string, {
  title: string;
  date: string;
  readTime: string;
  category: string;
  emoji: string;
  excerpt: string;
  content: React.ReactNode;
}> = {
  'how-ai-finds-the-perfect-meme': {
    title: 'How AI Finds the Perfect Meme for Any Situation',
    date: 'August 2, 2026',
    readTime: '8 min read',
    category: 'Engineering',
    emoji: '🤖',
    excerpt: 'We built a 5-stage AI pipeline combining Groq LLM intent parsing, DistilRoBERTa emotion detection, MiniLM embeddings, Qdrant vector search, and business-logic re-ranking.',
    content: (
      <div className="space-y-6 text-neutral-300 leading-relaxed">
        <p>
          When you type <em>"my boss emailed at 11pm on Friday"</em> into MemeGPT, five separate AI systems activate
          within 1.5 seconds to find you the most relevant meme. Here's exactly what happens.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 1: Intent Parsing (Groq, ~300ms)</h2>
        <p>
          The raw user text is sent to <strong>Groq's llama-3.1-8b-instant</strong> — the fastest free LLM available
          at 500+ tokens/second. The LLM extracts a structured JSON object containing: the primary emotion,
          situation description, tone (sarcastic/sincere/humorous/etc.), keywords, and meme format hint.
        </p>
        <pre className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 text-sm font-mono overflow-x-auto text-green-400">
{`// LLM output for "my boss emailed at 11pm on Friday"
{
  "emotion": "frustration",
  "situation": "boss email after work hours on Friday",
  "tone": "sarcastic",
  "keywords": ["boss", "email", "friday", "night", "work"],
  "meme_format": "reaction"
}`}
        </pre>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 2: Emotion Detection (~100ms)</h2>
        <p>
          Simultaneously, <strong>j-hartmann/emotion-english-distilroberta-base</strong> runs locally on CPU.
          This 250MB model classifies 7 emotions and returns confidence scores. The top emotion is used
          to boost matching memes in the re-ranking layer.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 3: Query Embedding (~50ms)</h2>
        <p>
          The intent-enriched query text is converted into a <strong>384-dimensional vector</strong> using
          sentence-transformers/all-MiniLM-L6-v2. This 80MB model runs on CPU and handles 14,000 sentences/second.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 4: Vector Search (~50ms)</h2>
        <p>
          The 384-dim query vector is searched against our Qdrant vector database using cosine similarity.
          Top-10 candidates are returned with their similarity scores. Qdrant uses HNSW indexing for
          sub-100ms search across 100,000+ vectors.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 5: Re-Ranking (~10ms)</h2>
        <p>
          The top-10 candidates are re-ranked using business logic: +15% for primary emotion match,
          +8% for secondary emotion, +10% popularity boost, +5% for format preference. The top-5
          results are returned to the user.
        </p>
        <p>
          Total: <strong className="text-violet-400">under 1.5 seconds</strong> for any query,
          any emotion, any situation.
        </p>
      </div>
    ),
  },

  'vector-search-vs-keyword-search-memes': {
    title: 'Why Keyword Search Fails for Memes (And What We Did Instead)',
    date: 'July 28, 2026',
    readTime: '6 min read',
    category: 'AI/ML',
    emoji: '🔍',
    excerpt: 'Keyword search returns memes with matching words. Semantic search returns the meme you\'re thinking of — even when you can\'t describe it.',
    content: (
      <div className="space-y-6 text-neutral-300 leading-relaxed">
        <p>
          Traditional meme search engines use keyword matching: you type "tired monday" and they return
          memes tagged with those exact words. This fails constantly.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">The Problem with Keywords</h2>
        <p>
          When someone types <em>"my alarm went off and I wanted to throw my phone"</em>, keyword search
          returns nothing useful — no meme is tagged "alarm" and "throw phone". But the perfect meme
          for this situation is the classic "This is fine" dog, or the sleepy Kermit.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">How Vector Search Solves This</h2>
        <p>
          Vector embeddings capture <em>meaning</em>, not just words. The sentence-transformers model
          converts both the query and every meme description into 384-dimensional vectors in the same
          semantic space. Memes about "not wanting to wake up" and "hating Monday mornings" cluster
          together — and your query about alarm clocks lands right next to them.
        </p>
        <p>
          The result: search by vibe, search by situation, search by feeling — and always get something
          that fits.
        </p>
      </div>
    ),
  },

  'building-memegpt-on-zero-dollars': {
    title: 'Building MemeGPT on $0/Month: Our Free-Tier Stack',
    date: 'July 15, 2026',
    readTime: '5 min read',
    category: 'Startup',
    emoji: '💰',
    excerpt: 'Every service in our stack has a free tier generous enough to handle thousands of users. Total cost: $0/month at MVP scale.',
    content: (
      <div className="space-y-6 text-neutral-300 leading-relaxed">
        <p>
          MemeGPT is built entirely on free-tier services. Here's the breakdown:
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-neutral-800 text-neutral-400">
                <th className="text-left py-2 pr-4">Service</th>
                <th className="text-left py-2 pr-4">Use</th>
                <th className="text-left py-2">Free Tier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-900">
              {[
                ['Groq', 'LLM intent parsing', '6,000 req/day'],
                ['Qdrant Cloud', 'Vector search', '1M vectors, 1GB'],
                ['Supabase', 'PostgreSQL database', '500MB, 2GB BW'],
                ['Cloudflare R2', 'Meme file storage', '10GB storage'],
                ['Upstash Redis', 'Caching', '10K cmd/day'],
                ['Vercel', 'Frontend hosting', 'Unlimited deploys'],
                ['Railway', 'Backend hosting', '$5 credit/month'],
                ['GitHub Actions', 'CI/CD', '2,000 min/month'],
              ].map(([svc, use, tier]) => (
                <tr key={svc}>
                  <td className="py-2 pr-4 font-semibold text-violet-400">{svc}</td>
                  <td className="py-2 pr-4 text-neutral-400">{use}</td>
                  <td className="py-2 text-green-400">{tier}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p>
          At roughly 500 daily users doing 3 searches each, this stack handles everything for free.
          The first real cost comes around 5,000+ daily active users — at which point you're profitable.
        </p>
      </div>
    ),
  },
};

/* ── generateMetadata ────────────────────────────────────────────────────── */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = POSTS[params.slug];
  if (!post) {
    return { title: 'Post Not Found | MemeGPT Blog' };
  }
  return {
    title: `${post.title} | MemeGPT Blog`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
    },
  };
}

/* ── Page ────────────────────────────────────────────────────────────────── */
export default function BlogPostPage({ params }: Props) {
  const post = POSTS[params.slug];

  if (!post) {
    // Generic fallback for slugs without content
    const title = params.slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return (
      <main className="max-w-3xl mx-auto px-4 py-16 space-y-8">
        <Link href="/blog" className="text-sm text-violet-400 hover:text-violet-300 transition-colors inline-flex items-center gap-1">
          ← Back to Blog
        </Link>
        <article className="space-y-6">
          <div className="space-y-3">
            <p className="text-xs text-neutral-600 uppercase tracking-wider">August 1, 2026 · 5 min read</p>
            <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-neutral-100 leading-tight">{title}</h1>
          </div>
          <div className="h-px bg-neutral-800" />
          <div className="space-y-4 text-neutral-300 leading-relaxed">
            <p>
              MemeGPT uses a multi-stage AI pipeline to recommend the perfect meme for any text input.
              The core is a combination of semantic vector search (MiniLM-L6-v2 + Qdrant) and emotion
              classification (DistilRoBERTa), enriched by Groq LLM intent parsing.
            </p>
            <p>
              The result is a recommendation engine that understands context, emotion, sarcasm, and
              cultural nuance — not just keywords.
            </p>
          </div>
        </article>
        <div className="pt-8 border-t border-neutral-800">
          <Link
            href="/app"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                       text-white font-bold px-6 py-3 rounded-xl transition-all text-sm"
          >
            Try MemeGPT →
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-16">
      {/* Back link */}
      <Link
        href="/blog"
        className="text-sm text-violet-400 hover:text-violet-300 transition-colors inline-flex items-center gap-1 mb-10 block"
      >
        ← Back to Blog
      </Link>

      <article className="space-y-8">
        {/* Header */}
        <header className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl" aria-hidden="true">{post.emoji}</span>
            <span className="text-xs font-bold text-violet-400 uppercase tracking-wider">{post.category}</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-neutral-100 leading-tight">
            {post.title}
          </h1>
          <p className="text-neutral-400 leading-relaxed">{post.excerpt}</p>
          <div className="flex items-center gap-3 text-xs text-neutral-600">
            <time dateTime={post.date}>{post.date}</time>
            <span>·</span>
            <span>{post.readTime}</span>
          </div>
        </header>

        {/* Divider */}
        <div className="h-px bg-neutral-800" />

        {/* Content */}
        <div className="blog-content">
          {post.content}
        </div>
      </article>

      {/* Footer CTA */}
      <div className="mt-16 pt-10 border-t border-neutral-800 space-y-4">
        <p className="text-neutral-500 text-sm">Ready to find the perfect meme?</p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/app"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                       text-white font-bold px-6 py-3 rounded-xl transition-all text-sm"
          >
            Try MemeGPT free →
          </Link>
          <Link
            href="/blog"
            className="inline-flex items-center gap-2 bg-neutral-900 hover:bg-neutral-800
                       border border-neutral-800 hover:border-neutral-700
                       text-neutral-300 font-semibold px-6 py-3 rounded-xl transition-all text-sm"
          >
            More posts
          </Link>
        </div>
      </div>
    </main>
  );
}
