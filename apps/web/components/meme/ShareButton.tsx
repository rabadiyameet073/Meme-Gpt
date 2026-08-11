'use client';

import React, { useState } from 'react';

interface ShareButtonProps {
  slug: string;
  name: string;
  className?: string;
}

export function ShareButton({ slug, name, className = '' }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleShare = async () => {
    const url = `${window.location.origin}/meme/${slug}`;
    const shareData = { title: `${name} — MemeGPT`, url };

    // Use native share sheet if available (mobile)
    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return;
      } catch {
        // User cancelled or unsupported, fall through to clipboard
      }
    }

    // Fallback: copy link to clipboard
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Silently fail
    }
  };

  return (
    <button
      onClick={handleShare}
      aria-label="Share meme link"
      className={`flex items-center gap-2 bg-neutral-800 hover:bg-neutral-700
                  text-neutral-300 font-semibold text-sm px-4 py-2 rounded-xl transition-all ${className}`}
    >
      {copied ? '✓ Link copied' : '🔗 Share'}
    </button>
  );
}
