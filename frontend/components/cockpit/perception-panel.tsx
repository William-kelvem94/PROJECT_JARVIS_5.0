'use client';

import { Brain, Camera, Eye } from 'lucide-react';
import { type TelemetryData } from '@/hooks/use-jarvis-data';
import { Panel } from '@/components/cockpit/panel';
import { StateTile } from '@/components/cockpit/state-tile';

export function PerceptionPanel({
  telemetry,
  activeObjects,
}: {
  telemetry: TelemetryData | null;
  activeObjects: string[];
}) {
  return (
    <Panel title="Percepção ao vivo" icon={Eye}>
      <div className="grid gap-3 sm:grid-cols-2">
        <StateTile
          icon={Camera}
          label="Identidade"
          value={telemetry?.perception.face_identity || 'sem rosto'}
          active={!!telemetry?.perception.face_identity}
        />
        <StateTile
          icon={Brain}
          label="Afeto"
          value={telemetry?.perception.face_emotion || 'neutro'}
          active={!!telemetry?.perception.face_emotion}
        />
      </div>
      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
          <span>Objetos detectados</span>
          <span>{activeObjects.length}</span>
        </div>
        <div className="flex min-h-20 flex-wrap content-start gap-2 rounded-lg border border-white/10 bg-black/20 p-3">
          {activeObjects.length > 0 ? (
            activeObjects.slice(0, 10).map((object) => (
              <span
                key={object}
                className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-2 py-1 text-xs text-emerald-100"
              >
                {object}
              </span>
            ))
          ) : (
            <span className="text-sm text-slate-500">Nenhum objeto no snapshot atual.</span>
          )}
        </div>
      </div>
    </Panel>
  );
}
