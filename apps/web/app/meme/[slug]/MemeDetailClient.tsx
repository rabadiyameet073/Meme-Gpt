'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import type { MemeListItem, MemeResult } from '../../../lib/api';
import { getDownloadUrl, submitFeedback, getRelatedMemes, toggleFavorite } from '../../../lib/api';
import { getSessionId } from '../../../lib/hooks/useMemeSearch';

async function convertToPngBlob(blob: Blob): Promise<Blob> {
  if (blob.type === 'image/png') return blob;
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth || img.width;
      canvas.height = img.naturalHeight || img.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        resolve(blob);
        return;
      }
      ctx.drawImage(img, 0, 0);
      canvas.toBlob((pngBlob) => {
        resolve(pngBlob || blob);
      }, 'image/png');
    };
    img.onerror = () => resolve(blob);
    img.src = URL.createObjectURL(blob);
  });
}

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
  const [relatedMemes, setRelatedMemes] = useState<MemeResult[]>([]);
  const [loadingRelated, setLoadingRelated] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem('memegpt_saved_memes') || '[]');
      setIsFavorite(saved.some((m: any) => m.id === meme.id || m.slug === slug));
    } catch {}
  }, [meme.id, slug]);

  const handleToggleFavorite = () => {
    try {
      const saved = JSON.parse(localStorage.getItem('memegpt_saved_memes') || '[]');
      let updated;
      if (isFavorite) {
        updated = saved.filter((m: any) => m.id !== meme.id && m.slug !== slug);
        setIsFavorite(false);
      } else {
        if (saved.length >= 200) {
          alert('Favorites collection limit reached (200 memes). Please remove some before adding more.');
          return;
        }
        const newEntry = {
          id: meme.id,
          name: meme.name,
          slug,
          preview_url: meme.gifRef || meme.imageRef || null,
          formats: { gif: meme.gifRef || null, image: meme.imageRef || null },
          collection_name: 'Favorites',
          saved_at: new Date().toISOString(),
        };
        updated = [newEntry, ...saved];
        setIsFavorite(true);
      }
      localStorage.setItem('memegpt_saved_memes', JSON.stringify(updated));
      toggleFavorite(meme.id, getSessionId()).catch(() => {});
    } catch {}
  };

  useEffect(() => {
    let active = true;
    setLoadingRelated(true);
    getRelatedMemes(slug, 8)
      .then((res) => {
        if (active) setRelatedMemes(res);
      })
      .catch(() => {})
      .finally(() => {
        if (active) setLoadingRelated(false);
      });
    return () => {
      active = false;
    };
  }, [slug]);

  const previewSrc = meme.gifRef || meme.imageRef || null;
  const downloadUrl = getDownloadUrl(slug, selectedFormat);
  const shareUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/meme/${slug}?ref=share_detail`
    : `https://memegpt.com/meme/${slug}?ref=share_detail`;

  const handleCopy = async () => {
    try {
      if (previewSrc) {
        const res = await fetch(previewSrc);
        const rawBlob = await res.blob();
        const pngBlob = await convertToPngBlob(rawBlob);
        await navigator.clipboard.write([new ClipboardItem({ 'image/png': pngBlob })]);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        submitFeedback({ meme_id: meme.id, signal: 'copy', session_id: getSessionId() }).catch(() => {});
        return;
      }
    } catch {
      // Fall through to share URL
    }

    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      submitFeedback({ meme_id: meme.id, signal: 'copy', session_id: getSessionId() }).catch(() => {});
    } catch { /* ignore */ }
  };

  const handleShare = async () => {
    if (navigator.share) {
      await navigator.share({ title: meme.name, url: shareUrl });
      submitFeedback({ meme_id: meme.id, signal: 'share', session_id: getSessionId() }).catch(() => {});
    } else {
      handleCopy();
    }
  };

  const handleDownload = () => {
    submitFeedback({ meme_id: meme.id, signal: 'download', session_id: getSessionId() }).catch(() => {});
  };

  const handleVote = (dir: 'up' | 'down') => {
    if (voted === dir) return;
    setVoted(dir);
    submitFeedback({
      meme_id: meme.id,
      signal: dir === 'up' ? 'thumbs_up' : 'thumbs_down',
      session_id: getSessionId(),
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
            <button
              onClick={handleToggleFavorite}
              id="favorite-btn"
              aria-label={isFavorite ? 'Remove from favorites' : 'Save to favorites'}
              className={`flex items-center gap-1.5 border font-semibold py-3 px-4 rounded-2xl transition-all text-sm ${
                isFavorite
                  ? 'bg-rose-950/40 border-rose-600/60 text-rose-300 hover:bg-rose-900/50'
                  : 'bg-bg-surface hover:bg-bg-hover border-neutral-800 hover:border-neutral-700 text-neutral-300'
              }`}
            >
              {isFavorite ? '❤️ Saved' : '🤍 Save'}
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

      {/* ── Cultural Origin & Usage Guide ────────────────────────────────────── */}
      <section className="mt-16 bg-bg-surface border border-neutral-800 rounded-3xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center gap-2">
          <span className="text-xl" aria-hidden="true">📖</span>
          <h2 className="text-xl font-display font-bold text-neutral-100">Origin & Cultural Context</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-neutral-300 leading-relaxed">
          <div className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-violet-400">Background & Evolution</h3>
            <p className="text-neutral-400">
              {meme.explanation || `The "${meme.name}" meme emerged as an internet staple expressing iconic shared emotions across social platforms and online communities.`}
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-amber-400">How & When to Use</h3>
            <p className="text-neutral-400">
              Best deployed when reacting to sudden surprises, ironic dilemmas, or relatable daily life situations in Discord, Slack, or social threads.
            </p>
          </div>
        </div>
      </section>

      {/* ── Related Memes Carousel ───────────────────────────────────────────── */}
      {relatedMemes.length > 0 && (
        <section className="mt-16 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-display font-bold text-neutral-100 flex items-center gap-2">
                <span>⚡ Related Memes</span>
              </h2>
              <p className="text-xs text-neutral-500 mt-0.5">Memes sharing similar emotional undertones and comedic timing.</p>
            </div>
            <Link href="/app" className="text-xs text-violet-400 hover:text-violet-300 font-semibold">
              Browse all →
            </Link>
          </div>

          <div className="flex gap-4 overflow-x-auto pb-4 snap-x">
            {relatedMemes.map((item) => (
              <Link
                key={item.id}
                href={`/meme/${item.slug}`}
                className="min-w-[200px] max-w-[220px] shrink-0 snap-start bg-bg-surface border border-neutral-800 hover:border-violet-600/60 rounded-2xl overflow-hidden transition-all hover:-translate-y-1 group"
              >
                <div className="w-full h-32 bg-neutral-900 overflow-hidden flex items-center justify-center">
                  <img
                    src={item.preview_url || item.formats?.image || item.formats?.gif || '/placeholder-meme.svg'}
                    alt={item.name}
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                </div>
                <div className="p-3">
                  <h3 className="text-xs font-bold text-neutral-200 truncate group-hover:text-violet-300 transition-colors">
                    {item.name}
                  </h3>
                  <div className="flex items-center justify-between mt-2 text-[10px] text-neutral-500">
                    <span className="capitalize">{item.category}</span>
                    {item.viralScore > 0 && <span className="text-amber-400">✨ {item.viralScore.toFixed(1)}</span>}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
