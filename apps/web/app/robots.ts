import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://memegpt.com';
  return {
    rules: [
      {
        userAgent: '*',
        allow: ['/', '/_next/static/'],
        disallow: ['/api/', '/library', '/app/library'],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
