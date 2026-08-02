import React from 'react';

export interface MemeCardProps {
  id: string;
  title: string;
  imageUrl: string;
}

export function MemeCard({ title, imageUrl }: MemeCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-sky-500 transition">
      <img src={imageUrl} alt={title} className="w-full h-48 object-cover" />
      <div className="p-3">
        <h3 className="text-sm font-semibold text-slate-200 truncate">{title}</h3>
      </div>
    </div>
  );
}
