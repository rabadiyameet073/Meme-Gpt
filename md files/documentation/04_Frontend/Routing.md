# MemeGPT — Routing

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete routing architecture for MemeGPT — Next.js App Router file-based routing, dynamic segments, and mobile navigation.

---

## Route Table

| Route | File | Rendering | Auth | Purpose |
|---|---|---|---|---|
| `/` | `app/page.tsx` | SSR | None | Landing page + search |
| `/app` | `app/app/page.tsx` | CSR | None | Full search experience |
| `/meme/[slug]` | `app/meme/[slug]/page.tsx` | SSR | None | Meme detail (SEO) |
| `/trending` | `app/trending/page.tsx` | ISR (1h) | None | Trending grid |
| `/about` | `app/about/page.tsx` | SSR | None | About page |
| `/privacy` | `app/privacy/page.tsx` | SSR | None | Privacy policy |
| `/api/health` | `app/api/health/route.ts` | API | None | Health check proxy |

---

## File Structure

```
apps/web/app/
├── layout.tsx          # Root layout (header, footer, fonts)
├── page.tsx            # Homepage (/)
├── globals.css         # Global styles
├── app/
│   └── page.tsx        # Full app page (/app)
├── meme/
│   └── [slug]/
│       └── page.tsx    # Dynamic meme page (/meme/this-is-fine)
├── trending/
│   └── page.tsx        # Trending page (/trending)
├── about/
│   └── page.tsx        # About page (/about)
└── api/
    └── health/
        └── route.ts    # API route handler
```

---

## Dynamic Routes

### `/meme/[slug]` — Server-Side Rendered Meme Pages

```typescript
// app/meme/[slug]/page.tsx
import { Metadata } from 'next'

interface Props {
  params: { slug: string }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const meme = await fetch(`${API_URL}/api/v1/memes/${params.slug}`).then(r => r.json())
  return {
    title: `${meme.name} — MemeGPT`,
    description: `Find and download the ${meme.name} meme in GIF, PNG, or video format.`,
    openGraph: {
      images: [meme.preview_url],
      type: 'article',
    },
  }
}

export default async function MemePage({ params }: Props) {
  const meme = await fetch(`${API_URL}/api/v1/memes/${params.slug}`).then(r => r.json())
  return <MemeDetail meme={meme} />
}
```

### Static Generation for Top Memes

```typescript
export async function generateStaticParams() {
  // Pre-render top 1000 memes at build time
  const memes = await fetch(`${API_URL}/api/v1/trending?limit=1000`).then(r => r.json())
  return memes.results.map((m: any) => ({ slug: m.slug }))
}
```

---

## Mobile Navigation (React Native)

```typescript
// React Native navigation stack
const Stack = createNativeStackNavigator()

function AppNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Search" component={SearchScreen} />
      <Stack.Screen name="MemeDetail" component={MemeDetailScreen} />
      <Stack.Screen name="Trending" component={TrendingScreen} />
    </Stack.Navigator>
  )
}
```

---

## Best Practices

1. **Use App Router** — not Pages Router (deprecated patterns)
2. **SSR for SEO pages** — meme detail pages must be server-rendered
3. **CSR for interactive pages** — search app doesn't need SSR
4. **ISR for trending** — revalidate hourly, not on every request
5. **`generateStaticParams`** for top memes — fastest possible page loads

---

> **Related Documents:**
> - [Frontend_Overview.md](./Frontend_Overview.md) — Frontend architecture
> - [UI_Architecture.md](./UI_Architecture.md) — Layout wireframes
> - [16_SEO_Marketing/SEO_Strategy.md](../16_SEO_Marketing/SEO_Strategy.md) — SEO implementation
