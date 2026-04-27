'use client';
import { useEffect, useState } from 'react';
import { HudRing } from '@/components/cockpit/hud-ring';
import { IdentityPill } from '@/components/cockpit/identity-pill';
import { ConsolePanel } from '@/components/cockpit/console-panel';
import { OrbCore } from '@/components/cockpit/orb-core';
import { StatsStrip } from '@/components/cockpit/stats-strip';

interface HealthData {
  cpu: number;
  ram: number;
  face_identity: string;
  face_emotion: string;
}

export default function CockpitPage() {
  const [health, setHealth] = useState<HealthData>({
    cpu: 0, ram: 0, face_identity: 'Unknown', face_emotion: 'Neutro',
  });
  const [objects, setObjects] = useState<string[]>([]);
  const [todos, setTodos] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [thinking, setThinking] = useState(false);

  useEffect(() => {
    const tick = async () => {
      try {
        const h = await fetch('http://127.0.0.1:8000/health').then(r => r.json());
        setHealth({
          cpu: h.cpu ?? 0,
          ram: h.ram ?? 0,
          face_identity: h.face_identity || 'Unknown',
          face_emotion: h.face_emotion || 'Neutro',
        });
        setThinking((h.cpu ?? 0) > 50);
      } catch { /* backend offline */ }

      try {
        const t = await fetch('http://127.0.0.1:8001/api/status').then(r => r.json());
        setObjects(t?.perception?.detected_objects || []);
        setTodos(t?.obsidian?.active_todos || 0);
      } catch { /* telemetria offline */ }

      try {
        const today = new Date().toISOString().slice(0, 10);
        const l = await fetch(`http://127.0.0.1:8000/logs/${today}`).then(r => r.json());
        if (l?.logs) setLogs(l.logs);
      } catch { /* logs offline */ }
    };

    tick();
    const interval = setInterval(tick, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-6 gap-8">
      {/* Background radial glow */}
      <div
        className="fixed inset-0 z-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 50% at 50% 30%, rgba(0,242,255,0.06) 0%, rgba(112,0,255,0.04) 40%, transparent 70%)',
        }}
      />

      <div className="relative z-10 flex flex-col items-center gap-8 w-full">
        <OrbCore thinking={thinking} />

        <div className="flex items-center gap-12 flex-wrap justify-center">
          <HudRing value={health.cpu} label="CPU" color="#06b6d4" />
          <IdentityPill name={health.face_identity} emotion={health.face_emotion} />
          <HudRing value={health.ram} label="RAM" color="#a855f7" />
        </div>

        <StatsStrip objects={objects} todos={todos} />

        <div className="w-full max-w-2xl">
          <ConsolePanel logs={logs} />
        </div>
      </div>
    </main>
  );
}
