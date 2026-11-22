import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'About MemeGPT — The AI Meme Recommendation Engine',
  description: 'Learn how MemeGPT uses modern semantic search and natural language understanding to bridge human humor with artificial intelligence.',
  openGraph: {
    title: 'About MemeGPT — The AI Meme Recommendation Engine',
    description: 'Learn how MemeGPT bridges human humor and AI semantic intelligence.',
  },
};

const ARCHITECTURE_STEPS = [
  {
    step: '01',
    title: 'Semantic Vector Embeddings',
    tech: 'all-MiniLM-L6-v2',
    description:
      'We encode multi-modal cultural context, emotional subtext, and dialogue transcripts into 384-dimensional dense vectors.',
  },
  {
    step: '02',
    title: 'Sub-Millisecond Vector Search',
    tech: 'Qdrant Vector DB',
    description:
      'Cosine similarity indexing allows instant recall across thousands of curated viral memes with pgvector and Redis hybrid caching.',
  },
  {
    step: '03',
    title: 'Intent & Emotion Parsing',
    tech: 'Groq LLaMA 3.3',
    description:
      'Ultra-fast inference extracts situation context, primary emotion, and sarcasm nuance within 80 milliseconds.',
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-bg-base text-neutral-100 py-16 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto space-y-16">
        {/* Header */}
        <section className="text-center space-y-4">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-violet-950/60 text-violet-300 border border-violet-800/40">
            ✨ The Meme Intelligence Mission
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-extrabold tracking-tight">
            Humor is human. <br />
            <span className="text-gradient">We teach AI to get the joke.</span>
          </h1>
          <p className="text-lg text-neutral-400 max-w-2xl mx-auto leading-relaxed">
            MemeGPT was born out of frustration with keyword-based meme search engines that return literal images of cats
            when what you really wanted was an expression of quiet existential dread on a Tuesday afternoon.
          </p>
        </section>

        {/* Narrative Section */}
        <section className="bg-neutral-900/60 border border-neutral-800/80 rounded-3xl p-8 sm:p-10 space-y-6">
          <h2 className="text-2xl font-display font-bold text-neutral-100">
            Why Traditional Search Fails at Memes
          </h2>
          <p className="text-neutral-300 leading-relaxed text-sm sm:text-base">
            Memes are emotional shorthand. They carry complex situational irony, shared trauma, inside jokes, and cultural zeitgeist
            that simple keyword tags like <code className="bg-neutral-800 px-2 py-0.5 rounded text-amber-300">"dog"</code> or{' '}
            <code className="bg-neutral-800 px-2 py-0.5 rounded text-amber-300">"coffee"</code> completely miss.
          </p>
          <p className="text-neutral-300 leading-relaxed text-sm sm:text-base">
            When you type <em>"my unit tests passed in CI but failed in production"</em>, MemeGPT evaluates the frustration,
            disbelief, and technical resonance to match you with Disaster Girl or the Two Buttons dilemma—not a literal picture
            of a software manual.
          </p>
        </section>

        {/* Architecture Grid */}
        <section className="space-y-6">
          <h2 className="text-2xl font-display font-bold text-neutral-100 text-center">
            How The Pipeline Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {ARCHITECTURE_STEPS.map((item) => (
              <div
                key={item.step}
                className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-6 flex flex-col justify-between hover:border-violet-600/40 transition-colors"
              >
                <div className="space-y-3">
                  <div className="text-xs font-mono text-violet-400 font-bold">{item.step}</div>
                  <h3 className="font-bold text-neutral-100">{item.title}</h3>
                  <p className="text-xs text-neutral-400 leading-relaxed">{item.description}</p>
                </div>
                <div className="mt-4 pt-4 border-t border-neutral-800 text-[11px] font-mono text-neutral-500">
                  ⚡ Powered by {item.tech}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Call to action */}
        <section className="text-center py-10 bg-gradient-to-b from-transparent to-violet-950/20 rounded-3xl border border-violet-900/20 p-8 space-y-4">
          <h3 className="text-2xl font-display font-bold">Ready to find your reaction?</h3>
          <p className="text-sm text-neutral-400">Experience zero-latency emotional search right now.</p>
          <Link
            href="/app"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white font-bold px-8 py-3.5 rounded-2xl transition-all hover:scale-[1.02] shadow-glow-purple text-sm"
          >
            Launch Web App →
          </Link>
        </section>
      </div>
    </div>
  );
}

