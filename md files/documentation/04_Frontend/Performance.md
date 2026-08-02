# MemeGPT — Frontend Performance

> **Document Version:** 1.0 · **Last Updated:** 2026-08-01

---

## Core Web Vitals Targets

| Metric | Target | Strategy |
|---|---|---|
| **LCP** | <2.5s | CDN thumbnails, Next.js Image, lazy loading |
| **FID** | <100ms | No blocking scripts, code splitting |
| **CLS** | <0.1 | Fixed aspect-ratio meme cards, font preloading |
| **TTFB** | <600ms | Vercel Edge Network, static generation |
| **FCP** | <1.8s | Minimal critical CSS, server rendering |

## Optimization Techniques

### 1. Image Optimization
- WebP thumbnails (300x300) for search results
- Lazy loading with `loading="lazy"` below fold
- BlurHash placeholder during load
- CDN-served (Cloudflare) — edge cached globally

### 2. Code Splitting
```typescript
// Lazy load non-critical routes
const Trending = lazy(() => import('./pages/Trending'));
const Library = lazy(() => import('./pages/Library'));
```

### 3. Bundle Size Budget
| Chunk | Max Size | Actual |
|---|---|---|
| Initial JS | 100KB gzipped | ~80KB |
| CSS | 30KB gzipped | ~20KB |
| Vendor chunk | 80KB gzipped | ~60KB |

### 4. Caching Strategy
- Static assets: `Cache-Control: public, max-age=31536000, immutable`
- Meme pages: `s-maxage=3600, stale-while-revalidate=86400`
- API responses: No cache (dynamic)

---

> **Related Documents:**
> - [Frontend_Overview.md](./Frontend_Overview.md) · [12_Deployment/Frontend_Deployment.md](../12_Deployment/Frontend_Deployment.md)
