'use client';

import React from 'react';
import { MemeGrid } from '../meme/MemeGrid';
import type { MemeResult } from '../../lib/api';
import type { FormatPref } from '../../lib/hooks/useMemeSearch';

interface SearchResultsProps {
  results: MemeResult[];
  loading: boolean;
  queryId: string | null;
  responseTimeMs: number | null;
  cached: boolean;
  formatPref: FormatPref;
  onFeedback?: (memeId: string, action: string) => void;
}

export function SearchResults({
  results,
  loading,
  queryId,
  responseTimeMs,
  cached,
  formatPref,
  onFeedback,
}: SearchResultsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden animate-pulse">
            <div className="w-full h-48 bg-neutral-800" />
            <div className="p-3 space-y-2">
              <div className="h-3 w-2/3 bg-neutral-800 rounded" />
              <div className="h-3 w-1/2 bg-neutral-800 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!results.length) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-neutral-500">
        <span>{results.length} result{results.length !== 1 ? 's' : ''}</span>
        <span>
          {responseTimeMs != null ? `${responseTimeMs}ms` : ''}
          {cached && <span className="ml-2 text-violet-400">⚡ cached</span>}
        </span>
      </div>
      <MemeGrid results={results} formatPref={formatPref} onFeedback={onFeedback} />
    </div>
  );
}
