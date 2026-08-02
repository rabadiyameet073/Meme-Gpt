import React from 'react';

export default function FeaturesPage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold mb-4">Features</h1>
      <ul className="list-disc pl-6 text-slate-300 space-y-2">
        <li>Multimodal CLIP Visual & Text Search</li>
        <li>Instant Copy & Format Conversion (PNG, GIF, MP4)</li>
        <li>Personalized Collections & Saved Library</li>
      </ul>
    </div>
  );
}
