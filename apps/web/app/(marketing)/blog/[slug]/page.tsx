import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { BLOG_POSTS } from '../../../../lib/blog';

interface Props {
  params: { slug: string };
}

/** Pre-render every post that exists in the shared blog manifest. */
export function generateStaticParams() {
  return BLOG_POSTS.map((post) => ({ slug: post.slug }));
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
          It classifies the query into 7 emotions — joy, sadness, anger, surprise, fear, disgust, neutral —
          and returns a confidence score for each. The top label becomes the primary emotion signal used
          by the re-ranking layer.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 3: Query Embedding (~50ms)</h2>
        <p>
          The intent-enriched query text is converted into a <strong>384-dimensional vector</strong> using
          sentence-transformers/all-MiniLM-L6-v2. The model runs on CPU and is small enough to stay
          resident between requests, so no per-query download or cold start.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 4: Vector Search (~50ms)</h2>
        <p>
          The 384-dim query vector is searched against our Qdrant vector database using cosine similarity.
          Candidates are returned with their similarity scores. Qdrant uses HNSW indexing, so query time
          stays flat as the catalog grows.
        </p>
        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Stage 5: Re-Ranking (~10ms)</h2>
        <p>
          Candidates are re-scored with a convex blend of seven normalised signals that sums to exactly
          1.0 — semantic similarity <strong>0.34</strong>, lexical overlap <strong>0.30</strong>, primary
          emotion match <strong>0.14</strong>, secondary emotion match <strong>0.06</strong>, popularity
          <strong>0.08</strong>, recency <strong>0.03</strong> and format preference <strong>0.05</strong>.
          Because the weights sum to 1.0 the result is a true relevance in [0, 1] that cannot saturate
          into a tie. Duplicate meme names are then dropped and the top-5 are returned.
        </p>
        <p>
          Budget: <strong className="text-violet-400">under 1.5 seconds</strong> end to end,
          including the LLM call.
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
          Every service in the list above has a free tier that covers MVP traffic. Costs stay at zero
          until you outgrow one of them — in practice the first paid upgrade is usually the LLM quota
          or the managed database, not the vector store.
        </p>
      </div>
    ),
  },

  'emotion-detection-meme-matching': {
    title: 'Using Emotion Detection to Match Memes: A Deep Dive',
    date: 'July 22, 2026',
    readTime: '7 min read',
    category: 'AI/ML',
    emoji: '💜',
    excerpt: 'We run j-hartmann/emotion-english-distilroberta-base locally on CPU for every query. Seven emotions, and the emotion signal is what separates a relevant meme from a merely similar one.',
    content: (
      <div className="space-y-6 text-neutral-300 leading-relaxed">
        <p>
          Vector search answers one question: <em>which memes talk about the same topic as this query?</em>
          That is not the same as <em>which meme fits this feeling?</em> Two queries can sit
          next to each other in embedding space and still deserve completely different reactions.
        </p>
        <p>
          Emotion detection closes that gap. It is the signal that decides between the calm
          &quot;This is fine&quot; dog and the panic-screaming template for two nearly identical sentences.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 1: Classify the query</h2>
        <p>
          Every query is passed through <strong>j-hartmann/emotion-english-distilroberta-base</strong>,
          a DistilRoBERTa model fine-tuned on GoEmotions. It scores seven labels —
          <strong> joy, sadness, anger, surprise, fear, disgust, neutral</strong> — and the highest-scoring
          label becomes the primary emotion. It runs locally on CPU, so there is no API call, no latency
          spike, and no per-request cost.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 2: Bridge two vocabularies</h2>
        <p>
          The classifier speaks GoEmotions. Our catalog speaks meme. A meme in the database is tagged
          with things like <code>panic</code>, <code>smug</code>, <code>pride</code> or <code>denial</code> —
          words that never appear in the classifier&apos;s output. Comparing the two directly returns
          nothing, which is exactly the bug that made every scenario collapse onto the same generic results.
        </p>
        <p>
          The fix is an explicit emotion-family table: each classifier label maps to the set of meme tags
          that express it. A query classified as <strong>anger</strong> matches a meme tagged
          <code>frustrated</code>, <code>rage</code> or <code>annoyed</code>, because they all live in the
          same family.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-neutral-800 text-neutral-400">
                <th className="text-left py-2 pr-4">Classifier label</th>
                <th className="text-left py-2">Also matches meme tags</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-900">
              {[
                ['joy', 'happy, pride, smug, victory, wholesome, relieved'],
                ['sadness', 'upset, lonely, resigned, regret, heartbroken'],
                ['anger', 'frustrated, rage, annoyed, furious'],
                ['surprise', 'shocked, confused, disbelief, stunned'],
                ['fear', 'panic, anxious, stressed, dread, overwhelmed'],
                ['disgust', 'gross, cringe, nasty'],
                ['neutral', 'humor, sarcastic, relatable, deadpan, chill'],
              ].map(([label, tags]) => (
                <tr key={label}>
                  <td className="py-2 pr-4 font-semibold text-violet-400">{label}</td>
                  <td className="py-2 text-neutral-400">{tags}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 3: Primary and secondary</h2>
        <p>
          One label is rarely the whole story. Any additional label with a confidence of at least
          <strong> 0.15</strong> joins the secondary set, together with the tone and emotion hints the LLM
          extracted during intent parsing. Families already claimed by the primary emotion are removed from
          the secondary set, so a strong <em>anger</em> signal never gets counted twice as both primary and
          secondary.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 4: Score it, do not multiply it</h2>
        <p>
          Emotion enters the ranking as a fixed contribution inside a convex blend, not as a multiplier
          on the vector score. Primary match is worth <strong>0.14</strong> and secondary match
          <strong> 0.06</strong>, alongside semantic similarity 0.34, lexical overlap 0.30, popularity 0.08,
          recency 0.03 and format preference 0.05. The weights sum to exactly 1.0, so the final relevance is
          a genuine [0, 1] value whose ordering is preserved.
        </p>
        <pre className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 text-sm font-mono overflow-x-auto text-green-400">
{`score = semantic * 0.34 + lexical * 0.30
      + (primary_emotion_match   ? 0.14 : 0)
      + (secondary_emotion_match ? 0.06 : 0)
      + popularity * 0.08 + recency * 0.03
      + (format_match ? 0.05 : 0)`}
        </pre>
        <p>
          An earlier version added every bonus on top of the cosine similarity and clipped at 0.99.
          Because MiniLM cosine values on short meme text are routinely above 0.7, most candidates
          saturated at the ceiling and the final order was decided by dictionary iteration order. The
          convex blend removes that failure mode entirely.
        </p>
      </div>
    ),
  },

  'top-memes-for-programmers-2026': {
    title: 'Top Programming Memes of 2026 — Ranked by the Catalog',
    date: 'July 8, 2026',
    readTime: '4 min read',
    category: 'Meme Culture',
    emoji: '😂',
    excerpt: 'How we rank programming memes, plus the highest-scoring developer templates in our catalog right now — "This Is Fine", "StackOverflow Down Panic" and "Works on My Machine".',
    content: (
      <div className="space-y-6 text-neutral-300 leading-relaxed">
        <p>
          Every meme in the catalog ships with a <strong>viral score</strong> — a curated 0–100 estimate of
          how hard a template hits, recorded next to the meme in our seeder. It is a static curation
          signal, not live usage data. Here are the eight developer-adjacent entries currently sitting at
          the top of that list.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-neutral-800 text-neutral-400">
                <th className="text-left py-2 pr-4">Meme</th>
                <th className="text-left py-2 pr-4">Viral score</th>
                <th className="text-left py-2">Use it when</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-900">
              {[
                ['This Is Fine Dog in Fire', '99.8', 'three alerts, one deadline, zero coffee'],
                ['Gigachad', '99.7', 'someone unironically read the docs'],
                ['Senior Dev Watching Junior Push to Main', '99.1', 'force-push to main on a Friday'],
                ['Meeting That Could Have Been An Email', '98.3', 'a 60-minute sync that fit in two lines'],
                ['StackOverflow Down Panic', '98.2', 'the copy-paste oracle is offline'],
                ['Dark Souls YOU DIED', '98.1', 'the test suite after a one-line change'],
                ['Friday 5 PM Clock Out', '97.9', 'laptop shut, notifications muted'],
                ['Works on My Machine', '96.0', 'the build is green locally and red in CI'],
              ].map(([name, score, when]) => (
                <tr key={name}>
                  <td className="py-2 pr-4 font-semibold text-violet-400">{name}</td>
                  <td className="py-2 pr-4 text-green-400">{score}</td>
                  <td className="py-2 text-neutral-400">{when}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">The dialogue matters more than the picture</h2>
        <p>
          Each entry carries its own caption, because that caption is what gets embedded and searched.
          &quot;This Is Fine&quot; is indexed with <em>This is fine. I&apos;m okay with the events that are
          unfolding currently.</em> — which is why a query like &quot;production is on fire and I have a
          dentist appointment&quot; lands on it without ever using the words <em>dog</em> or <em>fire</em>.
        </p>
        <p>
          &quot;StackOverflow Down Panic&quot; is indexed with <em>StackOverflow is offline. Humanity has
          forgotten how to write a for loop.</em> Two entirely different situations, same catalog, no
          overlap in keywords — and both reachable from natural language.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Curation vs. live engagement</h2>
        <p>
          The viral score is only one input at query time. Re-ranking computes a popularity component from
          three things — <strong>viral score × 0.5</strong>, <strong>usage count × 0.3</strong> and
          <strong> upvotes × 0.2</strong> — normalised to [0, 1]. A template with a lower curated score can
          still outrank this table if people actually keep picking it.
        </p>
        <p>
          That split is deliberate: curation decides what is <em>allowed</em> to be great, and behaviour
          decides what <em>is</em> great this week.
        </p>
      </div>
    ),
  },

  'meme-data-pipeline-explained': {
    title: 'MemeGPT Data Pipeline: From Catalog to Vector DB in 5 Steps',
    date: 'July 1, 2026',
    readTime: '10 min read',
    category: 'Engineering',
    emoji: '⚙️',
    excerpt: 'How we seed, clean, OCR, caption (via BLIP), embed (via CLIP + MiniLM), and index memes into Qdrant. The offline pipeline that powers the entire recommendation engine.',
    content: (
      <div className="space-y-6 text-neutral-300 leading-relaxed">
        <p>
          Nothing in the search path guesses. Every result comes from an offline pipeline that turns a
          curated catalog into searchable vectors. Here are the five steps, in the order they run.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 1: Seed the catalog</h2>
        <p>
          The catalog is code, not a spreadsheet. <code>scripts/seed_master_catalog.py</code> holds every
          meme as a record with its name, categories, emotion tags, dialogue, explanation, keywords and a
          curated viral score, and writes them into the database. The same script doubles as the repair
          tool: rows that point at media which does not exist are cleared rather than left broken.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 2: Look at the picture</h2>
        <p>
          Text alone cannot describe a meme template whose whole joke is visual. The image pass runs
          three things per file: <strong>OCR</strong> to recover burned-in caption text,
          <strong> BLIP</strong> (<code>Salesforce/blip-image-captioning-base</code>) to generate a plain
          description such as &quot;a dog sitting in a burning room holding a mug&quot;, and
          <strong> CLIP</strong> (<code>openai/clip-vit-base-patch32</code>) to produce a 512-dimension
          image embedding.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 3: Embed the text</h2>
        <p>
          Name, dialogue, explanation, keywords, categories and the BLIP caption are concatenated into one
          searchable document and embedded with <strong>all-MiniLM-L6-v2</strong> into a
          <strong> 384-dimension</strong> vector.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 4: Index into Qdrant</h2>
        <p>
          The collection uses three named vectors so each modality can be queried on its own:
          <strong> text</strong> (384), <strong>image</strong> (512) and <strong>combined</strong> (896).
          Named vectors are why the same point can answer a text query, an image query, or a hybrid one
          without duplicating the record.
        </p>
        <pre className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 text-sm font-mono overflow-x-auto text-green-400">
{`python scripts/seed_master_catalog.py   # catalog -> database
python scripts/full_index_pipeline.py   # BLIP + OCR + CLIP + MiniLM -> Qdrant
python scripts/verify_index.py          # assert counts, vectors and payloads`}
        </pre>
        <p>
          When Qdrant runs in embedded on-disk mode it holds an exclusive lock on the storage directory,
          so the API must run with a single worker. Scale out to Qdrant Cloud with multiple workers and the
          same script needs no changes — only <code>QDRANT_URL</code> moves.
        </p>

        <h2 className="text-xl font-display font-bold text-neutral-100 mt-8">Step 5: Verify, then serve</h2>
        <p>
          Indexing is only finished when verification agrees. <code>scripts/verify_index.py</code> checks
          that every expected meme has a point, that each named vector has the right dimension, and that
          payloads carry the fields the re-ranker reads — including moderation status, so removed memes
          never surface in search.
        </p>
        <p>
          At query time the API only reads: intent parsing, emotion classification, one embedding call,
          one vector search, one re-rank. The expensive work already happened here.
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

  // Unknown slugs are a real 404 rather than an invented article.
  if (!post) {
    notFound();
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
