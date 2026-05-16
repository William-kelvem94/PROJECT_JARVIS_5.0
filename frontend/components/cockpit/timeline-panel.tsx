'use client';

import { useMemo } from 'react';
import { Gauge } from 'lucide-react';
import { Panel } from '@/components/cockpit/panel';
import type { TelemetryHistoryItem } from '@/components/cockpit/types';

export function TimelinePanel({
  history,
  healthCpu,
  healthRam,
}: {
  history: TelemetryHistoryItem[];
  healthCpu: number;
  healthRam: number;
}) {
  const points = useMemo(() => {
    const source =
      history.length > 0
        ? history
        : [{ cpu: healthCpu, memory: healthRam, timestamp: new Date().toISOString() }];
    return source.slice(-18).map((item, index) => ({
      cpu: Math.max(0, Math.min(100, item.cpu ?? 0)),
      memory: Math.max(0, Math.min(100, item.memory ?? item.ram ?? 0)),
      label: item.timestamp
        ? new Date(item.timestamp).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
          })
        : String(index + 1),
    }));
  }, [history, healthCpu, healthRam]);

  const chartPath = (key: 'cpu' | 'memory') => {
    if (points.length === 1) return `M 0 ${100 - points[0][key]}`;
    return points
      .map((point, index) => {
        const x = (index / (points.length - 1)) * 100;
        const y = 100 - point[key];
        return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
      })
      .join(' ');
  };

  return (
    <Panel title="Telemetria temporal" icon={Gauge}>
      <div className="h-56 rounded-lg border border-white/10 bg-[#080b11] p-4">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="h-full w-full overflow-visible"
        >
          <path
            d="M 0 25 H 100 M 0 50 H 100 M 0 75 H 100"
            stroke="rgba(255,255,255,.08)"
            strokeWidth="0.5"
            vectorEffect="non-scaling-stroke"
          />
          <path
            d={chartPath('cpu')}
            fill="none"
            stroke="#67e8f9"
            strokeWidth="2.2"
            vectorEffect="non-scaling-stroke"
          />
          <path
            d={chartPath('memory')}
            fill="none"
            stroke="#86efac"
            strokeWidth="2.2"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-cyan-300" />
          CPU
        </span>
        <span className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-emerald-300" />
          RAM
        </span>
        <span>{points.length} amostras</span>
      </div>
    </Panel>
  );
}
