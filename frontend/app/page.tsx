'use client';

import { useJarvisData } from '@/hooks/use-jarvis-data';
import { HudRing } from '@/components/cockpit/hud-ring';
import { IdentityPill } from '@/components/cockpit/identity-pill';
import { ConsolePanel } from '@/components/cockpit/console-panel';
import { OrbCore } from '@/components/cockpit/orb-core';
import { StatsStrip } from '@/components/cockpit/stats-strip';

export default function CockpitPage() {
  const { health, telemetry, logs, isThinking } = useJarvisData();

  return (
    <main className="relative min-h-screen w-full overflow-hidden bg-jarvis-bg text-white">
      {/* Scanlines overlay (já está no globals.css via body::before) */}

      {/* Background radial glow */}
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 60% 50% at 50% 30%, rgba(0,242,255,0.06) 0%, rgba(112,0,255,0.04) 40%, transparent 70%)',
        }}
      />

      {/* Conteúdo principal */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-6 gap-6">
        {/* Orb central */}
        <OrbCore thinking={isThinking} />

        {/* HUD Rings + Identity Pill */}
        <div className="flex items-center justify-center gap-10 flex-wrap">
          <HudRing value={health.cpu} label="CPU" color="#06b6d4" />
          <IdentityPill name={health.face_identity} emotion={health.face_emotion} />
          <HudRing value={health.ram} label="RAM" color="#a855f7" />
        </div>

        {/* Stats Strip */}
        <StatsStrip
          objects={telemetry?.perception.detected_objects ?? []}
          todos={telemetry?.obsidian.active_todos ?? 0}
        />

        {/* Console de Logs */}
        <div className="w-full max-w-2xl">
          <ConsolePanel logs={logs.logs} />
        </div>
      </div>
    </main>
  );
}
