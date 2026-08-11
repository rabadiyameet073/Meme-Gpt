import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'MemeGPT — AI Meme Finder & Recommender | Find the Perfect Meme Instantly',
  description:
    'MemeGPT uses AI to find the perfect meme for any situation. Type anything — a conversation, a feeling, a situation — and get instant meme recommendations. Download GIF, PNG, or MP4. Free forever.',
  openGraph: {
    title: 'MemeGPT — Find the Perfect Meme Instantly with AI',
    description: 'AI-powered meme recommendations. Type anything, get the perfect meme.',
  },
};

const FEATURES = [
  {
    emoji: '🧠',
    title: 'Understands Everything',
    desc: 'Context, emotion, sarcasm, cultural nuance — MemeGPT gets the full picture, not just keywords.',
    color: 'from-violet-600/20 to-violet-800/10',
    border: 'border-violet-700/30',
  },
  {
    emoji: '⚡',
    title: 'Under 1.5 Seconds',
    desc: 'AI-powered vector search returns results before you stop thinking about it.',
    color: 'from-amber-600/20 to-amber-800/10',
    border: 'border-amber-700/30',
  },
  {
    emoji: '🎞',
    title: 'Every Format',
    desc: 'GIF, PNG, MP4, WebP — whichever format your platform needs, ready to download or copy.',
    color: 'from-pink-600/20 to-pink-800/10',
    border: 'border-pink-700/30',
  },
  {
    emoji: '📱',
    title: 'Web + Mobile',
    desc: 'Same AI on browser and iOS/Android. Native share sheet on mobile — one tap to WhatsApp.',
    color: 'from-blue-600/20 to-blue-800/10',
    border: 'border-blue-700/30',
  },
  {
    emoji: '🔥',
    title: 'Trending Feed',
    desc: 'Hourly-refreshed trending memes from Reddit, filtered by category.',
    color: 'from-orange-600/20 to-orange-800/10',
    border: 'border-orange-700/30',
  },
  {
    emoji: '🔒',
    title: 'Privacy First',
    desc: 'No account required. No tracking. Anonymous by default. GDPR compliant.',
    color: 'from-green-600/20 to-green-800/10',
    border: 'border-green-700/30',
  },
];

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Type anything',
    desc: '"My boss emailed at 11pm on a Friday" or paste an entire WhatsApp conversation.',
    emoji: '💬',
  },
  {
    step: '02',
    title: 'AI understands',
    desc: 'Groq LLM parses emotion, tone, and context. MiniLM vector model finds the best match.',
    emoji: '🤖',
  },
  {
    step: '03',
    title: 'Get your meme',
    desc: 'Top 5 ranked memes appear in under 1.5 seconds. Download GIF, PNG, or copy to clipboard.',
    emoji: '🎯',
  },
];

const EXAMPLE_SEARCHES = [
  '"My code worked on the first try and I don\'t know why"',
  '"It\'s finally Friday after a 3-day week that felt like 3 years"',
  '"My boss scheduled a meeting that could have been an email"',
  '"I stayed up till 3am fixing one bug"',
  '"The client changed requirements again"',
];

const STATS = [
  { value: '5,000+',   label: 'Memes indexed' },
  { value: '<1.5s',    label: 'Avg response time' },
  { value: '7',        label: 'Emotions detected' },
  { value: '4',        label: 'Export formats' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-base">

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section
        className="relative overflow-hidden pt-20 pb-32 px-4"
        aria-label="Hero section"
        style={{
          background: 'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(124,58,237,0.25) 0%, transparent 60%)',
        }}
      >
        {/* Decorative orbs */}
        <div
          className="absolute top-20 left-1/4 w-72 h-72 rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: 'radial-gradient(circle, #7C3AED, transparent)' }}
          aria-hidden="true"
        />
        <div
          className="absolute top-40 right-1/4 w-56 h-56 rounded-full opacity-8 blur-3xl pointer-events-none"
          style={{ background: 'radial-gradient(circle, #F59E0B, transparent)' }}
          aria-hidden="true"
        />

        <div className="relative max-w-5xl mx-auto text-center space-y-8">
          {/* Badge */}
          <span className="inline-flex items-center gap-2 bg-violet-900/30 border border-violet-700/40
                           text-violet-300 text-xs font-semibold px-4 py-1.5 rounded-full
                           backdrop-blur-sm animate-fade-in">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500" />
            </span>
            AI-Powered Meme Discovery — Free Forever
          </span>

          {/* Headline */}
          <div className="space-y-4">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-display font-extrabold leading-[1.08] tracking-tight">
              Say anything.{' '}
              <br className="hidden sm:block" />
              <span className="text-gradient">
                Get the perfect meme.
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-neutral-400 max-w-2xl mx-auto leading-relaxed">
              MemeGPT understands context, emotion, sarcasm, and cultural nuance to suggest
              the <em className="not-italic text-neutral-200 font-medium">right meme for any moment</em> — instantly.
            </p>
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/app"
              id="hero-cta-primary"
              className="group flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white
                         font-bold px-8 py-4 rounded-2xl text-lg transition-all duration-200
                         hover:scale-[1.03] active:scale-[0.97] shadow-glow-purple"
            >
              Find your meme →
              <span className="group-hover:translate-x-0.5 transition-transform" aria-hidden="true">🃏</span>
            </Link>
            <Link
              href="/download"
              id="hero-cta-secondary"
              className="flex items-center gap-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200
                         font-semibold px-8 py-4 rounded-2xl text-lg border border-neutral-700
                         transition-all hover:border-neutral-600"
            >
              📱 Get the app
            </Link>
          </div>

          <p className="text-xs text-neutral-600">
            No sign-up needed · No credit card · 100% free
          </p>

          {/* Example searches */}
          <div className="pt-4 space-y-3">
            <p className="text-xs text-neutral-600 font-medium uppercase tracking-wider">
              People search for things like...
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {EXAMPLE_SEARCHES.map((q, i) => (
                <Link
                  key={i}
                  href={`/app?q=${encodeURIComponent(q.replace(/"/g, ''))}`}
                  className="text-xs text-neutral-500 hover:text-violet-300 bg-neutral-900
                             border border-neutral-800 hover:border-violet-700/40
                             px-3 py-1.5 rounded-full transition-all duration-150 text-left"
                >
                  {q}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats bar ─────────────────────────────────────────────────────── */}
      <section className="border-y border-neutral-800/60 bg-bg-surface/50 py-8 px-4" aria-label="Key stats">
        <div className="max-w-4xl mx-auto">
          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-8">
            {STATS.map(({ value, label }) => (
              <div key={label} className="text-center">
                <dt className="text-3xl font-display font-bold text-gradient">{value}</dt>
                <dd className="text-xs text-neutral-500 mt-1 font-medium uppercase tracking-wider">{label}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────────────────── */}
      <section className="py-24 px-4" aria-labelledby="how-heading">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16 space-y-3">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">How it works</p>
            <h2
              id="how-heading"
              className="text-3xl sm:text-4xl font-display font-bold text-neutral-100"
            >
              From thought to meme in 3 steps
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
            {/* Connector line on desktop */}
            <div
              className="hidden md:block absolute top-16 left-1/3 right-1/3 h-px bg-gradient-to-r from-violet-600 to-amber-500 opacity-30"
              aria-hidden="true"
            />

            {HOW_IT_WORKS.map(({ step, title, desc, emoji }) => (
              <div
                key={step}
                className="relative bg-bg-surface border border-neutral-800 rounded-3xl p-8 space-y-4
                           hover:border-violet-700/40 transition-colors group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-4xl">{emoji}</span>
                  <span className="font-display font-black text-5xl text-neutral-800 group-hover:text-neutral-700 transition-colors select-none">
                    {step}
                  </span>
                </div>
                <h3 className="text-lg font-display font-bold text-neutral-100">{title}</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features grid ─────────────────────────────────────────────────── */}
      <section
        className="py-24 px-4 bg-bg-surface/30"
        aria-labelledby="features-heading"
      >
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16 space-y-3">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">Features</p>
            <h2 id="features-heading" className="text-3xl sm:text-4xl font-display font-bold">
              Built different
            </h2>
            <p className="text-neutral-400 max-w-xl mx-auto">
              Not just a search engine. A meme intelligence system.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map(({ emoji, title, desc, color, border }) => (
              <article
                key={title}
                className={`relative bg-gradient-to-br ${color} border ${border}
                            rounded-2xl p-6 space-y-3 hover:-translate-y-1 transition-all duration-200 group`}
              >
                <span className="text-3xl animate-float" style={{ display: 'inline-block' }} aria-hidden="true">
                  {emoji}
                </span>
                <h3 className="font-display font-bold text-neutral-100 text-lg">{title}</h3>
                <p className="text-sm text-neutral-400 leading-relaxed">{desc}</p>
              </article>
            ))}
          </div>

          <div className="text-center mt-10">
            <Link
              href="/features"
              className="inline-flex items-center gap-2 text-sm text-violet-400 hover:text-violet-300
                         border border-violet-700/40 hover:border-violet-600/60 px-5 py-2.5
                         rounded-xl transition-all"
            >
              See all features →
            </Link>
          </div>
        </div>
      </section>

      {/* ── AI Pipeline callout ────────────────────────────────────────────── */}
      <section className="py-24 px-4" aria-labelledby="ai-heading">
        <div className="max-w-4xl mx-auto">
          <div className="bg-bg-surface border border-neutral-800 rounded-3xl p-8 sm:p-12 space-y-8">
            <div className="text-center space-y-3">
              <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">Under the hood</p>
              <h2 id="ai-heading" className="text-2xl sm:text-3xl font-display font-bold">
                Real AI. Real results.
              </h2>
            </div>
            <div className="font-mono text-xs sm:text-sm text-neutral-300 space-y-2 bg-neutral-950 rounded-2xl p-6 overflow-x-auto">
              <p><span className="text-violet-400">User Input</span> <span className="text-neutral-600">────────────────────────────────</span></p>
              <p className="pl-4 text-neutral-400">↓</p>
              <p><span className="text-amber-400">Groq Llama 3.1</span> <span className="text-neutral-500">→ emotion, situation, tone, keywords</span></p>
              <p className="pl-4 text-neutral-400">↓</p>
              <p><span className="text-green-400">MiniLM-L6-v2</span> <span className="text-neutral-500">→ 384-dim query vector</span></p>
              <p className="pl-4 text-neutral-400">↓</p>
              <p><span className="text-blue-400">Qdrant vector search</span> <span className="text-neutral-500">→ top-10 candidates</span></p>
              <p className="pl-4 text-neutral-400">↓</p>
              <p><span className="text-pink-400">Re-ranker</span> <span className="text-neutral-500">→ popularity + emotion boost</span></p>
              <p className="pl-4 text-neutral-400">↓</p>
              <p><span className="text-violet-400">Top 5 memes</span> <span className="text-neutral-500">returned in &lt; 1.5s</span></p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Format showcase ────────────────────────────────────────────────── */}
      <section
        className="py-24 px-4 border-t border-neutral-800/60 bg-bg-surface/20"
        aria-labelledby="formats-heading"
      >
        <div className="max-w-4xl mx-auto text-center space-y-10">
          <div className="space-y-3">
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Formats</p>
            <h2 id="formats-heading" className="text-3xl font-display font-bold">Every format you need</h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { fmt: 'GIF', desc: 'WhatsApp, Discord, Slack', emoji: '🎞', size: '≤ 2MB' },
              { fmt: 'PNG', desc: 'iMessage, Reddit, Email', emoji: '🖼', size: '≤ 300KB' },
              { fmt: 'MP4', desc: 'Instagram, TikTok, Stories', emoji: '🎬', size: '≤ 5MB' },
              { fmt: 'WebP', desc: 'Websites, web sharing', emoji: '🌐', size: '≤ 100KB' },
            ].map(({ fmt, desc, emoji, size }) => (
              <div
                key={fmt}
                className="bg-bg-surface border border-neutral-800 hover:border-violet-700/40
                           rounded-2xl p-5 space-y-2 transition-colors"
              >
                <span className="text-2xl" aria-hidden="true">{emoji}</span>
                <p className="font-display font-bold text-neutral-100 text-xl">.{fmt}</p>
                <p className="text-xs text-neutral-500">{desc}</p>
                <p className="text-xs text-neutral-600 font-mono">{size}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ─────────────────────────────────────────────────────── */}
      <section className="py-32 px-4" aria-labelledby="final-cta-heading">
        <div
          className="max-w-3xl mx-auto rounded-3xl p-12 text-center space-y-6 relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, rgba(124,58,237,0.2) 0%, rgba(245,158,11,0.1) 100%)',
            border: '1px solid rgba(124,58,237,0.3)',
          }}
        >
          {/* Glow orb */}
          <div
            className="absolute inset-0 rounded-3xl opacity-30 blur-2xl pointer-events-none"
            style={{ background: 'radial-gradient(circle at 50% 0%, #7C3AED, transparent 60%)' }}
            aria-hidden="true"
          />
          <div className="relative space-y-6">
            <span className="text-6xl animate-float block" aria-hidden="true">🃏</span>
            <h2 id="final-cta-heading" className="text-3xl sm:text-4xl font-display font-extrabold">
              Ready to find your perfect meme?
            </h2>
            <p className="text-neutral-400">
              Zero setup. Zero sign-up. Just type.
            </p>
            <Link
              href="/app"
              id="bottom-cta-button"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                         text-white font-bold px-10 py-4 rounded-2xl text-lg transition-all
                         hover:scale-[1.03] active:scale-[0.97] shadow-glow-purple"
            >
              Start searching — it's free →
            </Link>
            <p className="text-xs text-neutral-600">
              No account needed · 5,000+ memes · GIF, PNG, MP4, WebP
            </p>
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <footer className="border-t border-neutral-800/60 py-10 px-4">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-neutral-600">
          <p>
            <span className="text-violet-400 font-semibold">MemeGPT</span> — AI-powered meme recommendation engine
          </p>
          <nav className="flex gap-5" aria-label="Footer navigation">
            <Link href="/features" className="hover:text-neutral-400 transition-colors">Features</Link>
            <Link href="/download" className="hover:text-neutral-400 transition-colors">Download</Link>
            <Link href="/app" className="hover:text-neutral-400 transition-colors">Web App</Link>
            <Link href="/app/trending" className="hover:text-neutral-400 transition-colors">Trending</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
