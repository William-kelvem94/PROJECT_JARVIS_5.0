'use client';

import { useState } from 'react';
import { useJarvisData } from '@/hooks/use-jarvis-data';
import { useI18n } from '@/hooks/use-i18n';
import { useTelemetryHistory } from '@/hooks/use-telemetry-history';
import { HudRing } from '@/components/cockpit/hud-ring';
import { IdentityPill } from '@/components/cockpit/identity-pill';
import { ConsolePanel } from '@/components/cockpit/console-panel';
import { OrbCore } from '@/components/cockpit/orb-core';
import { StatsStrip } from '@/components/cockpit/stats-strip';
import { TelemetryChart } from '@/components/cockpit/telemetry-chart';

export default function Page() {
  const { health, telemetry, logs, isThinking } = useJarvisData();
  const { t } = useI18n();
  const { history } = useTelemetryHistory(60);
  const [showConsole, setShowConsole] = useState(false);

  return (
    <main className="min-h-screen bg-black text-white p-4 md:p-6 flex flex-col gap-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`h-3 w-3 rounded-full ${health.is_ai_ready ? 'bg-green-400' : 'bg-red-400'}`} />
          <span className="text-sm text-white/60">
            {health.is_ai_ready ? t('cockpit.iaOnline') : t('cockpit.iaStarting')}
          </span>
        </div>
        <div className="text-sm text-white/40">
          {new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </header>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <aside className="flex flex-col gap-4 lg:w-1/3">
          <section className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
            <h2 className="text-xs font-semibold uppercase tracking-[0.25em] text-white/50 mb-4">Hardware</h2>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-between">
              <HudRing value={health.cpu} label={t('cockpit.cpu')} color="#06b6d4" />
              <HudRing value={health.ram} label={t('cockpit.ram')} color="#a855f7" />
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
            <h2 className="text-xs font-semibold uppercase tracking-[0.25em] text-white/50 mb-4">Presença</h2>
            <div className="flex justify-center">
              <IdentityPill name={health.face_identity} emotion={health.face_emotion} />
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
            <h2 className="text-xs font-semibold uppercase tracking-[0.25em] text-white/50 mb-4">Ambiente</h2>
            <StatsStrip
              objects={telemetry?.perception?.detected_objects || []}
              todos={telemetry?.obsidian?.active_todos || 0}
              noObjectsText={t('cockpit.noObjects')}
              tasksText={(count: number) =>
                t('cockpit.tasks', {
                  count,
                  plural: count !== 1 ? 's' : '',
                })
              }
            />
          </section>
        </aside>

        <section className="flex-1 rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
          <div className="flex flex-col items-center gap-8">
            <OrbCore thinking={isThinking} />
            <div className="w-full max-w-3xl">
              <TelemetryChart data={history} width={640} height={180} />
            </div>
          </div>
        </section>
      </div>

      <div className="relative">
        <button
          type="button"
          onClick={() => setShowConsole((state) => !state)}
          className="mb-4 rounded-full bg-white/10 px-4 py-2 text-sm text-white transition hover:bg-white/20"
        >
          {showConsole ? 'Ocultar terminal' : 'Exibir terminal'}
        </button>

        <div className={`overflow-hidden rounded-3xl border border-white/10 bg-white/5 transition-all duration-300 ${showConsole ? 'max-h-[420px] p-4' : 'max-h-0 p-0'}`}>
          <ConsolePanel logs={logs} emptyText={t('cockpit.noLogs')} />
        </div>
      </div>
    </main>
  );
}
