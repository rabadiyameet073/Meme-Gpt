import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Privacy Policy — MemeGPT',
  description: 'MemeGPT privacy policy: transparency on zero-surveillance search, data retention, and content rights.',
  openGraph: {
    title: 'Privacy Policy — MemeGPT',
    description: 'Learn how MemeGPT respects user privacy and protects intellectual property.',
  },
};

export default function PrivacyPage() {
  const lastUpdated = 'November 10, 2026';

  return (
    <div className="min-h-screen bg-bg-base text-neutral-100 py-16 px-4 sm:px-6">
      <div className="max-w-3xl mx-auto space-y-12">
        {/* Header */}
        <div className="space-y-3 border-b border-neutral-800 pb-8">
          <span className="text-xs font-semibold uppercase tracking-wider text-violet-400">Legal & Transparency</span>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-neutral-100">
            Privacy Policy
          </h1>
          <p className="text-xs text-neutral-500 font-mono">Last updated: {lastUpdated}</p>
        </div>

        {/* Content sections */}
        <div className="space-y-8 text-neutral-300 text-sm leading-relaxed">
          <section className="space-y-3">
            <h2 className="text-lg font-bold text-neutral-100">1. Our Commitment to Zero Surveillance</h2>
            <p>
              MemeGPT is built to be a utility, not an advertising network. You do not need to register, provide an email address,
              or link a social identity to search, preview, or download memes. We do not sell your personal data to data brokers
              or use your search history to build tracking profiles across the web.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-neutral-100">2. Information We Collect</h2>
            <ul className="list-disc pl-5 space-y-2 text-neutral-400">
              <li>
                <strong className="text-neutral-200">Anonymous Session IDs:</strong> Random UUIDs stored in browser cookies or local storage
                to enable features like vote deduplication, favorite collections, and conversational query refinement.
              </li>
              <li>
                <strong className="text-neutral-200">Search Queries:</strong> Text input submitted to our search bar. Queries are vectorized
                and analyzed anonymously to improve ranking models and populate our Redis cache. Queries are retained for a maximum of 30 days.
              </li>
              <li>
                <strong className="text-neutral-200">Usage Interactions:</strong> Anonymous signals such as meme downloads, copy actions, and upvotes/downvotes
                used exclusively to recalculate meme virality scores.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-neutral-100">3. Infrastructure & Third-Party Processors</h2>
            <p>
              To deliver sub-second responses globally, we utilize trusted infrastructure providers:
            </p>
            <ul className="list-disc pl-5 space-y-2 text-neutral-400">
              <li><strong className="text-neutral-200">Cloudflare R2:</strong> Edge distribution and storage for static GIF, PNG, WebP, and MP4 files.</li>
              <li><strong className="text-neutral-200">Groq:</strong> Low-latency LLM inference for natural language semantic parsing without data retention.</li>
              <li><strong className="text-neutral-200">Qdrant Cloud:</strong> Managed vector indexing for embedding similarity calculations.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-neutral-100">4. DMCA & Intellectual Property</h2>
            <p>
              MemeGPT indexes publicly available internet culture and user-submitted memes. If you believe your copyrighted work
              is indexed without appropriate license or fair use attribution, please submit an expedited takedown notice to{' '}
              <a href="mailto:legal@memegpt.com" className="text-violet-400 hover:underline">
                legal@memegpt.com
              </a>{' '}
              or via our designated takedown endpoint. Verified notices result in prompt removal within 24 hours.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-bold text-neutral-100">5. GDPR & User Rights</h2>
            <p>
              Under European General Data Protection Regulation (GDPR) and California Consumer Privacy Act (CCPA), you retain the right
              to request deletion of any session data or audit records tied to your IP hash or anonymous identifier. Contact our privacy
              team at <a href="mailto:privacy@memegpt.com" className="text-violet-400 hover:underline">privacy@memegpt.com</a>.
            </p>
          </section>
        </div>

        {/* Back Link */}
        <div className="pt-8 border-t border-neutral-800">
          <Link href="/" className="text-xs text-neutral-400 hover:text-neutral-200 transition-colors">
            ← Return to MemeGPT Home
          </Link>
        </div>
      </div>
    </div>
  );
}
