'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_LINKS = [
  { href: '/app',       label: 'Search',   emoji: '🔍' },
  { href: '/trending',  label: 'Trending', emoji: '🔥' },
  { href: '/library',   label: 'Library',  emoji: '📚' },
];

export function Header() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-40 transition-all duration-300 ${
        scrolled
          ? 'glass border-b border-white/5 shadow-lg'
          : 'bg-bg-base/80 backdrop-blur-sm border-b border-neutral-900'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 font-display font-bold text-lg shrink-0
                     hover:opacity-80 transition-opacity"
          aria-label="MemeGPT home"
        >
          <span className="text-2xl select-none" aria-hidden="true">🃏</span>
          <span>
            <span className="text-gradient">Meme</span>
            <span className="text-neutral-100">GPT</span>
          </span>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-0.5" aria-label="Main navigation">
          {NAV_LINKS.map(({ href, label, emoji }) => {
            const isActive = pathname === href || (href !== '/app' && href !== '/' && pathname?.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-1.5 text-sm font-medium px-3 py-1.5 rounded-xl
                            transition-all duration-150 ${
                  isActive
                    ? 'bg-violet-600/20 text-violet-300 border border-violet-600/30'
                    : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/60'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                <span className="text-base" aria-hidden="true">{emoji}</span>
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* CTA — only visible on marketing pages */}
        <div className="flex items-center gap-2 shrink-0">
          {!pathname?.startsWith('/app') && (
            <Link
              href="/app"
              className="hidden sm:flex items-center gap-1.5 bg-violet-600 hover:bg-violet-500
                         text-white text-sm font-semibold px-4 py-1.5 rounded-xl
                         transition-all hover:scale-[1.03] active:scale-95 glow-purple"
            >
              Try free →
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
