'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const RECENT_SEARCHES_KEY = 'memegpt_recent_searches';

const NAV_LINKS = [
  { href: '/app',      label: 'Search',   emoji: '🔍' },
  { href: '/trending', label: 'Trending', emoji: '🔥' },
  { href: '/library',  label: 'Library',  emoji: '📚' },
];

const SUGGESTION_CHIPS = [
  { label: 'Monday vibe', emoji: '😩' },
  { label: 'Bug in prod',  emoji: '🐛' },
  { label: 'Finally fixed', emoji: '🎉' },
  { label: 'Meeting again', emoji: '😤' },
  { label: 'It works!', emoji: '🚀' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [recent, setRecent] = useState<string[]>([]);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(RECENT_SEARCHES_KEY) || '[]');
      setRecent(Array.isArray(stored) ? stored.slice(0, 8) : []);
    } catch { /* ignore */ }
  }, []);

  return (
    <aside
      className="hidden lg:flex flex-col w-60 shrink-0 border-r border-neutral-800/60
                 bg-bg-surface/50 overflow-y-auto"
      aria-label="Sidebar navigation"
    >
      <div className="flex flex-col gap-6 p-4 h-full">

        {/* Navigation */}
        <nav aria-label="App sections">
          <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 px-2">
            Navigate
          </p>
          <ul className="space-y-0.5">
            {NAV_LINKS.map(({ href, label, emoji }) => {
              const isActive = pathname === href || (href !== '/app' && href !== '/' && pathname?.startsWith(href));
              return (
                <li key={href}>
                  <Link
                    href={href}
                    className={`flex items-center gap-2.5 text-sm font-medium px-3 py-2.5
                                rounded-xl transition-all duration-150 ${
                      isActive
                        ? 'bg-violet-600/15 text-violet-300 border border-violet-600/25'
                        : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
                    }`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <span className="text-lg" aria-hidden="true">{emoji}</span>
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Quick searches */}
        <div>
          <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 px-2">
            Quick search
          </p>
          <div className="flex flex-col gap-1">
            {SUGGESTION_CHIPS.map(({ label, emoji }) => (
              <Link
                key={label}
                href={`/app?q=${encodeURIComponent(label)}`}
                className="flex items-center gap-2 text-xs text-neutral-500 hover:text-neutral-300
                           px-3 py-1.5 rounded-lg hover:bg-neutral-800/50 transition-colors truncate"
              >
                <span aria-hidden="true">{emoji}</span>
                {label}
              </Link>
            ))}
          </div>
        </div>

        {/* Recent searches */}
        {recent.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2 px-2">
              Recent
            </p>
            <ul className="space-y-0.5">
              {recent.map((q, i) => (
                <li key={i}>
                  <Link
                    href={`/app?q=${encodeURIComponent(q)}`}
                    className="flex items-center gap-2 text-xs text-neutral-500 hover:text-neutral-300
                               px-3 py-1.5 rounded-lg hover:bg-neutral-800/50 transition-colors"
                  >
                    <span className="text-neutral-700" aria-hidden="true">🕐</span>
                    <span className="truncate">{q}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer */}
        <div className="mt-auto pt-4 border-t border-neutral-800/60">
          <p className="text-xs text-neutral-600 px-2 leading-relaxed">
            MemeGPT v2.0<br />
            <span className="text-violet-700">AI-powered</span> meme search
          </p>
        </div>
      </div>
    </aside>
  );
}
