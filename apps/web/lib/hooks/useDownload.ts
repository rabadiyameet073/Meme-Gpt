/**
 * useDownload — handles file downloads and clipboard copy.
 * Shows spinner → checkmark feedback pattern as per UI spec.
 */
'use client';

import { useState, useCallback } from 'react';
import { getDownloadUrl, submitFeedback } from '../api';
import { getSessionId } from './useMemeSearch';

export type DownloadFormat = 'gif' | 'image' | 'mp4' | 'webp';
export type DownloadState = 'idle' | 'downloading' | 'done' | 'error';

interface UseDownloadReturn {
  downloadState: DownloadState;
  copyState: DownloadState;
  download: (slug: string, format?: DownloadFormat, memeId?: string) => Promise<void>;
  copyImage: (imageUrl: string, memeId?: string) => Promise<void>;
  copyLink: (slug: string) => Promise<void>;
}

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

export function useDownload(): UseDownloadReturn {
  const [downloadState, setDownloadState] = useState<DownloadState>('idle');
  const [copyState, setCopyState] = useState<DownloadState>('idle');

  const download = useCallback(async (slug: string, format: DownloadFormat = 'gif', memeId?: string) => {
    setDownloadState('downloading');
    try {
      const url = getDownloadUrl(slug, format);
      const res = await fetch(url);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `${slug}.${format === 'image' ? 'png' : format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
      setDownloadState('done');
      if (memeId) submitFeedback({ meme_id: memeId, signal: 'download', action: 'download', session_id: getSessionId() }).catch(() => {});
      setTimeout(() => setDownloadState('idle'), 2000);
    } catch {
      // Fallback direct link
      const fallbackUrl = getDownloadUrl(slug, format);
      window.open(fallbackUrl, '_blank');
      setDownloadState('done');
      setTimeout(() => setDownloadState('idle'), 2000);
    }
  }, []);

  const copyImage = useCallback(async (imageUrl: string, memeId?: string) => {
    setCopyState('downloading');
    try {
      const res = await fetch(imageUrl);
      const rawBlob = await res.blob();
      const pngBlob = await convertToPngBlob(rawBlob);
      await navigator.clipboard.write([new ClipboardItem({ 'image/png': pngBlob })]);
      setCopyState('done');
      if (memeId) submitFeedback({ meme_id: memeId, signal: 'copy', action: 'copy', session_id: getSessionId() }).catch(() => {});

      setTimeout(() => setCopyState('idle'), 2000);
    } catch {
      // Fallback: copy URL
      try {
        await navigator.clipboard.writeText(imageUrl);
        setCopyState('done');
        if (memeId) submitFeedback({ meme_id: memeId, signal: 'copy', action: 'copy', session_id: getSessionId() }).catch(() => {});
      } catch {
        setCopyState('error');
      }
      setTimeout(() => setCopyState('idle'), 2000);
    }
  }, []);
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
