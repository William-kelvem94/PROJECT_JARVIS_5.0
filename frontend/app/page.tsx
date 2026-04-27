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

export default function Page() {
  const [health, setHealth] = useState<HealthData>({
    cpu: 0,
    ram: 0,
    face_identity: 'Unknown',
    face_emotion: 'Neutro',
  });
  const [objects, setObjects] = useState<string[]>([]);
  const [todos, setTodos] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [thinking, setThinking] = useState(false);

  useEffect(() => {
    const tick = async () => {
      try {
        const h = await fetch('http://127.0.0.1:8000/health').then((r) => r.json());
        setHealth({
          cpu: h.cpu ?? 0,
          ram: h.ram ?? 0,
          face_identity: h.face_identity || 'Unknown',
          face_emotion: h.face_emotion || 'Neutro',
        });
        setThinking((h.cpu ?? 0) > 50);
      } catch {
        setHealth((current) => ({ ...current }));
      }

      try {
        const t = await fetch('http://127.0.0.1:8001/api/status').then((r) => r.json());
        setObjects(t?.perception?.detected_objects || []);
        setTodos(t?.obsidian?.active_todos || 0);
      } catch {
        setObjects([]);
        setTodos(0);
      }

      try {
        const today = new Date().toISOString().slice(0, 10);
        const l = await fetch(`http://127.0.0.1:8000/logs/${today}`).then((r) => r.json());
        if (l?.logs) setLogs(l.logs);
      } catch {
        setLogs([]);
      }
    };

    tick();
    const intervalId = setInterval(tick, 5000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-6 gap-8">
      <OrbCore thinking={thinking} />

      <div className="flex items-center gap-12 flex-wrap justify-center">
        <HudRing value={health.cpu} label="CPU" color="#06b6d4" />
        <HudRing value={health.ram} label="RAM" color="#a855f7" />
        <IdentityPill name={health.face_identity} emotion={health.face_emotion} />
      </div>

      <StatsStrip objects={objects} todos={todos} />

      <div className="w-full max-w-2xl">
        <ConsolePanel logs={logs} />
      </div>
    </main>
  );
}
