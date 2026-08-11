import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';
import { getMeme, getDownloadUrl } from '../../../lib/api';
import { MemeDetailClient } from './MemeDetailClient';

interface Props {
  params: { slug: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const meme = await getMeme(params.slug);
    const title = meme.name || 'Meme';
    const desc = meme.dialogue || meme.explanation || `Download the ${title} meme as GIF, PNG, or MP4.`;
    const imageUrl = meme.gifRef || meme.imageRef || null;
    return {
      title: `${title} Meme — Download GIF, PNG, MP4 | MemeGPT`,
      description: desc.slice(0, 160),
      openGraph: {
        title: `${title} — MemeGPT`,
        description: desc.slice(0, 160),
        images: imageUrl ? [{ url: imageUrl, alt: title }] : [],
        type: 'article',
      },
      twitter: {
        card: 'summary_large_image',
        title: `${title} — MemeGPT`,
        description: desc.slice(0, 160),
        images: imageUrl ? [imageUrl] : [],
      },
    };
  } catch {
    return {
      title: 'Meme | MemeGPT',
      description: 'Download this meme as GIF, PNG, or MP4.',
    };
  }
}

export default async function MemePage({ params }: Props) {
  const { slug } = params;

  let meme: Awaited<ReturnType<typeof getMeme>> | null = null;
  let error: string | null = null;

  try {
    meme = await getMeme(slug);
  } catch {
    error = 'Meme not found';
  }

  if (error || !meme) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="text-center space-y-4">
          <span className="text-6xl" aria-hidden="true">🤷</span>
          <h1 className="text-2xl font-display font-bold text-neutral-200">Meme not found</h1>
          <p className="text-neutral-500 text-sm">This meme doesn't exist or hasn't been indexed yet.</p>
          <Link
            href="/app"
            className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                       text-white font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
          >
            Search for memes →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Breadcrumb */}
      <nav
        className="max-w-5xl mx-auto px-4 pt-6 pb-2 text-xs text-neutral-600"
        aria-label="Breadcrumb"
      >
        <ol className="flex items-center gap-1.5">
          <li><Link href="/" className="hover:text-neutral-400 transition-colors">Home</Link></li>
          <li aria-hidden="true">/</li>
          <li><Link href="/app" className="hover:text-neutral-400 transition-colors">Search</Link></li>
          <li aria-hidden="true">/</li>
          <li className="text-neutral-400 truncate max-w-[200px]" aria-current="page">{meme.name}</li>
        </ol>
      </nav>

      {/* Main content — client component for interactivity */}
      <MemeDetailClient meme={meme} slug={slug} />

      {/* JSON-LD structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'ImageObject',
            name: meme.name,
            description: meme.dialogue || meme.explanation || '',
            contentUrl: meme.gifRef || meme.imageRef || '',
            url: `https://memegpt.com/meme/${slug}`,
            keywords: (meme.keywords || []).join(', '),
          }),
        }}
      />
    </div>
  );
}
