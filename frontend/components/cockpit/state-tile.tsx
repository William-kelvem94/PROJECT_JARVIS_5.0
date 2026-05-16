'use client';

import type { ComponentType } from 'react';
import { cn } from '@/lib/shadcn/utils';

export function StateTile({
  icon: Icon,
  label,
  value,
  active,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
  active?: boolean;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <Icon className={cn('mb-2 size-4', active ? 'text-emerald-200' : 'text-slate-500')} />
      <div className="text-[11px] text-slate-500 uppercase">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-100">{value}</div>
    </div>
  );
}
