'use client';

import type { ComponentType } from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';

export function Meter({
  label,
  value,
  icon: Icon,
  tone,
  suffix,
}: {
  label: string;
  value: number;
  icon: ComponentType<{ className?: string }>;
  tone: string;
  suffix?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value || 0));
  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="flex items-center gap-2 text-slate-400">
          <Icon className="size-3.5" />
          {label}
        </span>
        <span className="font-semibold text-slate-100 tabular-nums">
          {suffix ?? `${clamped.toFixed(0)}%`}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <motion.div
          className={cn('h-full rounded-full', tone)}
          animate={{ width: `${clamped}%` }}
          transition={{ duration: 0.6 }}
        />
      </div>
    </div>
  );
}
