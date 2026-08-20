/**
 * MemeGPT — Clipboard, Share and Download Utilities
 * Specifications: 08_Features/Copy_Download.md & 08_Features/Share_Feature.md
 */

export interface MemeAsset {
  id: string;
  name: string;
  slug?: string;
  dialogue?: string;
  share_url?: string;
  formats?: {
    image?: string;
    gif?: string;
    video?: string;
    webp?: string;
  };
}

/**
 * Share Meme using Web Share API or Clipboard Fallback.
 * Adheres to 08_Features/Share_Feature.md
 */
export async function shareMeme(
  meme: MemeAsset,
  queryId?: string,
  onToast?: (msg: string) => void,
  onTrackFeedback?: (queryId: string, memeId: string, action: string) => void
): Promise<"share" | "copy" | "cancelled" | false> {
  const slug = meme.slug || meme.id || "meme";
  const shareUrl = `https://memegpt.com/meme/${slug}${queryId ? `?ref=${queryId}` : ""}`;

  if (navigator.share) {
    // Native share sheet (mobile + supported browsers)
    try {
      await navigator.share({
        title: `${meme.name} — MemeGPT`,
        text: `Check out this meme: ${meme.name}`,
        url: shareUrl,
      });
      if (onTrackFeedback && queryId) {
        onTrackFeedback(queryId, meme.id, "share");
      }
      return "share";
    } catch (err: any) {
      if (err?.name === "AbortError") {
        // User cancelled share
        return "cancelled";
      }
      console.error("Native share failed:", err);
    }
  }

  // Fallback: copy link to clipboard
  try {
    await navigator.clipboard.writeText(shareUrl);
    if (onToast) {
      onToast("✓ Link copied to clipboard!");
    }
    if (onTrackFeedback && queryId) {
      onTrackFeedback(queryId, meme.id, "copy");
    }
    return "copy";
  } catch {
    return false;
  }
}

/**
 * Copy meme image data to clipboard (blob), or fallback to URL copy.
 */
export async function copyMemeImageToClipboard(
  imageUrl: string,
  onToast?: (msg: string) => void
): Promise<boolean> {
  try {
    const response = await fetch(imageUrl);
    const blob = await response.blob();
    await navigator.clipboard.write([
      new ClipboardItem({ [blob.type]: blob }),
    ]);
    if (onToast) {
      onToast("✓ Meme copied to clipboard!");
    }
    return true;
  } catch {
    // Fallback: copy URL instead
    try {
      await navigator.clipboard.writeText(imageUrl);
      if (onToast) {
        onToast("✓ Link copied (image copy not supported)");
      }
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Copy meme to clipboard using Method 1 (Image Blob) or Method 2 (Share URL text fallback).
 * Returns 'image' if image copied, 'url' if text URL copied, or false if failed.
 */
export async function copyMemeToClipboard(meme: MemeAsset): Promise<"image" | "url" | false> {
  const imageUrl = meme.formats?.image;
  const shareUrl = meme.share_url || `https://memegpt.com/meme/${meme.slug || meme.id}`;

  try {
    // Method 1: Copy image data (Chrome, Edge, Safari 14+)
    if (imageUrl) {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      await navigator.clipboard.write([
        new ClipboardItem({ [blob.type]: blob }),
      ]);
      return "image";
    }
  } catch {
    // Fallback to Method 2
  }

  try {
    // Method 2: Fallback — copy share URL
    await navigator.clipboard.writeText(shareUrl);
    return "url";
  } catch {
    return false;
  }
}

/**
 * Download meme file in specific format (image/png, gif, video/mp4, webp).
 */
export function downloadMeme(meme: MemeAsset, format: string = "image"): string {
  const formats = meme.formats || {};
  const ext = format === "image" ? "png" : format;
  const targetUrl = formats[format as keyof typeof formats] || formats.image || "#";
  const slug = meme.slug || meme.id || "meme";
  const filename = `${slug}.${ext}`;

  const link = document.createElement("a");
  link.href = targetUrl;
  link.download = filename;
  link.target = "_blank";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  return filename;
}
