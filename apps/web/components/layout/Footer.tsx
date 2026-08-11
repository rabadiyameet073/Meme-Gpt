import React from 'react';
import Link from 'next/link';

const LINKS = {
  Product: [
    { label: 'Search Memes', href: '/app' },
    { label: 'Trending', href: '/app/trending' },
    { label: 'Your Library', href: '/app/library' },
    { label: 'Features', href: '/features' },
    { label: 'Mobile App', href: '/download' },
  ],
  Resources: [
    { label: 'Blog', href: '/blog' },
    { label: 'How It Works', href: '/#how-it-works' },
    { label: 'API (coming soon)', href: '#' },
    { label: 'Changelog', href: '/blog' },
  ],
  Tech: [
    { label: 'Groq LLM', href: 'https://console.groq.com', external: true },
    { label: 'MiniLM Embeddings', href: 'https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2', external: true },
    { label: 'Qdrant Vector DB', href: 'https://qdrant.tech', external: true },
    { label: 'Next.js 14', href: 'https://nextjs.org', external: true },
    { label: 'FastAPI', href: 'https://fastapi.tiangolo.com', external: true },
  ],
};

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-neutral-800/60 mt-20" aria-label="Site footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">

        {/* Main grid */}
        <div className="py-14 grid grid-cols-2 sm:grid-cols-4 gap-8">

          {/* Brand column */}
          <div className="col-span-2 sm:col-span-1 space-y-4">
            <Link
              href="/"
              className="flex items-center gap-2 font-display font-bold text-lg hover:opacity-80 transition-opacity"
              aria-label="MemeGPT home"
            >
              <span className="text-2xl select-none" aria-hidden="true">🃏</span>
              <span>
                <span className="text-gradient">Meme</span>
                <span className="text-neutral-100">GPT</span>
              </span>
            </Link>
            <p className="text-sm text-neutral-500 leading-relaxed max-w-[200px]">
              AI-powered meme recommendations. Type anything, get the perfect meme.
            </p>
            <div className="flex gap-3">
              <a
                href="https://github.com/memegpt"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="MemeGPT on GitHub"
                className="text-neutral-600 hover:text-neutral-300 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </a>
              <a
                href="https://twitter.com/memegpt"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="MemeGPT on Twitter / X"
                className="text-neutral-600 hover:text-neutral-300 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(LINKS).map(([group, links]) => (
            <div key={group} className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-neutral-500">{group}</h3>
              <ul className="space-y-2.5">
                {links.map(({ label, href, external }) => (
                  <li key={label}>
                    {external ? (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors inline-flex items-center gap-1"
                      >
                        {label}
                        <span className="text-neutral-700 text-xs" aria-hidden="true">↗</span>
                      </a>
                    ) : (
                      <Link
                        href={href}
                        className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors"
                      >
                        {label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="border-t border-neutral-900 py-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-neutral-700">
          <p>© {year} MemeGPT. Built with AI, served with humor.</p>
          <div className="flex gap-5">
            <span className="inline-flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" aria-hidden="true" />
              All systems operational
            </span>
            <span>·</span>
            <a
              href="mailto:legal@memegpt.com"
              className="hover:text-neutral-400 transition-colors"
            >
              Legal
            </a>
            <a
              href="mailto:hello@memegpt.com"
              className="hover:text-neutral-400 transition-colors"
            >
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
