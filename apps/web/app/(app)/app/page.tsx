'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { SearchInput } from '../../../components/search/SearchInput';
import { SuggestionChips } from '../../../components/search/SuggestionChips';
import { SearchResults } from '../../../components/search/SearchResults';
import { FormatSelector } from '../../../components/meme/FormatSelector';
import { useMemeSearch, FormatPref } from '../../../lib/hooks/useMemeSearch';

function SearchPageInner() {
  const [formatPref, setFormatPref] = useState<FormatPref>('gif');
  const { results, loading, error, queryId, responseTimeMs, cached, search, sendFeedback } = useMemeSearch(formatPref);
  const searchParams = useSearchParams();

  // Auto-trigger search when ?q= query param is present (e.g. from sidebar chips)
  useEffect(() => {
    const q = searchParams.get('q');
    if (q && q.trim()) {
      search(q.trim());
    }
    // Only run on mount / when q param changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
      {/* Heading */}
      <div>
        <h1 className="text-2xl font-display font-bold text-neutral-100">
          Find the <span className="text-gradient">perfect meme</span>
        </h1>
        <p className="text-sm text-neutral-500 mt-1">
          Type anything — a feeling, a situation, a conversation, a quote.
        </p>
      </div>

      {/* Search input */}
      <SearchInput
        onSearch={search}
        loading={loading}
        error={error}
        placeholder="e.g. 'My boss emailed at 11pm on Friday' or 'when code works first try'"
      />

      {/* Quick suggestion chips — shown when no results yet */}
      {!results.length && !loading && (
        <SuggestionChips onSelect={search} />
      )}

      {/* Format selector */}
      <FormatSelector value={formatPref} onChange={setFormatPref} />

      {/* Results */}
      <SearchResults
        results={results}
        loading={loading}
        queryId={queryId}
        responseTimeMs={responseTimeMs}
        cached={cached}
        formatPref={formatPref}
        onFeedback={sendFeedback}
      />
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="max-w-4xl mx-auto py-4">
        <div className="h-8 w-64 skeleton rounded-lg mb-6" />
        <div className="h-32 skeleton rounded-2xl" />
      </div>
    }>
      <SearchPageInner />
    </Suspense>
  );
}
