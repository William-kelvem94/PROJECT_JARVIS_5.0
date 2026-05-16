'use client';

import { Camera, Search } from 'lucide-react';
import { jarvisApi } from '@/lib/jarvis-endpoints';
import { Panel } from '@/components/cockpit/panel';

export function VisionPanel({ screenshot, objects }: { screenshot?: string; objects: string[] }) {
  return (
    <Panel title="Visão e capturas" icon={Camera}>
      <div className="aspect-video overflow-hidden rounded-lg border border-white/10 bg-black/30">
        {screenshot ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={jarvisApi(`/screenshots/${screenshot}`)}
            alt="Ultima captura do Jarvis"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="grid h-full place-items-center text-center text-sm text-slate-500">
            <div>
              <Search className="mx-auto mb-2 size-6 text-slate-600" />
              Aguardando capturas
            </div>
          </div>
        )}
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span>{screenshot || 'sem arquivo recente'}</span>
        <span>{objects.length} objetos</span>
      </div>
    </Panel>
  );
}
