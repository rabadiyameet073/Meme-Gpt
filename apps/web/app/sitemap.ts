import type { MetadataRoute } from 'next';
import { BLOG_POSTS } from '../lib/blog';

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || 'https://memegpt.com';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch every meme slug for the dynamic half of the sitemap.
 *
 * This used to be wrapped in a bare `catch {}`, so an unreachable API produced a
 * sitemap of twelve static URLs with no signal at all — the "10,000+ SEO pages"
 * claim quietly became zero. Failures are now logged, and rethrown when
 * SEO_STRICT=true so a broken deploy cannot ship a gutted sitemap silently.
 */
async function fetchMemePages(): Promise<MetadataRoute.Sitemap> {
  const strict = process.env.SEO_STRICT === 'true';
  try {
    const res = await fetch(`${API_URL}/api/v1/memes?limit=50000`, {
      next: { revalidate: 86400 },
    });
    if (!res.ok) {
      throw new Error(`GET /api/v1/memes returned ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    const memes: Array<{ slug?: string; popularity_score?: number; created_at?: string }> =
      Array.isArray(data) ? data : data.items || [];
    const pages = memes
      .filter((meme) => Boolean(meme.slug))
      .map((meme) => ({
        url: `${BASE_URL}/meme/${meme.slug}`,
        changeFrequency: 'monthly' as const,
        priority: Math.min(0.9, 0.5 + (meme.popularity_score || 0) * 0.4),
        lastModified: meme.created_at ? new Date(meme.created_at) : new Date(),
      }));

    if (pages.length === 0) {
      throw new Error('the memes endpoint returned zero slugs');
    }
    return pages;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    console.error(`[sitemap] Failed to expand meme pages from ${API_URL}: ${detail}`);
    if (strict) throw error;
    return [];
  }
}

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
  ];

  // Blog posts — derived from the same list the routes are generated from, so the
  // sitemap can never advertise a slug that has no page.
  const blogPages: MetadataRoute.Sitemap = BLOG_POSTS.map((post) => ({
    url: `${BASE_URL}/blog/${post.slug}`,
    changeFrequency: 'monthly' as const,
    priority: 0.7,
    lastModified: new Date(post.publishedAt),
  }));

  const memePages = await fetchMemePages();

  return [...staticPages, ...blogPages, ...memePages];
}
