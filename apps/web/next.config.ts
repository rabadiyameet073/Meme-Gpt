import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.memegpt.com',
      },
      {
        protocol: 'https',
        hostname: 'i.imgflip.com',
      },
    ],
  },
};

export default nextConfig;
