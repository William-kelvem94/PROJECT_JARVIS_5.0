<<<<<<< HEAD
import { useEffect, useState } from 'react';

const JARVIS_API_URL = process.env.NEXT_PUBLIC_JARVIS_API_URL || 'http://localhost:8000';
const TELEMETRY_URL = 'http://localhost:8001';

export interface HealthData {
=======
'use client';

import { useEffect, useState } from 'react';

interface HealthData {
>>>>>>> main
  cpu: number;
  ram: number;
  face_identity: string;
  face_emotion: string;
  gesture: string;
<<<<<<< HEAD
}

export interface TelemetryData {
=======
  is_ai_ready: boolean;
}

interface TelemetryData {
>>>>>>> main
  hardware: { cpu: number; ram: number; threads: number };
  perception: {
    face_identity: string | null;
    face_emotion: string | null;
    detected_objects: string[];
  };
  persona: Record<string, number>;
  obsidian: { active_todos: number; vault_path: string };
}

<<<<<<< HEAD
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
};

export function useJarvisData(): JarvisData {
  const [health, setHealth] = useState<HealthData>(DEFAULT_HEALTH);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [logs, setLogs] = useState<LogsData>({ logs: [] });
=======
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
>>>>>>> main
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
<<<<<<< HEAD
        const res = await fetch(`${JARVIS_API_URL}/health`);
        if (!res.ok) return;
=======
        const res = await fetch('http://127.0.0.1:8000/health');
>>>>>>> main
        const data = await res.json();
        setHealth({
          cpu: data.cpu ?? 0,
          ram: data.ram ?? 0,
          face_identity: data.face_identity || 'Unknown',
          face_emotion: data.face_emotion || 'Neutro',
          gesture: data.gesture || 'None',
<<<<<<< HEAD
        });
        setIsThinking((data.cpu ?? 0) > 50);
      } catch {
        // backend offline — mantém últimos valores
      }
=======
          is_ai_ready: data.is_ai_ready ?? false,
        });
        setIsThinking((data.cpu ?? 0) > 50);
      } catch {}
>>>>>>> main
    };

    const fetchTelemetry = async () => {
      try {
<<<<<<< HEAD
        const res = await fetch(`${TELEMETRY_URL}/api/status`);
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
        const res = await fetch(`${JARVIS_API_URL}/logs/${today}`);
        if (!res.ok) return;
        const data = await res.json();
        if (Array.isArray(data.logs)) {
          setLogs({ logs: data.logs });
        }
      } catch {
        // sem logs disponíveis
      }
=======
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
>>>>>>> main
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
