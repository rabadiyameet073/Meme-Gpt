import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import { listMemes, getCategories } from '../../../lib/api';

interface Props {
  params: { category: string };
}

function capitalize(str: string): string {
  if (!str) return '';
  return str
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const catName = capitalize(params.category);
  return {
    title: `${catName} Memes — Download GIF, PNG, MP4 | MemeGPT`,
    description: `Explore the top ${catName} memes. Instant AI search, dialogue quotes, and one-click downloads in GIF, PNG, or MP4 formats.`,
    openGraph: {
      title: `${catName} Memes — MemeGPT`,
      description: `Browse the best trending ${catName} memes on MemeGPT.`,
      url: `https://memegpt.com/memes/${params.category}`,
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: `${catName} Memes | MemeGPT`,
      description: `Browse and download top ${catName} memes.`,
    },
  };
}

export default async function CategoryPage({ params }: Props) {
  const { category } = params;
  const catTitle = capitalize(category);

  let memes: any[] = [];
  let total = 0;

  try {
    const data = await listMemes(category, 1, 40);
    memes = data.items || [];
    total = data.total || memes.length;
  } catch {
    memes = [];
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 pb-20">
      {/* Breadcrumb */}
      <nav
        className="max-w-6xl mx-auto px-4 pt-8 pb-4 text-xs text-neutral-500"
        aria-label="Breadcrumb"
      >
        <ol className="flex items-center gap-2">
          <li>
            <Link href="/" className="hover:text-neutral-300 transition-colors">
              Home
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li>
            <Link href="/memes/reaction" className="hover:text-neutral-300 transition-colors">
              Categories
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li className="text-violet-400 font-medium" aria-current="page">
            {catTitle}
          </li>
        </ol>
      </nav>

      {/* Hero Header */}
      <header className="max-w-6xl mx-auto px-4 py-8 border-b border-neutral-800/80 mb-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <span className="text-xs uppercase font-bold tracking-widest text-violet-400 bg-violet-950/60 border border-violet-800/50 px-3 py-1 rounded-full">
              Category Collection
            </span>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight mt-3 text-white">
              {catTitle} Memes
            </h1>
            <p className="text-neutral-400 mt-2 text-sm max-w-2xl">
              High-quality {catTitle.toLowerCase()} memes matched by sentiment, keywords, and viral potential.
              Free downloads in GIF, PNG, and MP4.
            </p>
          </div>

          <div className="text-sm text-neutral-500">
            Showing <span className="font-semibold text-neutral-200">{memes.length}</span> of{' '}
            <span className="font-semibold text-neutral-200">{total}</span> memes
          </div>
        </div>
      </header>

      {/* Grid Content */}
      <main className="max-w-6xl mx-auto px-4">
        {memes.length === 0 ? (
          <div className="text-center py-20 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-8">
            <span className="text-5xl mb-4 block" aria-hidden="true">
              🎭
            </span>
            <h2 className="text-xl font-bold text-neutral-300">No memes found in this category</h2>
            <p className="text-neutral-500 text-sm mt-2 max-w-md mx-auto">
              We haven't indexed memes under "{category}" yet or the backend service is synchronizing.
            </p>
            <div className="mt-6 flex justify-center gap-3">
              <Link
                href="/"
                className="bg-violet-600 hover:bg-violet-500 text-white font-semibold text-sm px-5 py-2.5 rounded-xl transition-colors"
              >
                Explore All Memes
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {memes.map((m) => {
              const preview = m.gifRef || m.imageRef;
              return (
                <article
                  key={m.id || m.slug}
                  className="bg-neutral-900/60 border border-neutral-800/80 rounded-2xl overflow-hidden hover:border-violet-500/50 transition-all flex flex-col group"
                >
                  <Link href={`/meme/${m.slug}`} className="block relative aspect-video bg-neutral-950 overflow-hidden">
                    {preview ? (
                      <img
                        src={preview}
                        alt={m.name}
                        loading="lazy"
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-neutral-600 text-xs">
                        No Preview
                      </div>
                    )}
                  </Link>

                  <div className="p-4 flex-1 flex flex-col justify-between">
                    <div>
                      <h2 className="font-semibold text-base text-neutral-100 group-hover:text-violet-300 transition-colors line-clamp-1">
                        <Link href={`/meme/${m.slug}`}>{m.name}</Link>
                      </h2>
                      {m.dialogue && (
                        <p className="text-xs text-neutral-400 italic line-clamp-2 mt-1">
                          "{m.dialogue}"
                        </p>
                      )}
                    </div>

                    <div className="mt-4 pt-3 border-t border-neutral-800/60 flex items-center justify-between text-xs">
                      <span className="text-neutral-500 capitalize">{m.category || category}</span>
                      <Link
                        href={`/meme/${m.slug}`}
                        className="text-violet-400 hover:text-violet-300 font-medium transition-colors"
                      >
                        View & Download →
                      </Link>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </main>

      {/* JSON-LD Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'ItemList',
            name: `${catTitle} Memes`,
            description: `Collection of ${catTitle} memes on MemeGPT`,
            itemListElement: memes.map((m, idx) => ({
              '@type': 'ListItem',
              position: idx + 1,
              url: `https://memegpt.com/meme/${m.slug}`,
              name: m.name,
            })),
          }),
        }}
      />
    </div>
  );
}
