import React from 'react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'MemeGPT — AI Conversational Meme Engine',
  description: 'Search, create, and share the perfect meme using AI.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
