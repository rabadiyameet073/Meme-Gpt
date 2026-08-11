'use client';

/**
 * MemeCard — Individual meme result card.
 * States: default, hover (card lifts +shadow), downloading.
 * Features: format selector buttons, copy, download, share, thumbs up/down.
 */
import React, { useState } from 'react';
import type { MemeResult } from '../../lib/api';
import { useDownload } from '../../lib/hooks/useDownload';
import type { FormatPref } from '../../lib/hooks/useMemeSearch';

interface MemeCardProps {
  meme: MemeResult;
  activeFormat: FormatPref;
  onFeedback?: (memeId: string, action: string) => void;
}

const EMOTION_EMOJI: Record<string, string> = {
  joy: '😄', frustration: '😤', sadness: '😢', anger: '😠',
  surprise: '😲', fear: '😨', neutral: '😐', humor: '😂',
};

export function MemeCard({ meme, activeFormat, onFeedback }: MemeCardProps) {
  const { downloadState, copyState, download, copyImage, copyLink } = useDownload();
  const [voted, setVoted] = useState<'up' | 'down' | null>(null);

  const previewUrl =
    (activeFormat === 'gif' && meme.formats.gif) ||
    (activeFormat === 'video' && meme.formats.video) ||
    meme.formats.webp ||
    meme.formats.image ||
    meme.preview_url ||
    '/placeholder-meme.png';

  const handleDownload = () => {
    const fmt = activeFormat === 'any' ? 'gif' : activeFormat === 'image' ? 'image' : activeFormat as any;
    download(meme.slug, fmt, meme.id);
    onFeedback?.(meme.id, 'download');
  };

  const handleCopy = () => {
    const src = meme.formats.image || meme.preview_url || '';
    copyImage(src, meme.id);
    onFeedback?.(meme.id, 'copy');
  };

  const handleVote = (dir: 'up' | 'down') => {
    setVoted(dir);
    onFeedback?.(meme.id, dir === 'up' ? 'thumbs_up' : 'thumbs_down');
  };

  const score = Math.round(meme.relevance_score * 100);

  return (
    <article
      className="group bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden
                 hover:border-violet-600/60 hover:-translate-y-1 hover:shadow-2xl hover:shadow-violet-900/20
                 transition-all duration-200"
      aria-label={`Meme: ${meme.name}`}
    >
      {/* Meme image / GIF */}
      <div className="relative w-full aspect-square bg-neutral-800 overflow-hidden">
        <img
          src={previewUrl}
          alt={meme.name}
          loading="lazy"
          className="w-full h-full object-contain"
          onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder-meme.png'; }}
        />
        {/* Relevance score badge */}
        {score > 0 && (
          <span className="absolute top-2 left-2 bg-black/60 text-violet-300 text-xs px-2 py-0.5 rounded-full">
            🎯 {score}%
          </span>
        )}
      </div>

      {/* Card body */}
      <div className="p-3 space-y-2">
        <h3 className="text-sm font-semibold text-neutral-200 truncate">{meme.name}</h3>

        {/* Emotions */}
        {meme.emotions.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {meme.emotions.slice(0, 3).map((em) => (
              <span key={em} className="text-xs text-neutral-500">
                {EMOTION_EMOJI[em] ?? '😶'} {em}
              </span>
            ))}
          </div>
        )}

        {/* Format availability badges */}
        <div className="flex gap-1.5">
          {(['gif', 'image', 'video'] as const).map((fmt) => {
            const available = fmt === 'gif' ? meme.formats.gif : fmt === 'image' ? meme.formats.image : meme.formats.video;
            return (
              <span
                key={fmt}
                title={available ? `${fmt.toUpperCase()} available` : `${fmt.toUpperCase()} not available`}
                className={`text-xs px-1.5 py-0.5 rounded font-mono uppercase ${
                  available
                    ? 'bg-violet-900/40 text-violet-300 border border-violet-700/40'
                    : 'bg-neutral-800 text-neutral-600 border border-neutral-700/40'
                }`}
              >
                {fmt}
              </span>
            );
          })}
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 pt-1">
          {/* Copy */}
          <button
            onClick={handleCopy}
            aria-label="Copy meme to clipboard"
            className="flex-1 flex items-center justify-center gap-1 text-xs bg-neutral-800
                       hover:bg-neutral-700 text-neutral-300 py-1.5 rounded-lg transition-colors"
          >
            {copyState === 'done' ? '✓ Copied' : copyState === 'downloading' ? '…' : '📋 Copy'}
          </button>

          {/* Download */}
          <button
            onClick={handleDownload}
            aria-label="Download meme"
            className="flex-1 flex items-center justify-center gap-1 text-xs bg-violet-700
                       hover:bg-violet-600 text-white py-1.5 rounded-lg transition-colors"
          >
            {downloadState === 'done' ? '✓ Saved' : downloadState === 'downloading' ? '…' : '⬇ Save'}
          </button>

          {/* Thumbs up/down */}
          <button
            onClick={() => handleVote('up')}
            aria-label="Thumbs up"
            className={`p-1.5 rounded-lg transition-colors ${
              voted === 'up' ? 'bg-green-700 text-white' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-400'
            }`}
          >
            👍
          </button>
          <button
            onClick={() => handleVote('down')}
            aria-label="Thumbs down"
            className={`p-1.5 rounded-lg transition-colors ${
              voted === 'down' ? 'bg-red-800 text-white' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-400'
            }`}
          >
            👎
          </button>
        </div>
      </div>
    </article>
  );
}
