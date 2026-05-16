'use client';

import { useEffect, useState } from 'react';
import { jarvisApi } from '@/lib/jarvis-endpoints';
import type { MemoryItem, ProjectData, TelemetryHistoryItem, VaultStats } from '@/components/cockpit/types';

export function useProjectData(): ProjectData & { refresh: () => Promise<void> } {
  const [state, setState] = useState<ProjectData>({
    memories: [],
    screenshots: [],
    vaultStats: null,
    history: [],
    isLoading: true,
    lastUpdated: null,
  });

  const refresh = async () => {
    setState((prev) => ({ ...prev, isLoading: true }));
    const safeJson = async <T,>(path: string, fallback: T): Promise<T> => {
      try {
        const res = await fetch(jarvisApi(path));
        if (!res.ok) return fallback;
        return (await res.json()) as T;
      } catch {
        return fallback;
      }
    };

    const [memoryRes, screenshotRes, vaultRes, historyRes] = await Promise.all([
      safeJson<{ memories?: MemoryItem[] }>('/memory', { memories: [] }),
      safeJson<{ screenshots?: string[] }>('/screenshots', { screenshots: [] }),
      safeJson<VaultStats | null>('/vault-stats', null),
      safeJson<{ history?: TelemetryHistoryItem[] }>('/telemetry/history?limit=24', {
        history: [],
      }),
    ]);

    setState({
      memories: memoryRes.memories ?? [],
      screenshots: screenshotRes.screenshots ?? [],
      vaultStats: vaultRes,
      history: historyRes.history ?? [],
      isLoading: false,
      lastUpdated: new Date(),
    });
  };

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 15000);
    return () => window.clearInterval(timer);
  }, []);

  return { ...state, refresh };
}

export function normalizeDetectedObjects(objects?: unknown[]): string[] {
  if (!Array.isArray(objects)) return [];

  return objects
    .map((item) => {
      if (typeof item === 'string') return item;
      if (item && typeof item === 'object') {
        const record = item as Record<string, unknown>;
        const label = record.label ?? record.name ?? record.class ?? record.type;
        return typeof label === 'string' ? label : '';
      }
      return '';
    })
    .filter(Boolean)
    .slice(0, 24);
}
