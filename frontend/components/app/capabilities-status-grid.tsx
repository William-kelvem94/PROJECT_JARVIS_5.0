"use client";

import { useEffect, useState } from 'react';
import { Brain, Eye, MonitorUp, Shield } from 'lucide-react';

type ComponentStatus = 'online' | 'offline' | 'degraded' | 'error' | 'initializing' | 'not_configured';

interface ComponentHealth {
  name: string;
  status: ComponentStatus;
  available: boolean;
  message: string;
  details?: Record<string, any>;
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
    total: number;
    online: number;
    offline: number;
    degraded: number;
    error: number;
    not_configured: number;
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
        const response = await fetch('/jarvis-api/system/capabilities');
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
        <div className="text-white/60 animate-pulse">Carregando status do sistema...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-lg">
        <div className="text-red-400 font-semibold">Erro ao carregar capabilities</div>
        <div className="text-red-300/60 text-sm mt-1">{error || 'Dados não disponíveis'}</div>
      </div>
    );
  }

  const groups = Object.entries(data.capabilities) as [keyof typeof data.capabilities, CapabilityGroup][];

  return (
    <div className="space-y-6">
      {/* Health Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Online"
          value={data.summary.online}
          total={data.summary.total}
          color="text-emerald-400"
        />
        <StatCard
          label="Offline"
          value={data.summary.offline}
          total={data.summary.total}
          color="text-red-400"
        />
        <StatCard
          label="Degraded"
          value={data.summary.degraded}
          total={data.summary.total}
          color="text-amber-400"
        />
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
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {groups.map(([key, group]) => {
          const Icon = GROUP_ICONS[key];
          const colorClass = GROUP_COLORS[key];

          return (
            <div
              key={key}
              className="bg-white/3 border border-white/10 rounded-lg p-4 backdrop-blur-sm"
            >
              <div className="flex items-center gap-2 mb-3">
                <Icon className={`w-4 h-4 ${colorClass}`} />
                <h3 className={`font-semibold ${colorClass} text-sm uppercase tracking-wider`}>
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
    <div className="bg-white/3 border border-white/10 rounded-lg p-4 backdrop-blur-sm">
      <div className="text-white/60 text-xs uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>
        {value}
        {total !== undefined && typeof value === 'number' && (
          <span className="text-sm text-white/40 ml-1">/ {total}</span>
        )}
      </div>
    </div>
  );
}

function ComponentStatusRow({ component }: { component: ComponentHealth }) {
  const statusClass = STATUS_COLORS[component.status];
  const statusLabel = STATUS_LABELS[component.status];

  return (
    <div className="flex items-center justify-between gap-2 p-2 bg-white/2 rounded border border-white/5 hover:border-white/10 transition-colors">
      <div className="flex-1 min-w-0">
        <div className="text-white/90 text-sm font-medium truncate">{component.name}</div>
        <div className="text-white/40 text-xs truncate">{component.message}</div>
      </div>

      <div
        className={`px-2 py-1 rounded text-xs font-semibold border ${statusClass} shrink-0`}
        title={component.error || component.message}
      >
        {statusLabel}
      </div>
    </div>
  );
}
