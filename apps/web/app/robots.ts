import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: '*', allow: '/' },
      { userAgent: '*', disallow: ['/api/', '/app/library', '/_next/'] },
    ],
    sitemap: `${process.env.NEXT_PUBLIC_APP_URL || 'https://memegpt.com'}/sitemap.xml`,
  };
}
