'use client';

import React, { useState } from 'react';
import { getTrending } from '../../../lib/api';
import type { MemeResult } from '../../../lib/api';
import { MemeGrid } from '../../../components/meme/MemeGrid';
import { FormatSelector } from '../../../components/meme/FormatSelector';
import type { FormatPref } from '../../../lib/hooks/useMemeSearch';

const CATEGORIES = ['all', 'work', 'gaming', 'relationship', 'tech', 'coding', 'exam', 'general'];

interface TrendingClientProps {
  initialMemes: MemeResult[];
  initialCategory?: string;
}

export function TrendingClient({ initialMemes, initialCategory = 'all' }: TrendingClientProps) {
  const [category, setCategory] = useState(initialCategory);
  const [formatPref, setFormatPref] = useState<FormatPref>('gif');
  const [memes, setMemes] = useState<MemeResult[]>(initialMemes);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCategoryChange = async (cat: string) => {
    setCategory(cat);
    setLoading(true);
    setError('');
    try {
      const data = await getTrending(cat, 20);
      setMemes(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e?.message || 'Failed to update category');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-4">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-neutral-100">
          🔥 <span className="text-amber-400">Trending</span> Memes
        </h1>
        <p className="text-sm text-neutral-500 mt-1">
          Updated hourly via ISR. Top curated memes across categories.
        </p>
      </div>

      {/* Category filter chips */}
      <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by category">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            type="button"
            aria-pressed={category === cat}
            onClick={() => handleCategoryChange(cat)}
            className={`text-xs font-semibold px-3 py-1.5 rounded-full capitalize transition-all ${
              category === cat
                ? 'bg-amber-500 text-black shadow-sm'
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
        <p className="text-sm text-red-400" role="alert">⚠ {error}</p>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
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
      {!loading && (
        <MemeGrid
          memes={memes}
          formatPref={formatPref}
          emptyMessage={`No trending memes in category "${category}" right now.`}
        />
      )}
    </div>
  );
}