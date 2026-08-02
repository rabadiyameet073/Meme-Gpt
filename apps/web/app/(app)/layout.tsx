import React from 'react';

export default function AppShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 border-r border-slate-800 p-4 hidden md:block">
        <div className="text-xl font-bold text-sky-400 mb-8">MemeGPT App</div>
        <nav className="space-y-2">
          <a href="/app" className="block px-3 py-2 rounded-lg bg-slate-900 text-sky-400 font-medium">Search</a>
          <a href="/app/trending" className="block px-3 py-2 rounded-lg hover:bg-slate-900 text-slate-400">Trending</a>
          <a href="/app/library" className="block px-3 py-2 rounded-lg hover:bg-slate-900 text-slate-400">Library</a>
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
