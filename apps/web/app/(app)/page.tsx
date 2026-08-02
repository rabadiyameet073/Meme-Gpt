import React from 'react';

export default function SearchAppPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Meme Search</h1>
      <div className="flex gap-2">
        <input 
          type="text" 
          placeholder="Describe your vibe (e.g. 'Monday morning coding bug')..." 
          className="flex-1 bg-slate-900 border border-slate-700 px-4 py-3 rounded-xl focus:outline-none focus:border-sky-500 text-slate-100"
        />
        <button className="bg-sky-500 hover:bg-sky-600 font-bold px-6 py-3 rounded-xl">Search</button>
      </div>
    </div>
  );
}
