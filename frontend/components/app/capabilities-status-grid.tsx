'use client';

import { useEffect, useState } from 'react';
import { Brain, Eye, MonitorUp, Shield } from 'lucide-react';
import { jarvisApi } from '@/lib/jarvis-endpoints';

type ComponentStatus =
  | 'online'
  | 'offline'
  | 'degraded'
  | 'error'
  | 'initializing'
  | 'not_configured';

interface ComponentHealth {
  name: string;
  status: ComponentStatus;
  available: boolean;
  message: string;
  details?: Record<string, unknown>;
  error?: string | null;
}

interface CapabilityGroup {
  title: string;
  components: ComponentHealth[];
}

interface CapabilitiesData {
  capabilities: {
    nucleo_cognitivo: CapabilityGroup;
    percepcao: CapabilityGroup;
    sistema: CapabilityGroup;
    seguranca: CapabilityGroup;
    hardware: CapabilityGroup;
  };
  summary: {
    total_components?: number;
    online_count?: number;
    offline_count?: number;
    degraded_count?: number;
    error_count?: number;
    not_configured_count?: number;
    total?: number;
    online?: number;
    offline?: number;
    degraded?: number;
    error?: number;
    not_configured?: number;
    health_percentage: number;
  };
  timestamp: string;
}

const STATUS_COLORS: Record<ComponentStatus, string> = {
  online: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  offline: 'text-red-400 bg-red-500/10 border-red-500/20',
  degraded: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  error: 'text-red-400 bg-red-500/10 border-red-500/20',
  initializing: 'text-sky-400 bg-sky-500/10 border-sky-500/20',
  not_configured: 'text-gray-400 bg-gray-500/10 border-gray-500/20',
};

const STATUS_LABELS: Record<ComponentStatus, string> = {
  online: 'ONLINE',
  offline: 'OFFLINE',
  degraded: 'DEGRADED',
  error: 'ERROR',
  initializing: 'INIT',
  not_configured: 'N/C',
};

const GROUP_ICONS = {
  nucleo_cognitivo: Brain,
  percepcao: Eye,
  sistema: MonitorUp,
  seguranca: Shield,
  hardware: MonitorUp,
};

const GROUP_COLORS = {
  nucleo_cognitivo: 'text-sky-300',
  percepcao: 'text-emerald-300',
  sistema: 'text-amber-300',
  seguranca: 'text-purple-300',
  hardware: 'text-cyan-300',
};

export function CapabilitiesStatusGrid() {
  const [data, setData] = useState<CapabilitiesData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCapabilities = async () => {
      try {
        const response = await fetch(jarvisApi('/system/capabilities'));
        if (!response.ok) throw new Error('Failed to fetch capabilities');
        const json = await response.json();
        setData(json);
        setError(null);
      } catch (err) {
        console.error('Error fetching capabilities:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCapabilities();
    const interval = setInterval(fetchCapabilities, 5000); // Update every 5s

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-pulse text-white/60">Carregando status do sistema...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-6">
        <div className="font-semibold text-red-400">Erro ao carregar capabilities</div>
        <div className="mt-1 text-sm text-red-300/60">{error || 'Dados não disponíveis'}</div>
      </div>
    );
  }

  const groups = Object.entries(data.capabilities) as [
    keyof typeof data.capabilities,
    CapabilityGroup,
  ][];
  const total = data.summary.total_components ?? data.summary.total ?? 0;
  const online = data.summary.online_count ?? data.summary.online ?? 0;
  const offline = data.summary.offline_count ?? data.summary.offline ?? 0;
  const degraded = data.summary.degraded_count ?? data.summary.degraded ?? 0;

  return (
    <div className="space-y-6">
      {/* Health Summary */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Online" value={online} total={total} color="text-emerald-400" />
        <StatCard label="Offline" value={offline} total={total} color="text-red-400" />
        <StatCard label="Degraded" value={degraded} total={total} color="text-amber-400" />
        <StatCard
          label="Health"
          value={`${Math.round(data.summary.health_percentage)}%`}
          color={
            data.summary.health_percentage >= 80
              ? 'text-emerald-400'
              : data.summary.health_percentage >= 50
                ? 'text-amber-400'
                : 'text-red-400'
          }
        />
      </div>

      {/* Capability Groups */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {groups.map(([key, group]) => {
          const Icon = GROUP_ICONS[key];
          const colorClass = GROUP_COLORS[key];

          return (
            <div
              key={key}
              className="rounded-lg border border-white/10 bg-white/3 p-4 backdrop-blur-sm"
            >
              <div className="mb-3 flex items-center gap-2">
                <Icon className={`h-4 w-4 ${colorClass}`} />
                <h3 className={`font-semibold ${colorClass} text-sm tracking-wider uppercase`}>
                  {group.title}
                </h3>
              </div>

              <div className="space-y-2">
                {group.components.map((component, idx) => (
                  <ComponentStatusRow key={idx} component={component} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  total,
  color,
}: {
  label: string;
  value: number | string;
  total?: number;
  color: string;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/3 p-4 backdrop-blur-sm">
      <div className="mb-1 text-xs tracking-wider text-white/60 uppercase">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>
        {value}
        {total !== undefined && typeof value === 'number' && (
          <span className="ml-1 text-sm text-white/40">/ {total}</span>
        )}
      </div>
    </div>
  );
}

function ComponentStatusRow({ component }: { component: ComponentHealth }) {
  const statusClass = STATUS_COLORS[component.status];
  const statusLabel = STATUS_LABELS[component.status];

  return (
    <div className="flex items-center justify-between gap-2 rounded border border-white/5 bg-white/2 p-2 transition-colors hover:border-white/10">
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm font-medium text-white/90">{component.name}</div>
        <div className="truncate text-xs text-white/40">{component.message}</div>
      </div>

      <div
        className={`rounded border px-2 py-1 text-xs font-semibold ${statusClass} shrink-0`}
        title={component.error || component.message}
      >
        {statusLabel}
      </div>
    </div>
  );
}
