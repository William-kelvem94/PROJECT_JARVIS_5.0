'use client';

import { Radar } from 'lucide-react';
import { Panel } from '@/components/cockpit/panel';
import { roadmap } from '@/components/cockpit/types';

export function ModulePanel() {
  return (
    <Panel title="Mapa funcional" icon={Radar}>
      <div className="space-y-2">
        {roadmap.map((item) => (
          <div
            key={item.label}
            className="flex items-center justify-between rounded-lg border border-white/10 bg-black/20 px-3 py-2"
          >
            <span className="text-sm text-slate-300">{item.label}</span>
            <span className="rounded-full bg-white/8 px-2 py-0.5 text-[11px] text-slate-400 uppercase">
              {item.state}
            </span>
          </div>
        ))}
      </div>
    </Panel>
  );
}
