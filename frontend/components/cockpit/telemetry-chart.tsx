'use client';

import React, { useMemo } from 'react';
import { cn } from '@/lib/shadcn/utils';
import { JarvisTelemetryHistory } from '@/types';

interface TelemetryChartProps {
  data: JarvisTelemetryHistory[];
  width?: number;
  height?: number;
}

const EnergyWave = ({ value, colorClass }: { value: number; colorClass: string }) => {
  return (
    <div className="relative h-12 w-full overflow-hidden rounded-sm border border-cyan-500/30 bg-black/40">
      <svg className="absolute inset-0 h-full w-full">
        <path
          d={`M 0 24 Q ${Math.random() * 100} ${24 - value / 5}, 200 ${24}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className={cn('animate-pulse', colorClass)}
          style={{
            strokeDasharray: '5,5',
            filter: 'drop-shadow(0 0 8px rgba(34, 211, 238, 0.8))',
          }}
        />
      </svg>
      <div className="absolute inset-0 bg-gradient-to-t from-cyan-500/10 to-transparent" />
    </div>
  );
};

export function TelemetryChart({ data, width, height }: TelemetryChartProps) {
  const history = useMemo(() => data ?? [], [data]);

  const points = useMemo(
    () =>
      history.map((item) => ({
        timestamp: new Date(item.timestamp).toLocaleTimeString(),
        load: item.cpu || 0,
        memory: item.memory || 0,
      })),
    [history]
  );

  if (!history.length) {
    return (
      <div
        className="rounded-xl border border-cyan-500/30 bg-black/40 p-4 font-mono text-xs text-cyan-500/50"
        style={{ minHeight: height ?? 160 }}
      >
        NO_TELEMETRY_DATA // AWAITING_SIGNAL...
      </div>
    );
  }

  const lastPoint = points[points.length - 1];

  return (
    <div
      className="rounded-3xl border border-cyan-500/30 bg-black/60 p-4 font-mono shadow-[0_0_20px_rgba(6,182,212,0.1)] backdrop-blur-md"
      style={{ minHeight: height ?? 180, width: width ? `${width}px` : '100%' }}
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xs font-bold tracking-widest text-cyan-500 uppercase">
          System Telemetry
        </h2>
        <span className="text-[10px] text-cyan-500/50">{points.length} samples</span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* CPU Panel */}
        <div className="flex flex-col gap-2 border-l-2 border-cyan-500 bg-black/40 p-3">
          <div className="flex items-end justify-between">
            <span className="text-[10px] tracking-widest text-cyan-500/70 uppercase">CPU Load</span>
            <div className="text-right">
              <span className="text-xl font-bold text-cyan-400 tabular-nums">
                {lastPoint.load.toFixed(1)}
              </span>
              <span className="ml-1 text-[10px] text-cyan-600">%</span>
            </div>
          </div>
          <EnergyWave value={lastPoint.load} colorClass="text-cyan-400" />
        </div>

        {/* MEM Panel */}
        <div className="flex flex-col gap-2 border-l-2 border-purple-500 bg-black/40 p-3">
          <div className="flex items-end justify-between">
            <span className="text-[10px] tracking-widest text-purple-500/70 uppercase">Memory</span>
            <div className="text-right">
              <span className="text-xl font-bold text-purple-400 tabular-nums">
                {lastPoint.memory.toFixed(1)}
              </span>
              <span className="ml-1 text-[10px] text-purple-600">%</span>
            </div>
          </div>
          <EnergyWave value={lastPoint.memory} colorClass="text-purple-400" />
        </div>
      </div>

      <div className="mt-4 flex justify-between text-[8px] text-cyan-700">
        <span className="animate-pulse">STATUS: NOMINAL</span>
        <span>SYNC_CORE: ACTIVE</span>
      </div>
    </div>
  );
}
