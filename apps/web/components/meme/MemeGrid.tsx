import React from 'react';
import { MemeCard, MemeCardProps } from './MemeCard';

export function MemeGrid({ items }: { items: MemeCardProps[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {items.map((item) => (
        <MemeCard key={item.id} {...item} />
      ))}
    </div>
  );
}
