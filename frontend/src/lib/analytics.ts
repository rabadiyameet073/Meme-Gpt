/**
 * MemeGPT Umami Analytics Tracking Utility
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
