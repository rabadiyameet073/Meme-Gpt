'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import type { MemeListItem } from '../../../lib/api';
import { getDownloadUrl, submitFeedback } from '../../../lib/api';

interface Props {
  meme: MemeListItem;
  slug: string;
}

const FORMAT_OPTIONS = [
  { key: 'gif',   label: 'GIF',  emoji: '🎞', ext: '.gif' },
  { key: 'image', label: 'PNG',  emoji: '🖼', ext: '.png' },
  { key: 'mp4',   label: 'MP4',  emoji: '🎬', ext: '.mp4' },
  { key: 'webp',  label: 'WebP', emoji: '🌐', ext: '.webp' },
] as const;

type Format = typeof FORMAT_OPTIONS[number]['key'];

export function MemeDetailClient({ meme, slug }: Props) {
  const [selectedFormat, setSelectedFormat] = useState<Format>('gif');
  const [copied, setCopied] = useState(false);
  const [voted, setVoted] = useState<'up' | 'down' | null>(null);

  const previewSrc = meme.gifRef || meme.imageRef || null;
  const downloadUrl = getDownloadUrl(slug, selectedFormat);
  const shareUrl = typeof window !== 'undefined' ? window.location.href : `https://memegpt.com/meme/${slug}`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      submitFeedback({ meme_id: meme.id, signal: 'copy', session_id: 'anonymous' }).catch(() => {});
    } catch { /* ignore */ }
  };

  const handleShare = async () => {
    if (navigator.share) {
      await navigator.share({ title: meme.name, url: shareUrl });
      submitFeedback({ meme_id: meme.id, signal: 'share', session_id: 'anonymous' }).catch(() => {});
    } else {
      handleCopy();
    }
  };

  const handleDownload = () => {
    submitFeedback({ meme_id: meme.id, signal: 'download', session_id: 'anonymous' }).catch(() => {});
  };

  const handleVote = (dir: 'up' | 'down') => {
    if (voted === dir) return;
    setVoted(dir);
    submitFeedback({
      meme_id: meme.id,
      signal: dir === 'up' ? 'thumbs_up' : 'thumbs_down',
      session_id: 'anonymous',
    }).catch(() => {});
  };

  return (
    <main className="max-w-5xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">

        {/* ── Left: Preview ─────────────────────────────────────────────── */}
        <div className="space-y-4">
          <div
            className="relative bg-bg-surface border border-neutral-800 rounded-3xl overflow-hidden
                       flex items-center justify-center min-h-[320px]"
          >
            {previewSrc ? (
              <img
                src={previewSrc}
                alt={meme.name}
                className="max-w-full max-h-[480px] object-contain"
                loading="eager"
              />
            ) : (
              <div className="flex flex-col items-center gap-3 text-neutral-600 p-10">
                <span className="text-6xl" aria-hidden="true">🃏</span>
                <p className="text-sm">Preview not available</p>
              </div>
            )}
          </div>

          {/* Format selector */}
          <div className="flex gap-2" role="radiogroup" aria-label="Select format">
            {FORMAT_OPTIONS.map(({ key, label, emoji, ext }) => (
              <button
                key={key}
                role="radio"
                aria-checked={selectedFormat === key}
                onClick={() => setSelectedFormat(key)}
                className={`flex-1 text-center py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                  selectedFormat === key
                    ? 'bg-violet-600/20 border-violet-600/60 text-violet-300'
                    : 'bg-bg-surface border-neutral-800 text-neutral-500 hover:text-neutral-300 hover:border-neutral-700'
                }`}
              >
                <div className="text-base" aria-hidden="true">{emoji}</div>
                <div>{label}</div>
                <div className="text-neutral-600 font-mono text-[10px]">{ext}</div>
              </button>
            ))}
          </div>

          {/* Action buttons */}
          <div className="flex gap-2">
            <a
              href={downloadUrl}
              download
              onClick={handleDownload}
              id={`download-${selectedFormat}-btn`}
              className="flex-1 flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-500
                         text-white font-bold py-3 rounded-2xl transition-all hover:scale-[1.02]
                         active:scale-[0.97] text-sm shadow-glow-purple"
            >
              ⬇ Download {selectedFormat.toUpperCase()}
            </a>
            <button
              onClick={handleCopy}
              id="copy-link-btn"
              aria-label="Copy share link"
              className="flex items-center gap-1.5 bg-bg-surface hover:bg-bg-hover border border-neutral-800
                         hover:border-neutral-700 text-neutral-300 font-semibold py-3 px-4
                         rounded-2xl transition-all text-sm"
            >
              {copied ? '✓ Copied' : '🔗 Copy'}
            </button>
            <button
              onClick={handleShare}
              id="share-btn"
              aria-label="Share this meme"
              className="flex items-center gap-1.5 bg-bg-surface hover:bg-bg-hover border border-neutral-800
                         hover:border-neutral-700 text-neutral-300 font-semibold py-3 px-4
                         rounded-2xl transition-all text-sm"
            >
              📤 Share
            </button>
          </div>

          {/* Vote */}
          <div className="flex items-center justify-center gap-3 pt-1">
            <span className="text-xs text-neutral-600">Rate this result:</span>
            <button
              onClick={() => handleVote('up')}
              id="upvote-btn"
              aria-pressed={voted === 'up'}
              className={`text-xl transition-all hover:scale-125 active:scale-90 ${
                voted === 'up' ? 'opacity-100' : 'opacity-50 hover:opacity-100'
              }`}
            >
              👍
            </button>
            <button
              onClick={() => handleVote('down')}
              id="downvote-btn"
              aria-pressed={voted === 'down'}
              className={`text-xl transition-all hover:scale-125 active:scale-90 ${
                voted === 'down' ? 'opacity-100' : 'opacity-50 hover:opacity-100'
              }`}
            >
              👎
            </button>
          </div>
        </div>

        {/* ── Right: Info ───────────────────────────────────────────────── */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-neutral-100 leading-tight">
              {meme.name}
            </h1>
            {meme.dialogue && (
              <p className="mt-2 text-neutral-400 leading-relaxed text-sm">
                {meme.dialogue}
              </p>
            )}
          </div>

          {/* Metadata */}
          <div className="bg-bg-surface border border-neutral-800 rounded-2xl divide-y divide-neutral-800/60">
            {meme.category && (
              <div className="px-5 py-3 flex justify-between text-sm">
                <span className="text-neutral-500">Category</span>
                <span className="text-neutral-300 capitalize">{meme.category}</span>
              </div>
            )}
            <div className="px-5 py-3 flex justify-between text-sm">
              <span className="text-neutral-500">Viral score</span>
              <span className="text-amber-400 font-semibold">{meme.viralScore?.toFixed?.(1) ?? '–'} ✨</span>
            </div>
            <div className="px-5 py-3 flex justify-between text-sm">
              <span className="text-neutral-500">Used</span>
              <span className="text-neutral-300">{(meme.usageCount ?? 0).toLocaleString()} times</span>
            </div>
            {meme.createdAt && (
              <div className="px-5 py-3 flex justify-between text-sm">
                <span className="text-neutral-500">Added</span>
                <span className="text-neutral-300">
                  {new Date(meme.createdAt).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                </span>
              </div>
            )}
          </div>

          {/* Keywords */}
          {meme.keywords && meme.keywords.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">Keywords</p>
              <div className="flex flex-wrap gap-1.5">
                {meme.keywords.map((kw) => (
                  <Link
                    key={kw}
                    href={`/app?q=${encodeURIComponent(kw)}`}
                    className="text-xs bg-neutral-900 border border-neutral-800 hover:border-violet-600/40
                               text-neutral-500 hover:text-violet-400 px-2.5 py-1 rounded-full transition-all"
                  >
                    #{kw}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {meme.explanation && (
            <div className="bg-bg-surface border border-neutral-800 rounded-2xl p-5">
              <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-2">About this meme</p>
              <p className="text-sm text-neutral-400 leading-relaxed">{meme.explanation}</p>
            </div>
          )}

          {/* Find similar */}
          <Link
            href="/app"
            className="block w-full text-center bg-bg-elevated hover:bg-bg-hover border border-neutral-800
                       hover:border-violet-700/40 text-neutral-300 font-semibold py-3
                       rounded-2xl transition-all text-sm"
          >
            🔍 Find similar memes
          </Link>
        </div>
      </div>
    </main>
  );
}
