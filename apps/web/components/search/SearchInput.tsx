'use client';

/**
 * SearchInput — Main text input component.
 * States: empty, typing (char count), loading (animated border), error.
 * Max length: 2000 chars. Supports Cmd/Ctrl+Enter.
 */
import React, { useState, useRef, useEffect } from 'react';

interface SearchInputProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  error?: string | null;
  placeholder?: string;
  maxLength?: number;
}

export function SearchInput({
  onSearch,
  loading = false,
  error = null,
  placeholder = "What's happening? Type anything...",
  maxLength = 2000,
}: SearchInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    const q = value.trim();
    if (!q || loading) return;
    onSearch(q);
  };

  const borderClass = error
    ? 'border-red-500 focus-within:border-red-400'
    : loading
    ? 'border-violet-500 animate-pulse'
    : 'border-neutral-700 focus-within:border-violet-500';

  return (
    <div className="w-full space-y-2">
      <div className={`relative bg-neutral-900 border-2 rounded-2xl transition-colors ${borderClass}`}>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, maxLength))}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={3}
          disabled={loading}
          aria-label="Meme search input"
          className="w-full bg-transparent px-4 pt-4 pb-12 text-neutral-100 placeholder-neutral-500
                     resize-none focus:outline-none text-base leading-relaxed"
        />

        {/* Character count + submit button */}
        <div className="absolute bottom-3 left-4 right-3 flex items-center justify-between">
          <span className={`text-xs ${value.length > maxLength * 0.9 ? 'text-amber-400' : 'text-neutral-600'}`}>
            {value.length > 0 ? `${value.length} / ${maxLength}` : ''}
          </span>
          <button
            onClick={handleSubmit}
            disabled={!value.trim() || loading}
            aria-label="Search for meme"
            className="flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-40
                       disabled:cursor-not-allowed text-white text-sm font-semibold px-4 py-2
                       rounded-xl transition-all"
          >
            {loading ? (
              <>
                <span className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                Finding your meme...
              </>
            ) : (
              <>
                Search
                <kbd className="hidden sm:inline text-xs opacity-60 font-mono">⌘↵</kbd>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <p role="alert" className="text-sm text-red-400 px-1">
          ⚠ {error}
        </p>
      )}
    </div>
  );
}
