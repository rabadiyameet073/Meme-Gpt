/**
 * useDownload — handles file downloads and clipboard copy.
 * Shows spinner → checkmark feedback pattern as per UI spec.
 */
'use client';

import { useState, useCallback } from 'react';
import { getDownloadUrl, submitFeedback } from '../api';

export type DownloadFormat = 'gif' | 'image' | 'mp4' | 'webp';
export type DownloadState = 'idle' | 'downloading' | 'done' | 'error';

interface UseDownloadReturn {
  downloadState: DownloadState;
  copyState: DownloadState;
  download: (slug: string, format?: DownloadFormat, memeId?: string) => Promise<void>;
  copyImage: (imageUrl: string, memeId?: string) => Promise<void>;
  copyLink: (slug: string) => Promise<void>;
}

export function useDownload(): UseDownloadReturn {
  const [downloadState, setDownloadState] = useState<DownloadState>('idle');
  const [copyState, setCopyState] = useState<DownloadState>('idle');

  const download = useCallback(async (slug: string, format: DownloadFormat = 'gif', memeId?: string) => {
    setDownloadState('downloading');
    try {
      const url = getDownloadUrl(slug, format);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${slug}.${format === 'image' ? 'jpg' : format}`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setDownloadState('done');
      if (memeId) submitFeedback({ meme_id: memeId, action: 'download' }).catch(() => {});
      setTimeout(() => setDownloadState('idle'), 2000);
    } catch {
      setDownloadState('error');
      setTimeout(() => setDownloadState('idle'), 2000);
    }
  }, []);

  const copyImage = useCallback(async (imageUrl: string, memeId?: string) => {
    setCopyState('downloading');
    try {
      const res = await fetch(imageUrl);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
      setCopyState('done');
      if (memeId) submitFeedback({ meme_id: memeId, action: 'copy' }).catch(() => {});
      setTimeout(() => setCopyState('idle'), 2000);
    } catch {
      // Fallback: copy URL
      try {
        await navigator.clipboard.writeText(imageUrl);
        setCopyState('done');
        setTimeout(() => setCopyState('idle'), 2000);
      } catch {
        setCopyState('error');
        setTimeout(() => setCopyState('idle'), 2000);
      }
    }
  }, []);

  const copyLink = useCallback(async (slug: string) => {
    const base = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';
    const url = `${base}/meme/${slug}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopyState('done');
      setTimeout(() => setCopyState('idle'), 2000);
    } catch {
      setCopyState('error');
      setTimeout(() => setCopyState('idle'), 2000);
    }
  }, []);

  return { downloadState, copyState, download, copyImage, copyLink };
}
