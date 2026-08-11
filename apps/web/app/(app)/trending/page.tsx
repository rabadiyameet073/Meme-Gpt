'use client';

import React, { useState, useEffect } from 'react';
import { getTrending } from '../../../lib/api';
import type { MemeResult } from '../../../lib/api';
import { MemeGrid } from '../../../components/meme/MemeGrid';
import { FormatSelector } from '../../../components/meme/FormatSelector';
import type { FormatPref } from '../../../lib/hooks/useMemeSearch';

const CATEGORIES = ['all', 'work', 'gaming', 'relationship', 'tech', 'coding', 'exam', 'general'];

export default function TrendingPage() {
  const [category, setCategory] = useState('all');
  const [formatPref, setFormatPref] = useState<FormatPref>('gif');
  const [memes, setMemes] = useState<MemeResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    getTrending(category, 20)
      .then((data) => setMemes(Array.isArray(data) ? data : []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-100">
          🔥 <span className="text-amber-400">Trending</span> Memes
        </h1>
        <p className="text-sm text-neutral-500 mt-1">
          Updated hourly. Top memes across categories.
        </p>
      </div>

      {/* Category filter chips */}
      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filter by category">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            role="tab"
            aria-selected={category === cat}
            onClick={() => setCategory(cat)}
            className={`text-xs font-semibold px-3 py-1.5 rounded-full capitalize transition-all
              ${category === cat
                ? 'bg-amber-500 text-black'
                : 'bg-neutral-800 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-700'
              }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Format selector */}
      <FormatSelector value={formatPref} onChange={setFormatPref} />

      {/* Error */}
      {error && (
        <p className="text-sm text-red-400">⚠ {error}</p>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden animate-pulse">
              <div className="w-full h-48 bg-neutral-800" />
              <div className="p-3 space-y-2">
                <div className="h-3 w-2/3 bg-neutral-800 rounded" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      {!loading && memes.length > 0 && (
        <MemeGrid results={memes} formatPref={formatPref} />
      )}

      {!loading && !error && memes.length === 0 && (
        <div className="text-center py-16 text-neutral-500">
          <p className="text-4xl mb-3">🦗</p>
          <p>No trending memes yet. Run the data pipeline first.</p>
          <code className="text-xs text-neutral-600 mt-2 block">
            python scripts/download_datasets.py
          </code>
        </div>
      )}
    </div>
  );
}
