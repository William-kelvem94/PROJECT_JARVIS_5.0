'use client';

import { useJarvisData } from '@/hooks/use-jarvis-data';
import { useI18n } from '@/hooks/use-i18n';
import { HudRing } from '@/components/cockpit/hud-ring';
import { IdentityPill } from '@/components/cockpit/identity-pill';
import { ConsolePanel } from '@/components/cockpit/console-panel';
import { OrbCore } from '@/components/cockpit/orb-core';
import { StatsStrip } from '@/components/cockpit/stats-strip';
import { TelemetryChart } from '@/components/cockpit/telemetry-chart';
import { useTelemetryHistory } from '@/hooks/use-telemetry-history';

export default function Page() {
  const { health, telemetry, logs, isThinking } = useJarvisData();
  const { t } = useI18n();
  const { history } = useTelemetryHistory();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 bg-black p-6 text-white">
      <OrbCore thinking={isThinking} />

      <div className="flex flex-wrap items-center justify-center gap-12">
        <HudRing value={health.cpu} label={t('cockpit.cpu')} color="#06b6d4" />
        <HudRing value={health.ram} label={t('cockpit.ram')} color="#a855f7" />
        <IdentityPill name={health.face_identity} emotion={health.face_emotion} />
      </div>

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

      <div className="grid w-full max-w-5xl gap-6 lg:grid-cols-[1.5fr_1fr]">
        <div>
          <ConsolePanel logs={logs} emptyText={t('cockpit.noLogs')} />
        </div>
        <TelemetryChart history={history} />
      </div>

      <div className="fixed bottom-4 right-4 flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 backdrop-blur">
        <span className={`h-2 w-2 rounded-full ${health.is_ai_ready ? 'bg-green-400' : 'bg-red-400'}`} />
        <span className="text-xs text-white/60">
          {health.is_ai_ready ? t('cockpit.iaOnline') : t('cockpit.iaStarting')}
        </span>
      </div>
    </main>
  );
}
