# MemeGPT — Copy & Download Feature

> **Document Version:** 1.0 · **Last Updated:** 2026-08-02

---

## Purpose

Feature specification for the one-click copy-to-clipboard and download functionality.

---

## Copy to Clipboard

### Implementation

```typescript
async function copyMemeToClipboard(meme: Meme): Promise<boolean> {
  try {
    // Method 1: Copy image data (Chrome, Edge, Safari 14+)
    const response = await fetch(meme.formats.image);
    const blob = await response.blob();
    await navigator.clipboard.write([
      new ClipboardItem({ [blob.type]: blob })
    ]);
    return true;
  } catch {
    try {
      // Method 2: Fallback — copy share URL
      await navigator.clipboard.writeText(meme.share_url);
      return true;
    } catch {
      return false;
    }
  }
}
```

### Platform Support

| Platform | Image Copy | URL Fallback |
|---|---|---|
| Chrome 76+ | ✅ | ✅ |
| Edge 79+ | ✅ | ✅ |
| Safari 14.1+ | ✅ | ✅ |
| Firefox | ❌ (security policy) | ✅ |
| Mobile Safari | ✅ (iOS 16+) | ✅ |
| Mobile Chrome | ✅ | ✅ |

---

## Download

### Implementation

```typescript
function downloadMeme(meme: Meme, format: string): void {
  const url = meme.formats[format];
  const filename = `${meme.slug}.${format}`;
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
```

### User Flow

```
1. User sees meme in results
2. Clicks [📋 Copy] → Image data copied to clipboard → Toast: "✓ Copied!"
3. Or clicks [⬇ Download] → File downloads → Toast: "✓ Downloaded!"
4. Or clicks format button [GIF] [PNG] → Downloads in that format
5. User pastes/sends in WhatsApp, Slack, Discord
```

---

## Analytics Tracking

| Action | Signal | Tracked? |
|---|---|---|
| Copy (image) | `copy` (+1.0) | ✅ via Feedback API |
| Copy (URL fallback) | `copy` (+0.5) | ✅ |
| Download | `download` (+2.0) | ✅ |
| Format switch | `format_change` (+0.1) | ✅ |

---

> **Related Documents:**
> - [Smart_Meme_Search.md](./Smart_Meme_Search.md) · [04_Frontend/Components.md](../04_Frontend/Components.md)
