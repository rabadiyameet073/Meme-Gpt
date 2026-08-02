# MemeGPT — Share Feature

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete specification for meme sharing — native share sheet, link generation, clipboard copy, and social media integration.

---

## Share Methods

| Method | Platform | Implementation |
|---|---|---|
| **Native Share** | Mobile (iOS/Android) | Web Share API / React Native Share |
| **Copy Link** | All | Clipboard API |
| **Copy Image** | Desktop | Clipboard API (blob) |
| **Direct Download** | All | CDN redirect |

---

## Share URL Format

```
https://memegpt.com/meme/{slug}?ref={query_id}
```

Example: `https://memegpt.com/meme/this-is-fine?ref=q_xyz789`

- `slug` — SEO-friendly meme identifier
- `ref` — tracks which search led to the share (analytics)

---

## Web Share API Implementation

```typescript
async function shareMeme(meme: MemeResult, queryId: string) {
  const shareUrl = `https://memegpt.com/meme/${meme.slug}?ref=${queryId}`
  
  if (navigator.share) {
    // Native share sheet (mobile + supported browsers)
    try {
      await navigator.share({
        title: `${meme.name} — MemeGPT`,
        text: `Check out this meme: ${meme.name}`,
        url: shareUrl,
      })
      trackFeedback(queryId, meme.id, 'share')
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Share failed:', err)
      }
    }
  } else {
    // Fallback: copy link to clipboard
    await navigator.clipboard.writeText(shareUrl)
    showToast('✓ Link copied to clipboard!')
    trackFeedback(queryId, meme.id, 'copy')
  }
}
```

---

## Copy Image to Clipboard

```typescript
async function copyMemeToClipboard(imageUrl: string) {
  try {
    const response = await fetch(imageUrl)
    const blob = await response.blob()
    await navigator.clipboard.write([
      new ClipboardItem({ [blob.type]: blob })
    ])
    showToast('✓ Meme copied to clipboard!')
  } catch {
    // Fallback: copy URL instead
    await navigator.clipboard.writeText(imageUrl)
    showToast('✓ Link copied (image copy not supported)')
  }
}
```

---

## Analytics Tracking

| Share Action | Signal Weight | Recorded As |
|---|---|---|
| Native share completed | +3.0 | `action: "share"` |
| Link copied | +1.0 | `action: "copy"` |
| Image copied | +1.0 | `action: "copy"` |
| Share cancelled | 0 | Not recorded |

---

## Best Practices

1. **Always check `navigator.share`** — not supported on all browsers
2. **Track shares via `ref` parameter** — understand which searches lead to sharing
3. **Fall back gracefully** — copy link if native share unavailable
4. **Show confirmation toast** — users need feedback that sharing worked
5. **Include meme name in share text** — improves click-through from chat apps

---

> **Related Documents:**
> - [Copy_Download.md](./Copy_Download.md) — Download feature
> - [Smart_Meme_Search.md](./Smart_Meme_Search.md) — Core search
