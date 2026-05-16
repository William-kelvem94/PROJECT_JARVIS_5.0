'use client';

import { Activity, Cpu, HardDrive, Network, Radio, Zap } from 'lucide-react';
import { type TelemetryData, useJarvisData } from '@/hooks/use-jarvis-data';
import { Panel } from '@/components/cockpit/panel';
import { Meter } from '@/components/cockpit/meter';
import { StateTile } from '@/components/cockpit/state-tile';

export function SystemPanel({
  health,
  telemetry,
  isThinking,
  isConnected,
}: {
  health: ReturnType<typeof useJarvisData>['health'];
  telemetry: TelemetryData | null;
  isThinking: boolean;
  isConnected: boolean;
}) {
  return (
    <Panel title="Estado do sistema" icon={Activity}>
      <div className="grid gap-3">
        <Meter label="Processador" value={health.cpu} icon={Cpu} tone="bg-cyan-300" />
        <Meter label="Memória" value={health.ram} icon={HardDrive} tone="bg-emerald-300" />
        <Meter
          label="Threads ativas"
          value={Math.min((telemetry?.hardware.threads ?? 0) * 4, 100)}
          icon={Network}
          tone="bg-amber-300"
          suffix={String(telemetry?.hardware.threads ?? '-')}
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
        <StateTile
          icon={Radio}
          label="Voz"
          value={isConnected ? 'conectada' : 'manual'}
          active={isConnected}
        />
        <StateTile
          icon={Zap}
          label="Raciocinio"
          value={isThinking ? 'ativo' : 'ocioso'}
          active={isThinking}
        />
      </div>
    </Panel>
  );
}
