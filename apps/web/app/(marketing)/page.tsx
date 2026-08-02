import React from 'react';

export default function LandingPage() {
  return (
    <div className="container mx-auto px-4 py-20 text-center">
      <h1 className="text-5xl font-extrabold mb-6 bg-gradient-to-r from-sky-400 to-indigo-500 bg-clip-text text-transparent">
        Find the Exact Meme for Every Vibe
      </h1>
      <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-8">
        Powered by AI embeddings, Groq LLMs, and instant Qdrant vector search.
      </p>
      <a href="/app" className="inline-block bg-sky-500 hover:bg-sky-600 px-8 py-4 rounded-xl text-lg font-bold">
        Start Searching Now 🚀
      </a>
    </div>
  );
}
