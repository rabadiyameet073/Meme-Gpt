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
import { Badge } from '../ui/Badge';
import { MemeModal } from './MemeModal';

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
  const [modalOpen, setModalOpen] = useState(false);
  const [isFav, setIsFav] = useState(false);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('memegpt_saved_memes') || '[]');
      setIsFav(saved.some((m: any) => m.id === meme.id || m.slug === meme.slug));
    } catch {}
  }, [meme.id, meme.slug]);

  const handleToggleFav = () => {
    try {
      const saved = JSON.parse(localStorage.getItem('memegpt_saved_memes') || '[]');
      let updated;
      if (isFav) {
        updated = saved.filter((m: any) => m.id !== meme.id && m.slug !== meme.slug);
        setIsFav(false);
      } else {
        if (saved.length >= 200) {
          alert('Favorites collection limit reached (200 memes).');
          return;
        }
        const newEntry = {
          id: meme.id,
          name: meme.name,
          slug: meme.slug,
          preview_url: previewUrl,
          formats: { gif: meme.formats.gif, image: meme.formats.image },
          collection_name: 'Favorites',
          saved_at: new Date().toISOString(),
        };
        updated = [newEntry, ...saved];
        setIsFav(true);
      }
      localStorage.setItem('memegpt_saved_memes', JSON.stringify(updated));
      onFeedback?.(meme.id, 'favorite');
    } catch {}
  };

  const previewUrl =
    (activeFormat === 'gif' && meme.formats.gif) ||
    (activeFormat === 'video' && meme.formats.video) ||
    meme.formats.webp ||
    meme.formats.image ||
    meme.preview_url ||
    '/placeholder-meme.svg';

  const handleDownload = () => {
    const fmt = activeFormat === 'any' ? 'gif' : activeFormat === 'image' ? 'image' : activeFormat as any;
    download(meme.slug, fmt);
    onFeedback?.(meme.id, 'download');
  };

  const handleCopy = () => {
    const src = meme.formats.image || meme.preview_url || '';
    copyImage(src);
    onFeedback?.(meme.id, 'copy');
  };

  const handleVote = (dir: 'up' | 'down') => {
    setVoted(dir);
    onFeedback?.(meme.id, dir === 'up' ? 'thumbs_up' : 'thumbs_down');
  };

  const score = Math.round(meme.relevance_score * 100);

  return (
    <>
      <article
        className="group bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden
                   hover:border-violet-600/60 hover:-translate-y-1 hover:shadow-2xl hover:shadow-violet-900/20
                   transition-all duration-200"
        aria-label={`Meme: ${meme.name}`}
      >
        {/* Meme image / GIF */}
        <div
          onClick={() => setModalOpen(true)}
          className="relative w-full aspect-square bg-neutral-800 overflow-hidden cursor-pointer"
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter') setModalOpen(true); }}
          aria-label={`Expand ${meme.name}`}
        >
          <img
            src={previewUrl}
            alt={(meme as any).alt_text || (meme as any).altText || meme.name}
            loading="lazy"
            className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
            onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder-meme.svg'; }}
          />
          {/* Relevance score badge */}
          {score > 0 && (
            <div className="absolute top-2 left-2">
              <Badge variant="violet" className="bg-black/70 backdrop-blur-sm">
                🎯 {score}%
              </Badge>
            </div>
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
                <Badge
                  key={fmt}
                  variant={available ? 'violet' : 'default'}
                  className="font-mono uppercase text-[10px] px-1.5 py-0.5"
                >
                  {fmt}
                </Badge>
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

          {/* Favorite */}
          <button
            onClick={handleToggleFav}
            aria-label={isFav ? 'Remove from favorites' : 'Save to favorites'}
            className={`p-1.5 rounded-lg transition-colors ${
              isFav ? 'bg-rose-900/60 text-rose-300 border border-rose-700/60' : 'bg-neutral-800 hover:bg-neutral-700 text-neutral-400'
            }`}
          >
            {isFav ? '❤️' : '🤍'}
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
    {modalOpen && <MemeModal meme={meme} onClose={() => setModalOpen(false)} />}
  </>
  );
}
