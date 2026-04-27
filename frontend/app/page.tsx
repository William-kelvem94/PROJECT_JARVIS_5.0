'use client';

import { useEffect, useState } from 'react';
import { HudRing } from '@/components/cockpit/hud-ring';
import { IdentityPill } from '@/components/cockpit/identity-pill';
import { ConsolePanel } from '@/components/cockpit/console-panel';
import { OrbCore } from '@/components/cockpit/orb-core';
import { StatsStrip } from '@/components/cockpit/stats-strip';

export default function CockpitPage() {
  const [health, setHealth] = useState({
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
      } catch {}

      try {
        const t = await fetch('http://127.0.0.1:8001/api/status').then((r) => r.json());
        setObjects(t?.perception?.detected_objects ?? []);
        setTodos(t?.obsidian?.active_todos ?? 0);
      } catch {}
    };

    tick();
    const i = setInterval(tick, 5000);
    return () => clearInterval(i);
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

  const [data, setData] = useState<JarvisData>(DEFAULT);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const [healthRes, statusRes, logsRes] = await Promise.allSettled([
          fetch('http://localhost:8000/health'),
          fetch('http://localhost:8001/api/status'),
          fetch(`http://localhost:8000/logs/${new Date().toISOString().split('T')[0]}`),
        ]);

        const health =
          healthRes.status === 'fulfilled' && healthRes.value.ok
            ? await healthRes.value.json()
            : {};
        const status =
          statusRes.status === 'fulfilled' && statusRes.value.ok
            ? await statusRes.value.json()
            : {};
        const logsJson =
          logsRes.status === 'fulfilled' && logsRes.value.ok
            ? await logsRes.value.json()
            : {};

        if (!cancelled) {
          setConnected(healthRes.status === 'fulfilled' && (healthRes.value as Response).ok);
          setData({
            cpu: status.cpu ?? health.cpu ?? 0,
            ram: status.ram ?? health.ram ?? 0,
            emotion: status.emotion ?? health.emotion ?? 'neutro',
            face_label: status.face_label ?? health.face_label ?? 'Desconhecido',
            objects: status.objects ?? [],
            todos: status.todos ?? [],
            screenshot: status.screenshot,
            logs: Array.isArray(logsJson.logs) ? logsJson.logs : [],
            engine: health.engine ?? status.engine ?? '--',
            uptime: health.uptime ?? 0,
          });
        }
      } catch {
        if (!cancelled) setConnected(false);
      }
    }

    poll();
    const id = setInterval(poll, 5000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <main className="min-h-screen bg-jarvis-bg text-white flex flex-col items-center justify-start p-6 gap-6">
      {/* Header */}
      <div className="flex items-center gap-4 w-full max-w-6xl">
        <span className="text-2xl font-bold tracking-widest text-jarvis-cyan">J.A.R.V.I.S</span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full border ${
            connected ? 'border-green-400 text-green-400' : 'border-red-500 text-red-500'
          }`}
        >
          {connected ? 'ONLINE' : 'OFFLINE'}
        </span>
        <span className="text-xs text-white/40 ml-auto">{data.engine}</span>
      </div>

      {/* Orb + HUD rings */}
      <div className="flex items-center gap-8 w-full max-w-6xl">
        <HudRing label="CPU" value={data.cpu} color="#00f2ff" size={130} />
        <div className="flex-1 flex justify-center">
          <OrbCore />
        </div>
        <HudRing label="RAM" value={data.ram} color="#7000ff" size={130} />
      </div>

      {/* Identity pill */}
      <IdentityPill emotion={data.emotion} faceLabel={data.face_label} />

      {/* Stats strip */}
      <StatsStrip objects={data.objects} todos={data.todos} screenshot={data.screenshot} />

      {/* Console */}
      <div className="w-full max-w-6xl">
        <ConsolePanel logs={data.logs} />
      </div>
    </main>
  );
}
