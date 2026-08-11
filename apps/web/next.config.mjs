/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow meme images from CDN domains
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.memegpt.com' },
      { protocol: 'https', hostname: 'i.imgflip.com' },
      { protocol: 'https', hostname: 'media.tenor.com' },
      { protocol: 'https', hostname: 'media1.tenor.com' },
      { protocol: 'http', hostname: 'localhost' },
    ],
  },

  async rewrites() {
    // Proxy /api/proxy/* → FastAPI backend during development
    return [
      {
        source: '/api/proxy/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ];
  },
};

export default nextConfig;
