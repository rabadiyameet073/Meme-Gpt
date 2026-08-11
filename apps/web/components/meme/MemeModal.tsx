'use client';

import React, { useEffect } from 'react';
import type { MemeResult } from '../../lib/api';
import { DownloadButton } from './DownloadButton';
import { ShareButton } from './ShareButton';

interface MemeModalProps {
  meme: MemeResult;
  onClose: () => void;
}

export function MemeModal({ meme, onClose }: MemeModalProps) {
  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  const imgSrc = meme.formats.gif || meme.formats.image || meme.preview_url || '';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={meme.name}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-neutral-900 border border-neutral-700 rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-800">
          <h2 className="font-bold text-neutral-100">{meme.name}</h2>
          <button
            onClick={onClose}
            aria-label="Close"
            className="text-neutral-400 hover:text-neutral-200 text-xl"
          >
            ✕
          </button>
        </div>

        {/* Image */}
        <div className="bg-neutral-950 flex items-center justify-center p-4 min-h-64">
          <img src={imgSrc} alt={meme.name} className="max-w-full max-h-96 object-contain" />
        </div>

        {/* Actions */}
        <div className="p-4 flex flex-wrap gap-2">
          <DownloadButton slug={meme.slug} format="gif" memeId={meme.id} label="⬇ GIF" />
          <DownloadButton slug={meme.slug} format="image" memeId={meme.id} label="⬇ Image" />
          <ShareButton slug={meme.slug} name={meme.name} />
        </div>

        {/* Metadata */}
        {meme.categories.length > 0 && (
          <div className="px-4 pb-4 flex flex-wrap gap-1">
            {meme.categories.map((c) => (
              <span key={c} className="text-xs bg-neutral-800 text-neutral-400 px-2 py-0.5 rounded-full">
                {c}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
