'use client';

/**
 * SuggestionChips — Quick search chips shown below search input.
 * Clicking a chip populates and submits the search.
 */
import React from 'react';

const DEFAULT_CHIPS = [
  '🐛 When the bug finally gets fixed',
  '😤 Monday morning vibes',
  '🎉 My code worked first try',
  '😭 Exam szn be like',
  '🤦 Boss scheduled a meeting',
  '😴 Friday afternoon energy',
];

interface SuggestionChipsProps {
  onSelect: (query: string) => void;
  chips?: string[];
}

export function SuggestionChips({ onSelect, chips = DEFAULT_CHIPS }: SuggestionChipsProps) {
  return (
    <div className="flex flex-wrap gap-2" role="list" aria-label="Search suggestions">
      {chips.map((chip) => (
        <button
          key={chip}
          role="listitem"
          onClick={() => onSelect(chip)}
          className="text-xs bg-neutral-800 hover:bg-violet-800/50 border border-neutral-700
                     hover:border-violet-500 text-neutral-400 hover:text-neutral-200
                     px-3 py-1.5 rounded-full transition-all"
        >
          {chip}
        </button>
      ))}
    </div>
  );
}
