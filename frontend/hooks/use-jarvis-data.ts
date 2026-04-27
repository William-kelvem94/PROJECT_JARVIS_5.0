'use client';

import { useEffect, useState } from 'react';

interface HealthData {
  cpu: number;
  ram: number;
  face_identity: string;
  face_emotion: string;
  gesture: string;
  is_ai_ready: boolean;
}

interface TelemetryData {
  hardware: { cpu: number; ram: number; threads: number };
  perception: {
    face_identity: string | null;
    face_emotion: string | null;
    detected_objects: string[];
  };
  persona: Record<string, number>;
  obsidian: { active_todos: number; vault_path: string };
}

export function useJarvisData() {
  const [health, setHealth] = useState<HealthData>({
    cpu: 0,
    ram: 0,
    face_identity: 'Unknown',
    face_emotion: 'Neutro',
    gesture: 'None',
    is_ai_ready: false,
  });
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/health');
        const data = await res.json();
        setHealth({
          cpu: data.cpu ?? 0,
          ram: data.ram ?? 0,
          face_identity: data.face_identity || 'Unknown',
          face_emotion: data.face_emotion || 'Neutro',
          gesture: data.gesture || 'None',
          is_ai_ready: data.is_ai_ready ?? false,
        });
        setIsThinking((data.cpu ?? 0) > 50);
      } catch {}
    };

    const fetchTelemetry = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8001/api/status');
        const data = await res.json();
        setTelemetry(data);
      } catch {}
    };

    const fetchLogs = async () => {
      try {
        const today = new Date().toISOString().slice(0, 10);
        const res = await fetch(`http://127.0.0.1:8000/logs/${today}`);
        const data = await res.json();
        if (data.logs) setLogs(data.logs);
      } catch {}
    };

    fetchHealth();
    fetchTelemetry();
    fetchLogs();

    const interval = setInterval(() => {
      fetchHealth();
      fetchTelemetry();
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return { health, telemetry, logs, isThinking };
}
