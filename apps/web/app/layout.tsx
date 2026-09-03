import React from 'react';
import type { Metadata, Viewport } from 'next';
import { Inter, Space_Grotesk, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: {
    default: 'MemeGPT — AI Meme Finder & Recommender',
    template: '%s | MemeGPT',
  },
  description:
    'Find the perfect meme for any situation using AI. Type anything — a conversation, a feeling, a situation — and get instant meme recommendations. Download GIF, PNG, or MP4.',
  keywords: [
    'AI meme finder', 'meme recommender', 'meme GPT', 'find a meme',
    'meme generator AI', 'best meme for situation', 'download meme GIF',
    'meme search engine', 'funny meme finder',
  ],
  openGraph: {
    type: 'website',
    siteName: 'MemeGPT',
    title: 'MemeGPT — Find the Perfect Meme Instantly with AI',
    description: 'AI-powered meme recommendations. Type anything, get the perfect meme.',
    images: [{ url: '/og-image.jpg', width: 1200, height: 630, alt: 'MemeGPT — AI Meme Finder' }],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@memegpt',
    title: 'MemeGPT — AI Meme Finder',
    description: 'Type anything → get the perfect meme. Download as GIF, PNG, or MP4.',
    images: ['/og-image.jpg'],
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: '#7C3AED',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-neutral-950 text-neutral-100 antialiased min-h-screen font-sans">
        {children}
      </body>
    </html>
  );
}
