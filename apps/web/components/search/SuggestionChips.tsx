'use client';

/**
 * SuggestionChips — Quick search chips shown below search input.
 * Clicking a chip populates and submits the semantic search query.
 * Adheres to WF-02, WF-03, and A11Y-04 (semantic <ul><li> list).
 */
import React, { useState, useEffect } from 'react';

export interface ChipPair {
  label: string;
  query: string;
  emotion?: string;
}

const DEFAULT_CHIP_PAIRS: ChipPair[] = [
  { label: '🐛 Bug finally fixed', query: 'when the bug finally gets fixed after hours' },
  { label: '😤 Monday morning vibe', query: 'Monday morning feeling exhausted and low energy' },
  { label: '🎉 Code worked first try', query: 'my code worked on the first try without bugs' },
  { label: '😭 Exam season', query: 'studying entire syllabus one night before exam panic' },
  { label: '🤦 Meeting could be email', query: 'boss scheduled a meeting that could have been an email' },
  { label: '😴 Friday energy', query: 'waiting for 5pm on Friday ready for the weekend' },
  { label: '🚀 Shipped to prod', query: 'deploying code to production on Friday' },
  { label: '☕ Need caffeine', query: 'need coffee to function today' },
];

interface SuggestionChipsProps {
  onSelect: (query: string) => void;
  chips?: ChipPair[];
}

export function SuggestionChips({ onSelect, chips }: SuggestionChipsProps) {
  const [chipList, setChipList] = useState<ChipPair[]>(chips || DEFAULT_CHIP_PAIRS);

  useEffect(() => {
    if (chips) {
      setChipList(chips);
      return;
    }
    const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    fetch(`${apiBase}/api/v1/chips/suggestions?limit=8`)
      .then((res) => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then((data) => {
        if (data.chips && Array.isArray(data.chips) && data.chips.length > 0) {
          setChipList(data.chips);
        }
      })
      .catch(() => {
        // keep fallback
      });
  }, [chips]);

  return (
    <ul className="flex flex-wrap gap-2 list-none p-0 m-0" aria-label="Search suggestions">
      {chipList.map((chip, idx) => (
        <li key={`${chip.label}-${idx}`}>
          <button
            type="button"
            onClick={() => onSelect(chip.query)}
            className="text-xs bg-neutral-800/80 hover:bg-violet-800/40 border border-neutral-700/80
                       hover:border-violet-500/60 text-neutral-300 hover:text-white
                       px-3.5 py-1.5 rounded-full transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            {chip.label}
          </button>
        </li>
      ))}
    </ul>
  );
}
