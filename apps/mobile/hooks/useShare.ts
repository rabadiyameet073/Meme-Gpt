/**
 * useShare — Native share sheet + download to camera roll.
 * Uses Expo Sharing and Expo FileSystem.
 */
import { useState, useCallback } from 'react';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';
import { getDownloadUrl } from '../lib/api';

type ShareState = 'idle' | 'loading' | 'done' | 'error';

interface UseShareReturn {
  shareState: ShareState;
  downloadState: ShareState;
  share: (slug: string, name: string, memeId?: string | number) => Promise<void>;
  downloadToGallery: (slug: string, format?: 'gif' | 'image', memeId?: string | number) => Promise<void>;
}

export function useShare(): UseShareReturn {
  const [shareState, setShareState] = useState<ShareState>('idle');
  const [downloadState, setDownloadState] = useState<ShareState>('idle');

  const share = useCallback(async (slug: string, name: string, _memeId?: string | number) => {
    setShareState('loading');
    try {
      const url = getDownloadUrl(slug, 'gif');
      const fileUri = (FileSystem.cacheDirectory || '') + `${slug}.gif`;
      await FileSystem.downloadAsync(url, fileUri);

      const isAvailable = await Sharing.isAvailableAsync();
      if (isAvailable) {
        await Sharing.shareAsync(fileUri, {
          mimeType: 'image/gif',
          dialogTitle: `Share ${name}`,
        });
        setShareState('done');
      } else {
        setShareState('error');
      }
    } catch {
      setShareState('error');
    } finally {
      setTimeout(() => setShareState('idle'), 2000);
    }
  }, []);

  const downloadToGallery = useCallback(async (slug: string, format: 'gif' | 'image' = 'gif', _memeId?: string | number) => {
    setDownloadState('loading');
    try {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        setDownloadState('error');
        return;
      }

      const url = getDownloadUrl(slug, format);
      const ext = format === 'gif' ? 'gif' : 'jpg';
      const fileUri = (FileSystem.cacheDirectory || '') + `${slug}.${ext}`;
      await FileSystem.downloadAsync(url, fileUri);
      await MediaLibrary.saveToLibraryAsync(fileUri);
      setDownloadState('done');
    } catch {
      setDownloadState('error');
    } finally {
      setTimeout(() => setDownloadState('idle'), 2000);
    }
  }, []);

  return { shareState, downloadState, share, downloadToGallery };
}
