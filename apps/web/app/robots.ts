import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/app/library'],
    },
    sitemap: 'https://memegpt.com/sitemap.xml',
  };
}
