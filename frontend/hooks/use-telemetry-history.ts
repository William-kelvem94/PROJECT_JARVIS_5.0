import { useEffect, useState } from 'react';
import { JarvisTelemetryHistory } from '@/types';

export function useTelemetryHistory(pollInterval = 8000) {
  const [history, setHistory] = useState<JarvisTelemetryHistory[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchHistory = async () => {
      try {
        const response = await fetch('/api/telemetry/history');
        if (!response.ok) {
          throw new Error('Failed to load telemetry history.');
        }
        const data = await response.json();
        if (mounted) {
          setHistory(data);
        }
      } catch (err) {
        if (mounted) {
          setError((err as Error).message);
        }
      }
    };

    fetchHistory();
    const interval = window.setInterval(fetchHistory, pollInterval);
    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, [pollInterval]);

  return { history, error };
}
