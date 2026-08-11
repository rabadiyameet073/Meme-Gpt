'use client';

import React, { useState, useEffect } from 'react';

interface SavedMeme {
  id: string;
  name: string;
  slug: string;
  preview_url: string | null;
  formats: { gif: string | null; image: string | null };
  collection_name: string;
  saved_at: string;
}

const STORAGE_KEY = 'memegpt_saved_memes';

function getSavedMemes(): SavedMeme[] {
  if (typeof window === 'undefined') return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch {
    return [];
  }
}

function groupByCollection(memes: SavedMeme[]): Record<string, SavedMeme[]> {
  return memes.reduce((acc, m) => {
    const col = m.collection_name || 'Favorites';
    if (!acc[col]) acc[col] = [];
    acc[col].push(m);
    return acc;
  }, {} as Record<string, SavedMeme[]>);
}

export default function LibraryPage() {
  const [saved, setSaved] = useState<SavedMeme[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setSaved(getSavedMemes());
    setMounted(true);
  }, []);

  const removeFromLibrary = (id: string) => {
    const updated = saved.filter((m) => m.id !== id);
    setSaved(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  if (!mounted) return null;

  const grouped = groupByCollection(saved);
  const collections = Object.keys(grouped);

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-4">
      <div>
        <h1 className="text-2xl font-bold text-neutral-100">📚 Your Library</h1>
        <p className="text-sm text-neutral-500 mt-1">
          {saved.length} saved meme{saved.length !== 1 ? 's' : ''} across {collections.length} collection{collections.length !== 1 ? 's' : ''}.
        </p>
      </div>

      {saved.length === 0 && (
        <div className="text-center py-20 text-neutral-500">
          <p className="text-5xl mb-4">📭</p>
          <p className="text-lg font-semibold">No saved memes yet</p>
          <p className="text-sm mt-2">
            Search for memes and save them to your library.
          </p>
          <a
            href="/app"
            className="inline-block mt-4 bg-violet-600 hover:bg-violet-500 text-white
                       font-semibold px-5 py-2.5 rounded-xl text-sm transition-colors"
          >
            Search memes →
          </a>
        </div>
      )}

      {collections.map((col) => (
        <section key={col} aria-label={`Collection: ${col}`}>
          <h2 className="text-lg font-semibold text-neutral-200 mb-3">{col}</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {grouped[col].map((meme) => (
              <div
                key={meme.id}
                className="group relative bg-neutral-900 border border-neutral-800
                           rounded-xl overflow-hidden hover:border-violet-600/50 transition-all"
              >
                <div className="w-full h-36 bg-neutral-800 overflow-hidden">
                  <img
                    src={meme.formats.gif || meme.formats.image || meme.preview_url || ''}
                    alt={meme.name}
                    className="w-full h-full object-contain"
                    onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder-meme.png'; }}
                  />
                </div>
                <div className="p-2">
                  <p className="text-xs font-medium text-neutral-300 truncate">{meme.name}</p>
                </div>
                {/* Remove button on hover */}
                <button
                  onClick={() => removeFromLibrary(meme.id)}
                  aria-label={`Remove ${meme.name} from library`}
                  className="absolute top-1.5 right-1.5 bg-black/60 hover:bg-red-600
                             text-neutral-400 hover:text-white text-xs px-1.5 py-0.5
                             rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
