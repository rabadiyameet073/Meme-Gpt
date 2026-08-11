import type { MetadataRoute } from 'next';

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://memegpt.com';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Core static pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL,                        changeFrequency: 'daily',   priority: 1.0 },
    { url: `${BASE_URL}/download`,          changeFrequency: 'weekly',  priority: 0.9 },
    { url: `${BASE_URL}/features`,          changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/app`,               changeFrequency: 'daily',   priority: 0.9 },
    { url: `${BASE_URL}/trending`,          changeFrequency: 'hourly',  priority: 0.8 },
    { url: `${BASE_URL}/library`,           changeFrequency: 'weekly',  priority: 0.6 },
    { url: `${BASE_URL}/blog`,              changeFrequency: 'daily',   priority: 0.8 },
    // Blog posts
    { url: `${BASE_URL}/blog/how-ai-finds-the-perfect-meme`,      changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/blog/vector-search-vs-keyword-search-memes`, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/blog/building-memegpt-on-zero-dollars`,    changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/blog/top-memes-for-programmers-2026`,      changeFrequency: 'monthly', priority: 0.6 },
    { url: `${BASE_URL}/blog/emotion-detection-meme-matching`,     changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/blog/meme-data-pipeline-explained`,        changeFrequency: 'monthly', priority: 0.7 },
  ];

  // Dynamic meme pages (10,000+ SEO pages)
  let memePages: MetadataRoute.Sitemap = [];
  try {
    const res = await fetch(`${API_URL}/api/v1/memes?limit=50000`, {
      next: { revalidate: 86400 },
    });
    if (res.ok) {
      const data = await res.json();
      const memes = Array.isArray(data) ? data : data.items || [];
      memePages = memes.map((meme: { slug: string; popularity_score?: number; created_at?: string }) => ({
        url: `${BASE_URL}/meme/${meme.slug}`,
        changeFrequency: 'monthly' as const,
        priority: Math.min(0.9, 0.5 + (meme.popularity_score || 0) * 0.4),
        lastModified: meme.created_at ? new Date(meme.created_at) : new Date(),
      }));
    }
  } catch {
    // Silently skip meme pages if API unavailable during build
  }

  return [...staticPages, ...memePages];
}
