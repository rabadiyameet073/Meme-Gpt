import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Download MemeGPT — iOS & Android App',
  description:
    'Download MemeGPT for iOS and Android. Get AI meme recommendations with a native share sheet. Find the perfect meme from your phone in under 1.5 seconds.',
};

export default function DownloadPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-20">

      {/* Glow backdrop */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 40% at 50% 20%, rgba(124,58,237,0.12) 0%, transparent 70%)',
        }}
        aria-hidden="true"
      />

      <div className="relative max-w-lg w-full space-y-12 text-center">

        {/* Header */}
        <div className="space-y-4">
          <span className="text-6xl animate-float block">📱</span>
          <h1 className="text-4xl sm:text-5xl font-display font-extrabold">
            MemeGPT{' '}
            <span className="text-gradient">Mobile</span>
          </h1>
          <p className="text-neutral-400 text-lg leading-relaxed">
            The same AI meme engine — now in your pocket.
            Share memes to WhatsApp, Telegram, and Instagram with one tap.
          </p>
        </div>

        {/* App store buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="#"
            id="ios-download-btn"
            aria-label="Download on the App Store (coming soon)"
            className="flex items-center gap-3 bg-bg-surface border border-neutral-700
                       hover:border-violet-600/60 text-neutral-200 font-semibold
                       px-6 py-4 rounded-2xl transition-all hover:scale-[1.02] group"
          >
            <svg className="w-8 h-8 text-neutral-300" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
            </svg>
            <div className="text-left">
              <div className="text-xs text-neutral-500">Download on the</div>
              <div className="text-base font-bold">App Store</div>
            </div>
            <span className="ml-auto text-xs text-amber-500 font-medium">Coming soon</span>
          </a>

          <a
            href="#"
            id="android-download-btn"
            aria-label="Get it on Google Play (coming soon)"
            className="flex items-center gap-3 bg-bg-surface border border-neutral-700
                       hover:border-violet-600/60 text-neutral-200 font-semibold
                       px-6 py-4 rounded-2xl transition-all hover:scale-[1.02] group"
          >
            <svg className="w-8 h-8 text-green-400" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M3 20.5v-17c0-.83.94-1.3 1.6-.8l14 8.5c.6.37.6 1.23 0 1.6l-14 8.5c-.66.5-1.6.03-1.6-.8z" opacity=".3"/>
              <path d="M5 3.77L18.23 12 5 20.23V3.77M3 20.5v-17c0-.83.94-1.3 1.6-.8l14 8.5c.6.37.6 1.23 0 1.6l-14 8.5c-.66.5-1.6.03-1.6-.8z"/>
            </svg>
            <div className="text-left">
              <div className="text-xs text-neutral-500">Get it on</div>
              <div className="text-base font-bold">Google Play</div>
            </div>
            <span className="ml-auto text-xs text-amber-500 font-medium">Coming soon</span>
          </a>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { emoji: '⚡', title: 'Instant search', desc: 'Same AI as web — under 1.5s' },
            { emoji: '📤', title: 'Native share', desc: 'Share directly to any app' },
            { emoji: '💾', title: 'Offline saves', desc: 'Download memes to camera roll' },
          ].map(({ emoji, title, desc }) => (
            <div
              key={title}
              className="bg-bg-surface border border-neutral-800 rounded-2xl p-5 space-y-1.5"
            >
              <span className="text-2xl" aria-hidden="true">{emoji}</span>
              <p className="font-semibold text-neutral-200 text-sm">{title}</p>
              <p className="text-xs text-neutral-500">{desc}</p>
            </div>
          ))}
        </div>

        {/* In the meantime */}
        <div className="bg-bg-surface border border-neutral-800 rounded-2xl p-6 space-y-4">
          <p className="text-sm text-neutral-400">
            <span className="text-neutral-200 font-semibold">In the meantime</span> — the web app works
            great on mobile and is fully installable as a PWA.
          </p>
          <Link
            href="/app"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                       text-white font-semibold px-6 py-3 rounded-xl transition-all
                       hover:scale-[1.02] text-sm"
          >
            Use web app →
          </Link>
        </div>

        <p className="text-xs text-neutral-700">
          Notified when the app launches?{' '}
          <a href="mailto:hello@memegpt.com" className="text-violet-700 hover:text-violet-500 transition-colors">
            Join the waitlist
          </a>
        </p>
      </div>
    </div>
  );
}
