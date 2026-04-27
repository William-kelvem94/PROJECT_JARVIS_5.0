'use client';

import { useMemo } from 'react';
import { JarvisTelemetryHistory } from '@/types';

interface TelemetryChartProps {
  history: JarvisTelemetryHistory[];
}

export function TelemetryChart({ history }: TelemetryChartProps) {
  const points = useMemo(
    () => history.map((item) => ({
      timestamp: new Date(item.timestamp).toLocaleTimeString(),
      load: item.cpu || 0,
      memory: item.memory || 0,
    })),
    [history],
  );

  if (!history.length) {
    return <div className="rounded-xl border border-slate-200/80 p-4 text-slate-500">No telemetry history available.</div>;
  }

  return (
    <div className="rounded-3xl border border-slate-200/80 bg-white/90 p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-900">Telemetry history</h2>
        <span className="text-xs text-slate-500">{points.length} samples</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {points.slice(-6).map((point) => (
          <div key={point.timestamp} className="rounded-2xl bg-slate-50 p-3">
            <div className="text-xs text-slate-500">{point.timestamp}</div>
            <div className="mt-2 flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-slate-900">CPU</span>
              <span className="text-slate-700">{point.load.toFixed(1)}%</span>
            </div>
            <div className="mt-1 flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-slate-900">Memory</span>
              <span className="text-slate-700">{point.memory.toFixed(1)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
