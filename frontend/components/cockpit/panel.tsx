'use client';

import type { ComponentType, ReactNode } from 'react';
import { cn } from '@/lib/shadcn/utils';

export function Panel({
  title,
  icon: Icon,
  children,
  action,
  className,
}: {
  title: string;
  icon: ComponentType<{ className?: string }>;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        'rounded-xl border border-white/10 bg-white/4.5 p-4 shadow-xl shadow-black/20 backdrop-blur-md',
        className
      )}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <Icon className="size-4 shrink-0 text-cyan-200" />
          <h2 className="truncate text-sm font-semibold text-slate-100">{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
