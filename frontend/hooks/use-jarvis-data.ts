'use client';

import { useEffect, useState } from 'react';
import { jarvisApi, telemetryApi } from '@/lib/jarvis-endpoints';

export interface HealthData {
  cpu: number;
  ram: number;
  face_identity: string;
  face_emotion: string;
  gesture: string;
  is_ai_ready: boolean;
}

export interface TelemetryData {
  hardware: { cpu: number; ram: number; threads: number };
  perception: {
    face_identity: string | null;
    face_emotion: string | null;
    detected_objects: string[];
  };
  persona: Record<string, number>;
  obsidian: { active_todos: number; vault_path: string };
}

export interface LogsData {
  logs: string[];
}

export interface JarvisData {
  health: HealthData;
  telemetry: TelemetryData | null;
  logs: LogsData;
  isThinking: boolean;
}

const DEFAULT_HEALTH: HealthData = {
  cpu: 0,
  ram: 0,
  face_identity: 'Unknown',
  face_emotion: 'Neutro',
  gesture: 'None',
  is_ai_ready: false,
};

export function useJarvisData(): JarvisData {
  const [health, setHealth] = useState<HealthData>(DEFAULT_HEALTH);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [logs, setLogs] = useState<LogsData>({ logs: [] });
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(jarvisApi('/health'));
        if (!res.ok) return;
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
      } catch {
        // backend offline — mantém últimos valores
      }
    };

    const fetchTelemetry = async () => {
      try {
        const res = await fetch(telemetryApi('/api/status'));
        if (!res.ok) return;
        const data = await res.json();
        setTelemetry(data);
      } catch {
        // servidor de telemetria offline
      }
    };

    const fetchLogs = async () => {
      const today = new Date().toISOString().slice(0, 10);
      try {
        const res = await fetch(jarvisApi(`/logs/${today}`));
        if (!res.ok) return;
        const data = await res.json();
        if (Array.isArray(data.logs)) {
          setLogs({ logs: data.logs });
        }
      } catch {
        // sem logs disponíveis
      }
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
