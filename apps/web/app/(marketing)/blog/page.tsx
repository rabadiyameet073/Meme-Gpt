import React from 'react';
import type { Metadata } from 'next';
import Link from 'next/link';
import { BLOG_CATEGORIES, BLOG_POSTS } from '../../../lib/blog';

export const metadata: Metadata = {
  title: 'Blog — MemeGPT | AI Memes, Vector Search & Meme Culture',
  description:
    'Explore MemeGPT engineering insights: AI vector search, emotion detection, meme trends, and how we built an AI-powered meme recommendation engine. Updated regularly.',
  openGraph: {
    title: 'MemeGPT Blog — AI Memes & Engineering',
    description: 'Engineering blog from the team behind the AI meme recommendation engine.',
    type: 'website',
  },
};

const CATEGORIES = BLOG_CATEGORIES;

export default function BlogPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 space-y-16">

      {/* Header */}
      <div className="space-y-4">
        <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">Blog</p>
        <h1 className="text-4xl sm:text-5xl font-display font-extrabold text-gradient leading-tight">
          Engineering, AI &amp; Memes
        </h1>
        <p className="text-neutral-400 text-lg max-w-2xl">
          Deep dives into how MemeGPT works — from AI pipelines to meme culture analysis.
          Written by the team building the AI meme engine.
        </p>
      </div>

      {/* Category filter — static for now, interactive requires client component */}
      <div className="flex flex-wrap gap-2" aria-label="Blog categories">
        {CATEGORIES.map((cat) => (
          <span
            key={cat}
            className={`text-xs font-semibold px-3 py-1.5 rounded-full border transition-all cursor-default
              ${cat === 'All'
                ? 'bg-violet-600/20 border-violet-600/50 text-violet-300'
                : 'bg-neutral-900 border-neutral-800 text-neutral-500'
              }`}
          >
            {cat}
          </span>
        ))}
      </div>

      {/* Featured post */}
      <Link
        href={`/blog/${BLOG_POSTS[0].slug}`}
        className="block group"
        aria-label={`Read: ${BLOG_POSTS[0].title}`}
      >
        <article
          className={`border ${BLOG_POSTS[0].color} rounded-3xl p-8 sm:p-10 space-y-4
                       card-hover hover:border-violet-600/50 transition-all`}
        >
          <div className="flex items-center gap-3">
            <span className="text-4xl" aria-hidden="true">{BLOG_POSTS[0].emoji}</span>
            <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 
                             rounded-full border ${BLOG_POSTS[0].badge} bg-transparent`}>
              {BLOG_POSTS[0].category}
            </span>
            <span className="text-xs text-neutral-600 ml-auto hidden sm:block">✦ Featured</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-display font-bold text-neutral-100 
                          group-hover:text-violet-300 transition-colors leading-snug">
            {BLOG_POSTS[0].title}
          </h2>
          <p className="text-neutral-400 leading-relaxed">{BLOG_POSTS[0].excerpt}</p>
          <div className="flex items-center gap-4 text-xs text-neutral-600 pt-1">
            <span>{BLOG_POSTS[0].date}</span>
            <span>·</span>
            <span>{BLOG_POSTS[0].readTime}</span>
            <span className="ml-auto text-violet-400 font-semibold group-hover:translate-x-1 transition-transform">
              Read →
            </span>
          </div>
        </article>
      </Link>

      {/* Post grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {BLOG_POSTS.slice(1).map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="group block"
            aria-label={`Read: ${post.title}`}
          >
            <article
              className={`h-full border ${post.color} rounded-2xl p-6 space-y-3
                           card-hover hover:border-violet-600/40 transition-all`}
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl" aria-hidden="true">{post.emoji}</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${post.badge} bg-transparent`}>
                  {post.category}
                </span>
              </div>
              <h2 className="font-display font-bold text-neutral-100 leading-snug
                              group-hover:text-violet-300 transition-colors">
                {post.title}
              </h2>
              <p className="text-sm text-neutral-500 leading-relaxed line-clamp-3">
                {post.excerpt}
              </p>
              <div className="flex items-center gap-3 text-xs text-neutral-600 pt-1">
                <span>{post.date}</span>
                <span>·</span>
                <span>{post.readTime}</span>
                <span className="ml-auto text-violet-500 group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </article>
          </Link>
        ))}
      </div>

      {/* CTA */}
      <div className="text-center border-t border-neutral-800 pt-12 space-y-4">
        <p className="text-neutral-500 text-sm">
          Building something with memes? Try the AI search engine.
        </p>
        <Link
          href="/app"
          className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500
                     text-white font-bold px-8 py-4 rounded-2xl text-base
                     transition-all hover:scale-[1.03] active:scale-[0.97]"
        >
          Try MemeGPT free →
        </Link>
      </div>
    </div>
  );
}
