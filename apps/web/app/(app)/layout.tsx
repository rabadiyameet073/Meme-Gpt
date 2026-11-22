import React from 'react';
import Link from 'next/link';
import { Header } from '../../components/layout/Header';
import { Sidebar } from '../../components/layout/Sidebar';

export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden pb-14 lg:pb-0">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation Bar (RWD-01) */}
      <nav
        className="lg:hidden fixed bottom-0 left-0 right-0 h-14 bg-bg-surface/90 backdrop-blur-md border-t border-neutral-800 flex items-center justify-around z-40"
        aria-label="Mobile app navigation"
      >
        <Link
          href="/app"
          className="flex flex-col items-center justify-center text-xs text-neutral-400 hover:text-neutral-100 min-h-[44px] min-w-[44px]"
        >
          <span className="text-base" aria-hidden="true">🔍</span>
          <span>Search</span>
        </Link>
        <Link
          href="/trending"
          className="flex flex-col items-center justify-center text-xs text-neutral-400 hover:text-neutral-100 min-h-[44px] min-w-[44px]"
        >
          <span className="text-base" aria-hidden="true">🔥</span>
          <span>Trending</span>
        </Link>
        <Link
          href="/library"
          className="flex flex-col items-center justify-center text-xs text-neutral-400 hover:text-neutral-100 min-h-[44px] min-w-[44px]"
        >
          <span className="text-base" aria-hidden="true">📚</span>
          <span>Library</span>
        </Link>
      </nav>
    </div>
  );
}
