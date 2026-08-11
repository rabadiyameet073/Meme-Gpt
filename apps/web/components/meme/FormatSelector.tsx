'use client';

/**
 * FormatSelector — Global format toggle: GIF | Image | Video
 * Selection persists in localStorage. GIF is default.
 * Sticks to top when scrolling.
 */
import React, { useEffect } from 'react';
import type { FormatPref } from '../../lib/hooks/useMemeSearch';

const STORAGE_KEY = 'memegpt_format_pref';
const FORMATS: { value: FormatPref; label: string; emoji: string }[] = [
  { value: 'gif', label: 'GIF', emoji: '🎞' },
  { value: 'image', label: 'Image', emoji: '🖼' },
  { value: 'video', label: 'Video', emoji: '🎬' },
];

interface FormatSelectorProps {
  value: FormatPref;
  onChange: (format: FormatPref) => void;
}

export function FormatSelector({ value, onChange }: FormatSelectorProps) {
  // Restore persisted preference on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as FormatPref | null;
    if (stored && stored !== value) onChange(stored);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (fmt: FormatPref) => {
    onChange(fmt);
    localStorage.setItem(STORAGE_KEY, fmt);
  };

  return (
    <div
      className="flex items-center gap-1 bg-neutral-900 border border-neutral-800
                 rounded-xl p-1 sticky top-0 z-10 backdrop-blur"
      role="radiogroup"
      aria-label="Select meme format"
    >
      <span className="text-xs text-neutral-500 px-2">Prefer:</span>
      {FORMATS.map((f) => (
        <button
          key={f.value}
          role="radio"
          aria-checked={value === f.value}
          onClick={() => handleChange(f.value)}
          className={`flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg transition-all ${
            value === f.value
              ? 'bg-violet-600 text-white'
              : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800'
          }`}
        >
          <span aria-hidden="true">{f.emoji}</span>
          {f.label}
          {value === f.value && <span className="sr-only">(selected)</span>}
        </button>
      ))}
    </div>
  );
}
