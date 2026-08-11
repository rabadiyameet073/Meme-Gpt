import React from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'violet' | 'emerald' | 'amber';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className,
}) => {
  const base = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
  const variants = {
    default: 'bg-neutral-800 text-neutral-300 border border-neutral-700',
    violet: 'bg-violet-950/60 text-violet-300 border border-violet-800/50',
    emerald: 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/50',
    amber: 'bg-amber-950/60 text-amber-300 border border-amber-800/50',
  };

  return <span className={cn(base, variants[variant], className)}>{children}</span>;
};
