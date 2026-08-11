import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Features — MemeGPT',
  description:
    'Explore all MemeGPT features: AI intent parsing, emotion detection, vector search, multi-format export, trending feed, mobile app, and privacy-first design.',
};

const FEATURE_SECTIONS = [
  {
    emoji: '🧠',
    title: 'AI Intent Parsing (Groq Llama 3.1)',
    subtitle: 'Understands what you actually mean',
    desc: 'The heart of MemeGPT. When you type, Groq Llama 3.1 8B-Instant analyzes your text in ~300ms and extracts: situation, primary emotion, tone (sarcastic/sincere/humorous), keywords, and the ideal meme format. This is why "my code works and I have no idea why" returns a completely different result from "I fixed the bug finally."',
    details: [
      '7 emotions: joy, anger, sadness, fear, disgust, surprise, neutral',
      '8 tones: sarcastic, sincere, humorous, frustrated, excited, proud, anxious, relatable',
      '6 meme formats: reaction, comparison, advice, relatable, wholesome, achievement, failure',
      'Rule-based fallback when API unavailable — zero downtime',
    ],
    color: 'border-violet-700/40',
    bg: 'bg-violet-900/10',
  },
  {
    emoji: '🔍',
    title: 'Semantic Vector Search (MiniLM + Qdrant)',
    subtitle: 'Find meaning, not just keywords',
    desc: 'Your query is converted into a 384-dimensional semantic vector by sentence-transformers/all-MiniLM-L6-v2. This vector is searched against our Qdrant vector database with a score threshold of 0.40. Semantic search means "tired on a Monday" matches memes about "weekend ending" and "alarm clock dread" — not just memes with those exact words.',
    details: [
      '384-dimensional MiniLM-L6-v2 embeddings (80MB, Apache 2.0)',
      'Qdrant HNSW index — 50ms P99 on cloud tier',
      'Score threshold 0.40 ensures only relevant matches',
      'Local cosine fallback during dev (no Qdrant required)',
    ],
    color: 'border-blue-700/40',
    bg: 'bg-blue-900/10',
  },
  {
    emoji: '💜',
    title: 'Emotion Detection (DistilRoBERTa)',
    subtitle: '100ms emotional intelligence',
    desc: 'j-hartmann/emotion-english-distilroberta-base detects 7 emotions from your text with ~100ms inference on CPU. This emotion signal is used during re-ranking to boost memes with matching emotional tags. If you\'re expressing "frustration", memes tagged with "frustration" and "anger" get a +15% and +8% score boost respectively.',
    details: [
      '250MB model, MIT license, CPU inference',
      'Primary + secondary emotion with confidence score',
      'Rule-based fallback (keyword matching) when model unavailable',
      'Emotion feeds directly into vector query enrichment',
    ],
    color: 'border-pink-700/40',
    bg: 'bg-pink-900/10',
  },
  {
    emoji: '🏆',
    title: 'Business-Logic Re-Ranking',
    subtitle: 'AI picks the winner, business rules perfect it',
    desc: 'After vector search returns top-10 candidates, a re-ranking layer applies business rules before returning top-5 to the user. This is why a popular meme that matches your emotion scores higher than an obscure perfect match — better UX.',
    details: [
      '+15% if primary emotion matches meme emotion tags',
      '+8% if secondary emotion matches',
      '+10% weighted popularity boost (based on viral score)',
      '+5% if user prefers GIF and meme has GIF format',
      'Final score capped at 1.0',
    ],
    color: 'border-amber-700/40',
    bg: 'bg-amber-900/10',
  },
  {
    emoji: '🎞',
    title: 'Multi-Format Export',
    subtitle: 'Every format, instantly',
    desc: 'Every meme is available in 4 formats via Cloudflare R2 CDN. One-click download or copy-to-clipboard for whichever format your platform needs. Format filter lets you search specifically for GIFs when you need animated content.',
    details: [
      'GIF — WhatsApp, Discord, Slack, Telegram',
      'PNG — iMessage, Reddit, Email (up to 2MB)',
      'MP4 — Instagram, TikTok, Reels, Stories',
      'WebP — Web pages (smallest file size)',
      'CDN: cdn.memegpt.com (Cloudflare R2)',
    ],
    color: 'border-green-700/40',
    bg: 'bg-green-900/10',
  },
  {
    emoji: '🔥',
    title: 'Trending Feed',
    subtitle: 'What the world is memeing right now',
    desc: 'Hourly-refreshed trending memes pulled from Reddit (r/memes, r/dankmemes, r/ProgrammerHumor) and filtered by category. Categories: All, Work, Gaming, Relationship, Tech, Coding, Exam, General.',
    details: [
      'Updated every hour via background job',
      '8 categories for focused browsing',
      '30-minute server-side cache for zero-latency loads',
      'Popularity signal updates meme scores in real-time',
    ],
    color: 'border-orange-700/40',
    bg: 'bg-orange-900/10',
  },
  {
    emoji: '🔒',
    title: 'Privacy First',
    subtitle: 'No account, no tracking, no creep',
    desc: 'MemeGPT requires zero registration. All session data is anonymous (UUID-based). We do not store your search queries in any identifiable way. Feedback signals (click, copy, download) are recorded with the meme ID only — not linked to your identity.',
    details: [
      'No email, no password, no registration',
      'Anonymous session UUIDs, not linked to any account',
      'No search query logging to external analytics',
      'GDPR compliant by default — EU-hosted option available',
    ],
    color: 'border-neutral-700/40',
    bg: 'bg-neutral-900/10',
  },
];

export default function FeaturesPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 space-y-16">

      {/* Header */}
      <div className="text-center space-y-4">
        <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">Features</p>
        <h1 className="text-4xl sm:text-5xl font-display font-extrabold text-gradient leading-tight">
          What makes MemeGPT different
        </h1>
        <p className="text-neutral-400 text-lg max-w-2xl mx-auto">
          A full AI pipeline — not just a keyword search engine.
          Every decision is documented below.
        </p>
      </div>

      {/* Feature sections */}
      <div className="space-y-8">
        {FEATURE_SECTIONS.map(({ emoji, title, subtitle, desc, details, color, bg }) => (
          <article
            key={title}
            className={`border ${color} ${bg} rounded-3xl p-7 sm:p-10 space-y-5`}
          >
            <div className="flex items-start gap-5">
              <span className="text-4xl shrink-0">{emoji}</span>
              <div>
                <h2 className="font-display font-bold text-xl text-neutral-100">{title}</h2>
                <p className="text-sm text-neutral-500 mt-0.5">{subtitle}</p>
              </div>
            </div>
            <p className="text-neutral-300 leading-relaxed">{desc}</p>
            <ul className="space-y-2">
              {details.map((d) => (
                <li key={d} className="flex items-start gap-2 text-sm text-neutral-400">
                  <span className="text-violet-500 shrink-0 mt-0.5">✓</span>
                  {d}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      {/* CTA */}
      <div className="text-center py-8 border-t border-neutral-800">
        <Link
          href="/app"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white
                     font-bold px-8 py-4 rounded-2xl text-lg transition-all hover:scale-[1.03]
                     shadow-glow-purple"
        >
          Try all features — it's free →
        </Link>
      </div>
    </div>
  );
}
