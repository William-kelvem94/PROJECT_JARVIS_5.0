'use client';

import { cn } from '@/lib/shadcn/utils';

export function StatusBadge({ state, label }: { state: string; label: string }) {
  const color =
    state === 'atencao'
      ? 'border-rose-300/30 bg-rose-300/10 text-rose-100'
      : state === 'offline'
        ? 'border-slate-400/20 bg-slate-400/10 text-slate-300'
        : 'border-emerald-300/30 bg-emerald-300/10 text-emerald-100';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium',
        color
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {label}
    </span>
  );
}
