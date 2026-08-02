import React from 'react';

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="p-4 border-b border-slate-800 flex justify-between items-center">
        <div className="text-xl font-bold text-sky-400">MemeGPT</div>
        <nav className="space-x-4">
          <a href="/features" className="hover:underline">Features</a>
          <a href="/download" className="hover:underline">Download</a>
          <a href="/app" className="bg-sky-500 hover:bg-sky-600 px-4 py-2 rounded-lg font-medium">Launch App</a>
        </nav>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="p-4 border-t border-slate-800 text-center text-slate-500">
        © 2026 MemeGPT. All rights reserved.
      </footer>
    </div>
  );
}
