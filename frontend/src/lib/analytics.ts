/**
 * MemeGPT Umami Analytics Tracking Utility
 * Privacy-friendly, cookie-less analytics tracking.
 */
export function trackEvent(eventName: string, data?: Record<string, any>) {
  if (typeof window !== 'undefined' && (window as any).umami) {
    try {
      (window as any).umami.track(eventName, data);
    } catch (e) {
      console.debug('Umami event track failed', e);
    }
  }
}

export function trackMemeSearch(query: string, data?: Record<string, any>) {
  trackEvent('meme_search', { query, ...data });
}

export function trackMemeDownload(memeSlug: string, format: string) {
  trackEvent('meme_download', { meme_slug: memeSlug, format });
}

export function trackMemeShare(memeSlug: string, channel: string = 'web') {
  trackEvent('meme_share', { meme_slug: memeSlug, channel });
}

export function trackMemeFavorite(memeId: string, isFavorite: boolean) {
  trackEvent('meme_favorite', { meme_id: memeId, is_favorite: isFavorite });
}
