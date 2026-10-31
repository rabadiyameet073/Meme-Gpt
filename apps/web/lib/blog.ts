/**
 * Blog metadata — the single source of truth for which posts exist.
 *
 * The index page, the `/blog/[slug]` route and `sitemap.ts` all read from this
 * list. Previously the index, the sitemap and the post content kept three
 * separate slug lists, so the sitemap advertised six posts while only three had
 * content and unknown slugs rendered a fabricated placeholder article.
 */

export interface BlogPostMeta {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  /** ISO date, used for sitemap `lastModified`. */
  publishedAt: string;
  readTime: string;
  category: 'Engineering' | 'AI/ML' | 'Startup' | 'Meme Culture';
  emoji: string;
  color: string;
  badge: string;
}

export const BLOG_CATEGORIES = ['All', 'Engineering', 'AI/ML', 'Startup', 'Meme Culture'] as const;

export const BLOG_POSTS: BlogPostMeta[] = [
  {
    slug: 'how-ai-finds-the-perfect-meme',
    title: 'How AI Finds the Perfect Meme for Any Situation',
    excerpt:
      'We built a 5-stage AI pipeline combining Groq LLM intent parsing, DistilRoBERTa emotion detection, MiniLM embeddings, Qdrant vector search, and business-logic re-ranking.',
    date: 'August 2, 2026',
    publishedAt: '2026-08-02',
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
      'Keyword search returns "monday morning" when you search "monday morning". Semantic vector search returns the exact meme you are thinking of — even if you cannot describe it precisely.',
    date: 'July 28, 2026',
    publishedAt: '2026-07-28',
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
      'We run j-hartmann/emotion-english-distilroberta-base locally on CPU for every query. Seven emotions, and the emotion signal is what separates a relevant meme from a merely similar one.',
    date: 'July 22, 2026',
    publishedAt: '2026-07-22',
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
      'Groq (free LLM API), Qdrant (embedded or 1M vectors free), SQLite/PostgreSQL, Cloudflare R2 (10GB free), Upstash Redis (free), Vercel (frontend), Railway (backend).',
    date: 'July 15, 2026',
    publishedAt: '2026-07-15',
    readTime: '5 min read',
    category: 'Startup',
    emoji: '💰',
    color: 'border-green-700/40 bg-green-900/10',
    badge: 'border-green-700 text-green-400',
  },
  {
    slug: 'top-memes-for-programmers-2026',
    title: 'Top Programming Memes of 2026 — Ranked by the Catalog',
    excerpt:
      'How we rank programming memes, plus the highest-scoring developer templates in our catalog right now — "This Is Fine", "StackOverflow Down Panic" and "Works on My Machine".',
    date: 'July 8, 2026',
    publishedAt: '2026-07-08',
    readTime: '4 min read',
    category: 'Meme Culture',
    emoji: '😂',
    color: 'border-amber-700/40 bg-amber-900/10',
    badge: 'border-amber-700 text-amber-400',
  },
  {
    slug: 'meme-data-pipeline-explained',
    title: 'MemeGPT Data Pipeline: From Catalog to Vector DB in 5 Steps',
    excerpt:
      'How we seed, clean, OCR, caption (via BLIP), embed (via CLIP + MiniLM), and index memes into Qdrant. The offline pipeline that powers the entire recommendation engine.',
    date: 'July 1, 2026',
    publishedAt: '2026-07-01',
    readTime: '10 min read',
    category: 'Engineering',
    emoji: '⚙️',
    color: 'border-orange-700/40 bg-orange-900/10',
    badge: 'border-orange-700 text-orange-400',
  },
];

export const BLOG_SLUGS = BLOG_POSTS.map((post) => post.slug);

export function getBlogPostMeta(slug: string): BlogPostMeta | undefined {
  return BLOG_POSTS.find((post) => post.slug === slug);
}
