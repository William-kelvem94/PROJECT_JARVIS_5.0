'use client';

import type { ComponentType } from 'react';
import { cn } from '@/lib/shadcn/utils';

export function HeaderMetric({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <div className="flex h-10 items-center gap-2 rounded-lg border border-white/10 bg-white/4 px-3">
      <Icon className={cn('size-4', tone)} />
      <span className="text-[11px] text-slate-500 uppercase">{label}</span>
      <span className="text-sm font-semibold text-white tabular-nums">{value}</span>
    </div>
  );
}
