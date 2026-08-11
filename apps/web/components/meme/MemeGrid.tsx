'use client';

import React from 'react';
import { MemeCard } from './MemeCard';
import type { MemeResult } from '../../lib/api';
import type { FormatPref } from '../../lib/hooks/useMemeSearch';

interface MemeGridProps {
  results: MemeResult[];
  formatPref: FormatPref;
  onFeedback?: (memeId: string, action: string) => void;
}

export function MemeGrid({ results, formatPref, onFeedback }: MemeGridProps) {
  if (!results.length) return null;

  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
      role="list"
      aria-label="Meme search results"
    >
      {results.map((meme) => (
        <div key={meme.id} role="listitem">
          <MemeCard meme={meme} activeFormat={formatPref} onFeedback={onFeedback} />
        </div>
      ))}
    </div>
  );
}
