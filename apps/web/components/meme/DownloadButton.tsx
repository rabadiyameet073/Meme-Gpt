'use client';

import React from 'react';
import { useDownload, DownloadFormat } from '../../lib/hooks/useDownload';

interface DownloadButtonProps {
  slug: string;
  format?: DownloadFormat;
  memeId?: string;
  label?: string;
  className?: string;
}

export function DownloadButton({ slug, format = 'gif', memeId, label, className = '' }: DownloadButtonProps) {
  const { downloadState, download } = useDownload();

  return (
    <button
      onClick={() => download(slug, format, memeId)}
      disabled={downloadState === 'downloading'}
      aria-label={`Download ${format.toUpperCase()}`}
      className={`flex items-center gap-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-60
                  text-white font-semibold text-sm px-4 py-2 rounded-xl transition-all ${className}`}
    >
      {downloadState === 'downloading' && (
        <span className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
      )}
      {downloadState === 'done' ? '✓ Saved' : label || `⬇ ${format.toUpperCase()}`}
    </button>
  );
}
