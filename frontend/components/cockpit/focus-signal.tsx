'use client';

import type { ComponentType } from 'react';
import { cn } from '@/lib/shadcn/utils';

export function FocusSignal({
  label,
  value,
  icon: Icon,
  active,
}: {
  label: string;
  value: string;
  icon: ComponentType<{ className?: string }>;
  active?: boolean;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <div className="mb-3 flex items-center justify-between">
        <Icon className={cn('size-4', active ? 'text-cyan-200' : 'text-slate-500')} />
        <span className={cn('size-2 rounded-full', active ? 'bg-emerald-300' : 'bg-slate-600')} />
      </div>
      <div className="text-[11px] text-slate-500 uppercase">{label}</div>
      <div className="mt-1 text-sm font-semibold text-slate-100">{value}</div>
    </div>
  );
}
