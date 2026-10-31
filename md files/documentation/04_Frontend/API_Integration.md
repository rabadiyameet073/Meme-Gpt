# MemeGPT — API Integration (Frontend)

> **Document Version:** 2.0 · **Last Updated:** 2026-08-02

---

## Purpose

Complete guide to how the frontend communicates with the backend API — fetch patterns, error handling, loading states, and the API client module.

---

## API Client Module

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  status: number;
  data: any;
  constructor(status: number, data: any) {
    super(data?.message || `API Error ${status}`)
    this.status = status
    this.data = data
  }
}

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  
  const data = await response.json()
  
  if (!response.ok) {
    throw new ApiError(response.status, data)
  }
  
  return data as T
}

// Exported API functions
export const api = {
  search: (query: string, format: string = 'gif', limit: number = 5) =>
    apiRequest<SearchResponse>('/api/v1/search', {
      method: 'POST',
      body: JSON.stringify({ query, format_preference: format, limit }),
    }),

  getMeme: (slug: string) =>
    apiRequest<MemeDetail>(`/api/v1/memes/${slug}`),

  getTrending: (category: string = 'all', limit: number = 20) =>
    apiRequest<TrendingResponse>(`/api/v1/trending?category=${category}&limit=${limit}`),

  sendFeedback: (queryId: string, memeId: string, action: string) =>
    apiRequest<{ recorded: boolean }>('/api/v1/feedback', {
      method: 'POST',
      body: JSON.stringify({ query_id: queryId, meme_id: memeId, action }),
    }),
}
```

---

## Usage with React Query

```typescript
// In components
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

// Search (mutation — triggered by user action)
const { mutate: search, data, isPending } = useMutation({
  mutationFn: ({ query, format }: { query: string; format: string }) =>
    api.search(query, format),
})

// Trending (query — auto-fetches)
const { data: trending } = useQuery({
  queryKey: ['trending', 'all'],
  queryFn: () => api.getTrending('all'),
  staleTime: 5 * 60 * 1000,  // 5 min cache
})

// Feedback (fire-and-forget)
const { mutate: sendFeedback } = useMutation({
  mutationFn: ({ queryId, memeId, action }: FeedbackParams) =>
    api.sendFeedback(queryId, memeId, action),
})
```

---

## Error Handling in UI

```typescript
// In SearchResults component
if (error) {
  if (error instanceof ApiError) {
    if (error.status === 429) {
      return <RateLimitBanner retryAfter={error.data.retry_after} />
    }
    if (error.status === 503) {
      return <ServiceUnavailable />
    }
  }
  return <GenericError message="Something went wrong. Try again." />
}
```

---

## Best Practices

1. **Centralize API calls** — all fetch calls go through `lib/api.ts`
2. **Use React Query for caching** — don't manually cache in state
3. **Handle errors at the UI level** — show user-friendly messages
4. **Fire-and-forget for feedback** — don't block UI on analytics calls
5. **Use environment variables** — `NEXT_PUBLIC_API_URL` for different environments

---

> **Related Documents:**
> - [State_Management.md](./State_Management.md) — Custom hooks
> - [07_APIs/Search_API.md](../07_APIs/Search_API.md) — Backend API spec
> - [Components.md](./Components.md) — Component implementations
