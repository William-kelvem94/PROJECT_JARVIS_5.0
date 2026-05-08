'use client';

import { useEffect, useMemo, useState } from 'react';
import type { ComponentType, ReactNode } from 'react';
import dynamic from 'next/dynamic';
import {
  Activity,
  Brain,
  Camera,
  Cpu,
  Database,
  Eye,
  FileText,
  Gauge,
  HardDrive,
  LayoutDashboard,
  ListTodo,
  MessageSquareText,
  Mic,
  Network,
  Power,
  Radar,
  Radio,
  RefreshCcw,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Terminal,
  Zap,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { JarvisProvider, useJarvis } from '@/context/JarvisContext';
import { type TelemetryData, useJarvisData } from '@/hooks/use-jarvis-data';
import { jarvisApi } from '@/lib/jarvis-endpoints';
import { cn } from '@/lib/shadcn/utils';

// Dynamic import with fallback
const CapabilitiesStatusGrid = dynamic(
  () =>
    import('@/components/app/capabilities-status-grid').then((mod) => ({
      default: mod.CapabilitiesStatusGrid,
    })),
  {
    loading: () => (
      <div className="animate-pulse p-4 text-white/60">Carregando capabilities...</div>
    ),
    ssr: false,
  }
);

type MemoryItem = {
  id?: string;
  memory?: string;
  text?: string;
  content?: string;
  title?: string;
  metadata?: Record<string, unknown>;
};

type TelemetryHistoryItem = {
  cpu?: number;
  memory?: number;
  ram?: number;
  status?: string;
  timestamp?: string;
};

type VaultStats = {
  total_notes?: number;
  total_memories?: number;
  episodic?: number;
  semantic?: number;
  vault_path?: string;
  available?: boolean;
  [key: string]: unknown;
};

type SaveStatus = {
  type: 'idle' | 'success' | 'error';
  message: string;
};

type ProjectData = {
  memories: MemoryItem[];
  screenshots: string[];
  vaultStats: VaultStats | null;
  history: TelemetryHistoryItem[];
  isLoading: boolean;
  lastUpdated: Date | null;
};

const roadmap = [
  { label: 'Backend FastAPI', state: 'online' },
  { label: 'WebSocket de voz', state: 'manual' },
  { label: 'Telemetria 8001', state: 'sincroniza' },
  { label: 'Vault Obsidian', state: 'indexado' },
  { label: 'Memória episódica', state: 'gravável' },
];

export default function Home() {
  return (
    <JarvisProvider>
      <JarvisCockpit />
    </JarvisProvider>
  );
}

function JarvisCockpit() {
  const { health, telemetry, logs, isThinking } = useJarvisData();
  const { isConnected, agentState, messages, error, connect, disconnect, sendMessage } =
    useJarvis();
  const projectData = useProjectData();
  const [draft, setDraft] = useState('');
  const [chatOpen, setChatOpen] = useState(false);
  const [memoryDraft, setMemoryDraft] = useState({
    title: '',
    content: '',
    project: 'PROJECT_JARVIS_5.0',
    keywords: '',
    importance: 'MEDIA',
  });
  const [noteDraft, setNoteDraft] = useState({ title: '', body: '' });
  const [saveStatus, setSaveStatus] = useState<SaveStatus>({ type: 'idle', message: '' });
  const [isSavingKnowledge, setIsSavingKnowledge] = useState(false);

  const activeObjects = normalizeDetectedObjects(telemetry?.perception.detected_objects);
  const personaTraits = Object.entries(telemetry?.persona ?? {}).slice(0, 5);
  const latestScreenshot = projectData.screenshots[0];
  const lastLogs = logs.logs.slice(-7);
  const systemState = error
    ? 'atencao'
    : isConnected
      ? agentState
      : health.is_ai_ready
        ? 'pronto'
        : 'offline';

  const statusCopy = {
    idle: 'Aguardando comando',
    listening: 'Escutando',
    thinking: 'Raciocinando',
    speaking: 'Respondendo',
    pronto: 'Backend pronto',
    offline: 'Backend indisponivel',
    atencao: 'Precisa de atencao',
  }[systemState];

  const handleSend = async () => {
    const message = draft.trim();
    if (!message) return;
    setDraft('');
    setChatOpen(true);
    await sendMessage(message);
  };

  const saveVaultMemory = async () => {
    if (!memoryDraft.title.trim() || !memoryDraft.content.trim()) {
      setSaveStatus({ type: 'error', message: 'Informe título e conteúdo da memória.' });
      return;
    }

    try {
      setIsSavingKnowledge(true);
      const res = await fetch(jarvisApi('/vault-memory'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: memoryDraft.title.trim(),
          content: memoryDraft.content.trim(),
          project: memoryDraft.project.trim(),
          importance: memoryDraft.importance,
          keywords: memoryDraft.keywords
            .split(',')
            .map((keyword) => keyword.trim())
            .filter(Boolean),
        }),
      });

      if (!res.ok) throw new Error(`Falha HTTP ${res.status}`);
      const data = await res.json();
      setMemoryDraft((prev) => ({ ...prev, title: '', content: '', keywords: '' }));
      setSaveStatus({
        type: 'success',
        message: data.path ? `Memória salva em ${data.path}` : 'Memória salva no vault.',
      });
      await projectData.refresh();
    } catch {
      setSaveStatus({ type: 'error', message: 'Nao foi possivel salvar a memoria.' });
    } finally {
      setIsSavingKnowledge(false);
    }
  };

  const saveQuickNote = async () => {
    if (!noteDraft.title.trim() || !noteDraft.body.trim()) {
      setSaveStatus({ type: 'error', message: 'Informe título e corpo da nota.' });
      return;
    }

    try {
      setIsSavingKnowledge(true);
      const res = await fetch(jarvisApi('/notes'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: noteDraft.title.trim(), body: noteDraft.body.trim() }),
      });

      if (!res.ok) throw new Error(`Falha HTTP ${res.status}`);
      const data = await res.json();
      setNoteDraft({ title: '', body: '' });
      setSaveStatus({
        type: 'success',
        message: data.path ? `Nota criada em ${data.path}` : 'Nota criada no vault.',
      });
      await projectData.refresh();
    } catch {
      setSaveStatus({ type: 'error', message: 'Nao foi possivel criar a nota.' });
    } finally {
      setIsSavingKnowledge(false);
    }
  };

  return (
    <main className="bg-jarvis-bg min-h-screen overflow-x-hidden text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.12),transparent_34%),radial-gradient(circle_at_80%_20%,rgba(16,185,129,0.08),transparent_28%),linear-gradient(180deg,#080a0f_0%,#0f1117_52%,#080a0f_100%)]" />
      <div className="pointer-events-none fixed inset-0 bg-[linear-gradient(rgba(255,255,255,.8)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.8)_1px,transparent_1px)] bg-size-[48px_48px] opacity-[0.07]" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-420 flex-col px-4 py-4 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-4 border-b border-white/10 pb-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-4">
            <div className="grid size-12 place-items-center rounded-lg border border-cyan-300/30 bg-cyan-300/10">
              <LayoutDashboard className="size-6 text-cyan-200" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl font-semibold tracking-normal text-white">JARVIS 5.0</h1>
                <StatusBadge state={systemState} label={statusCopy} />
              </div>
              <p className="mt-1 max-w-2xl text-sm text-slate-400">
                Cockpit operacional para voz, memoria, percepcao, automacao local e engenharia do
                sistema.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <HeaderMetric
              icon={Cpu}
              label="CPU"
              value={`${health.cpu.toFixed(0)}%`}
              tone="text-cyan-200"
            />
            <HeaderMetric
              icon={HardDrive}
              label="RAM"
              value={`${health.ram.toFixed(0)}%`}
              tone="text-emerald-200"
            />
            <HeaderMetric
              icon={Database}
              label="Vault"
              value={
                telemetry?.obsidian.active_todos !== undefined
                  ? `${telemetry.obsidian.active_todos} tarefas`
                  : 'standby'
              }
              tone="text-amber-200"
            />
            <button
              onClick={() => projectData.refresh()}
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-white/10 bg-white/4 px-3 text-xs font-medium text-slate-200 transition hover:border-cyan-200/30 hover:bg-cyan-200/10"
              title="Atualizar dados"
            >
              <RefreshCcw className={cn('size-4', projectData.isLoading && 'animate-spin')} />
              Atualizar
            </button>
          </div>
        </header>

        <section className="grid flex-1 gap-4 py-4 xl:grid-cols-[320px_minmax(0,1fr)_360px]">
          <aside className="grid content-start gap-4">
            <SystemPanel
              health={health}
              telemetry={telemetry}
              isThinking={isThinking}
              isConnected={isConnected}
            />
            <ModulePanel />
          </aside>

          <section className="grid min-w-0 content-start gap-4">
            <CommandCenter
              status={statusCopy}
              connected={isConnected}
              error={error}
              draft={draft}
              setDraft={setDraft}
              onSend={handleSend}
              onConnect={connect}
              onDisconnect={disconnect}
              messages={messages}
            />

            <div className="grid gap-4 lg:grid-cols-[1.1fr_.9fr]">
              <TimelinePanel
                history={projectData.history}
                healthCpu={health.cpu}
                healthRam={health.ram}
              />
              <PerceptionPanel telemetry={telemetry} activeObjects={activeObjects} />
            </div>

            <CapabilitiesStatusGrid />
          </section>

          <aside className="grid content-start gap-4">
            <BrainPanel
              memories={projectData.memories}
              vaultStats={projectData.vaultStats}
              personaTraits={personaTraits}
            />
            <KnowledgeCapturePanel
              memoryDraft={memoryDraft}
              noteDraft={noteDraft}
              saveStatus={saveStatus}
              isSaving={isSavingKnowledge}
              onMemoryDraftChange={setMemoryDraft}
              onNoteDraftChange={setNoteDraft}
              onSaveMemory={saveVaultMemory}
              onSaveNote={saveQuickNote}
            />
            <VisionPanel screenshot={latestScreenshot} objects={activeObjects} />
            <ConsolePanel logs={lastLogs} />
          </aside>
        </section>

        <footer className="sticky bottom-4 z-30 mx-auto w-full max-w-3xl">
          <div className="rounded-xl border border-white/10 bg-[#0b0f16]/90 p-2 shadow-2xl shadow-black/50 backdrop-blur-xl">
            <AgentControlBar
              controls={{
                leave: true,
                microphone: true,
                camera: true,
                screenShare: true,
                chat: true,
              }}
              isChatOpen={chatOpen}
              onIsChatOpenChange={setChatOpen}
              onLeave={disconnect}
            />
          </div>
        </footer>
      </div>
    </main>
  );
}

function useProjectData(): ProjectData & { refresh: () => Promise<void> } {
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

function normalizeDetectedObjects(objects?: unknown[]): string[] {
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

function HeaderMetric({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <div className="flex h-10 items-center gap-2 rounded-lg border border-white/10 bg-white/4 px-3">
      <Icon className={cn('size-4', tone)} />
      <span className="text-[11px] text-slate-500 uppercase">{label}</span>
      <span className="text-sm font-semibold text-white tabular-nums">{value}</span>
    </div>
  );
}

function StatusBadge({ state, label }: { state: string; label: string }) {
  const color =
    state === 'atencao'
      ? 'border-rose-300/30 bg-rose-300/10 text-rose-100'
      : state === 'offline'
        ? 'border-slate-400/20 bg-slate-400/10 text-slate-300'
        : 'border-emerald-300/30 bg-emerald-300/10 text-emerald-100';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium',
        color
      )}
    >
      <span className="size-1.5 rounded-full bg-current" />
      {label}
    </span>
  );
}

function Panel({
  title,
  icon: Icon,
  children,
  action,
  className,
}: {
  title: string;
  icon: ComponentType<{ className?: string }>;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        'rounded-xl border border-white/10 bg-white/4.5 p-4 shadow-xl shadow-black/20 backdrop-blur-md',
        className
      )}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <Icon className="size-4 shrink-0 text-cyan-200" />
          <h2 className="truncate text-sm font-semibold text-slate-100">{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function SystemPanel({
  health,
  telemetry,
  isThinking,
  isConnected,
}: {
  health: ReturnType<typeof useJarvisData>['health'];
  telemetry: TelemetryData | null;
  isThinking: boolean;
  isConnected: boolean;
}) {
  return (
    <Panel title="Estado do sistema" icon={Activity}>
      <div className="grid gap-3">
        <Meter label="Processador" value={health.cpu} icon={Cpu} tone="bg-cyan-300" />
        <Meter label="Memória" value={health.ram} icon={HardDrive} tone="bg-emerald-300" />
        <Meter
          label="Threads ativas"
          value={Math.min((telemetry?.hardware.threads ?? 0) * 4, 100)}
          icon={Network}
          tone="bg-amber-300"
          suffix={String(telemetry?.hardware.threads ?? '-')}
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
        <StateTile
          icon={Radio}
          label="Voz"
          value={isConnected ? 'conectada' : 'manual'}
          active={isConnected}
        />
        <StateTile
          icon={Zap}
          label="Raciocinio"
          value={isThinking ? 'ativo' : 'ocioso'}
          active={isThinking}
        />
      </div>
    </Panel>
  );
}

function Meter({
  label,
  value,
  icon: Icon,
  tone,
  suffix,
}: {
  label: string;
  value: number;
  icon: ComponentType<{ className?: string }>;
  tone: string;
  suffix?: string;
}) {
  const clamped = Math.max(0, Math.min(100, value || 0));
  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-xs">
        <span className="flex items-center gap-2 text-slate-400">
          <Icon className="size-3.5" />
          {label}
        </span>
        <span className="font-semibold text-slate-100 tabular-nums">
          {suffix ?? `${clamped.toFixed(0)}%`}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <motion.div
          className={cn('h-full rounded-full', tone)}
          animate={{ width: `${clamped}%` }}
          transition={{ duration: 0.6 }}
        />
      </div>
    </div>
  );
}

function StateTile({
  icon: Icon,
  label,
  value,
  active,
}: {
  icon: ComponentType<{ className?: string }>;
  label: string;
  value: string;
  active?: boolean;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <Icon className={cn('mb-2 size-4', active ? 'text-emerald-200' : 'text-slate-500')} />
      <div className="text-[11px] text-slate-500 uppercase">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-100">{value}</div>
    </div>
  );
}

function ModulePanel() {
  return (
    <Panel title="Mapa funcional" icon={Radar}>
      <div className="space-y-2">
        {roadmap.map((item) => (
          <div
            key={item.label}
            className="flex items-center justify-between rounded-lg border border-white/10 bg-black/20 px-3 py-2"
          >
            <span className="text-sm text-slate-300">{item.label}</span>
            <span className="rounded-full bg-white/8 px-2 py-0.5 text-[11px] text-slate-400 uppercase">
              {item.state}
            </span>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function CommandCenter({
  status,
  connected,
  error,
  draft,
  setDraft,
  onSend,
  onConnect,
  onDisconnect,
  messages,
}: {
  status: string;
  connected: boolean;
  error: string | null;
  draft: string;
  setDraft: (value: string) => void;
  onSend: () => Promise<void>;
  onConnect: () => Promise<void>;
  onDisconnect: () => void;
  messages: { role: 'user' | 'assistant'; content: string; timestamp: string }[];
}) {
  return (
    <Panel
      title="Centro de comando"
      icon={MessageSquareText}
      className="min-h-[420px]"
      action={
        <button
          onClick={connected ? onDisconnect : onConnect}
          className={cn(
            'inline-flex h-9 items-center gap-2 rounded-lg px-3 text-xs font-semibold transition',
            connected
              ? 'bg-rose-400/12 text-rose-100 hover:bg-rose-400/20'
              : 'bg-emerald-300/12 text-emerald-100 hover:bg-emerald-300/20'
          )}
        >
          <Power className="size-4" />
          {connected ? 'Desconectar' : 'Ativar voz'}
        </button>
      }
    >
      <div className="grid min-h-[340px] gap-4 lg:grid-cols-[1fr_260px]">
        <div className="flex min-h-0 flex-col rounded-lg border border-white/10 bg-[#080b11]/80">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <div>
              <div className="text-sm font-medium text-white">Conversas e comandos</div>
              <div className="text-xs text-slate-500">{error || status}</div>
            </div>
            <Mic className={cn('size-5', connected ? 'text-emerald-200' : 'text-slate-600')} />
          </div>

          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
            <AnimatePresence initial={false}>
              {messages.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="grid h-full min-h-40 place-items-center text-center"
                >
                  <div>
                    <Sparkles className="mx-auto mb-3 size-8 text-cyan-200/70" />
                    <p className="text-sm font-medium text-slate-200">Pronto para operar.</p>
                    <p className="mt-1 max-w-sm text-sm text-slate-500">
                      Digite um comando ou ative a voz para conversar com o Jarvis.
                    </p>
                  </div>
                </motion.div>
              ) : (
                messages.slice(-8).map((message, index) => (
                  <motion.div
                    key={`${message.timestamp}-${index}`}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn(
                      'max-w-[88%] rounded-lg px-3 py-2 text-sm',
                      message.role === 'user'
                        ? 'ml-auto bg-cyan-300/[0.12] text-cyan-50'
                        : 'bg-white/8 text-slate-100'
                    )}
                  >
                    <div className="mb-1 text-[10px] text-slate-500 uppercase">
                      {message.role === 'user' ? 'Will' : 'Jarvis'} · {message.timestamp}
                    </div>
                    <div className="leading-relaxed">{message.content}</div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>

          <div className="border-t border-white/10 p-3">
            <div className="flex gap-2">
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    onSend();
                  }
                }}
                rows={2}
                placeholder="Ex: resumir logs de hoje, salvar memoria, analisar capturas..."
                className="min-h-12 flex-1 resize-none rounded-lg border border-white/10 bg-white/4 px-3 py-2 text-sm text-white transition outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
              />
              <button
                onClick={onSend}
                className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-cyan-200 text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-500"
                disabled={!draft.trim()}
                title="Enviar comando"
              >
                <Send className="size-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="grid content-start gap-3">
          <FocusSignal
            label="Escuta"
            value={connected ? 'ativa' : 'manual'}
            icon={Mic}
            active={connected}
          />
          <FocusSignal
            label="Pipeline"
            value={error ? 'erro' : 'pronto'}
            icon={Activity}
            active={!error}
          />
          <FocusSignal label="Memória" value="consulta HTTP" icon={Database} active />
          <FocusSignal label="Segurança" value="Sentinel" icon={ShieldCheck} active />
        </div>
      </div>
    </Panel>
  );
}

function FocusSignal({
  label,
  value,
  icon: Icon,
  active,
}: {
  label: string;
  value: string;
  icon: ComponentType<{ className?: string }>;
  active?: boolean;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <div className="mb-3 flex items-center justify-between">
        <Icon className={cn('size-4', active ? 'text-cyan-200' : 'text-slate-500')} />
        <span className={cn('size-2 rounded-full', active ? 'bg-emerald-300' : 'bg-slate-600')} />
      </div>
      <div className="text-[11px] text-slate-500 uppercase">{label}</div>
      <div className="mt-1 text-sm font-semibold text-slate-100">{value}</div>
    </div>
  );
}

function TimelinePanel({
  history,
  healthCpu,
  healthRam,
}: {
  history: TelemetryHistoryItem[];
  healthCpu: number;
  healthRam: number;
}) {
  const points = useMemo(() => {
    const source =
      history.length > 0
        ? history
        : [{ cpu: healthCpu, memory: healthRam, timestamp: new Date().toISOString() }];
    return source.slice(-18).map((item, index) => ({
      cpu: Math.max(0, Math.min(100, item.cpu ?? 0)),
      memory: Math.max(0, Math.min(100, item.memory ?? item.ram ?? 0)),
      label: item.timestamp
        ? new Date(item.timestamp).toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
          })
        : String(index + 1),
    }));
  }, [history, healthCpu, healthRam]);

  const chartPath = (key: 'cpu' | 'memory') => {
    if (points.length === 1) return `M 0 ${100 - points[0][key]}`;
    return points
      .map((point, index) => {
        const x = (index / (points.length - 1)) * 100;
        const y = 100 - point[key];
        return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
      })
      .join(' ');
  };

  return (
    <Panel title="Telemetria temporal" icon={Gauge}>
      <div className="h-56 rounded-lg border border-white/10 bg-[#080b11] p-4">
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="h-full w-full overflow-visible"
        >
          <path
            d="M 0 25 H 100 M 0 50 H 100 M 0 75 H 100"
            stroke="rgba(255,255,255,.08)"
            strokeWidth="0.5"
            vectorEffect="non-scaling-stroke"
          />
          <path
            d={chartPath('cpu')}
            fill="none"
            stroke="#67e8f9"
            strokeWidth="2.2"
            vectorEffect="non-scaling-stroke"
          />
          <path
            d={chartPath('memory')}
            fill="none"
            stroke="#86efac"
            strokeWidth="2.2"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-cyan-300" />
          CPU
        </span>
        <span className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-emerald-300" />
          RAM
        </span>
        <span>{points.length} amostras</span>
      </div>
    </Panel>
  );
}

function PerceptionPanel({
  telemetry,
  activeObjects,
}: {
  telemetry: TelemetryData | null;
  activeObjects: string[];
}) {
  return (
    <Panel title="Percepção ao vivo" icon={Eye}>
      <div className="grid gap-3 sm:grid-cols-2">
        <StateTile
          icon={Camera}
          label="Identidade"
          value={telemetry?.perception.face_identity || 'sem rosto'}
          active={!!telemetry?.perception.face_identity}
        />
        <StateTile
          icon={Brain}
          label="Afeto"
          value={telemetry?.perception.face_emotion || 'neutro'}
          active={!!telemetry?.perception.face_emotion}
        />
      </div>
      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between text-xs text-slate-500">
          <span>Objetos detectados</span>
          <span>{activeObjects.length}</span>
        </div>
        <div className="flex min-h-20 flex-wrap content-start gap-2 rounded-lg border border-white/10 bg-black/20 p-3">
          {activeObjects.length > 0 ? (
            activeObjects.slice(0, 10).map((object) => (
              <span
                key={object}
                className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-2 py-1 text-xs text-emerald-100"
              >
                {object}
              </span>
            ))
          ) : (
            <span className="text-sm text-slate-500">Nenhum objeto no snapshot atual.</span>
          )}
        </div>
      </div>
    </Panel>
  );
}

function BrainPanel({
  memories,
  vaultStats,
  personaTraits,
}: {
  memories: MemoryItem[];
  vaultStats: VaultStats | null;
  personaTraits: [string, number][];
}) {
  const memoryPreview = memories.slice(0, 3);
  return (
    <Panel title="Segundo cerebro" icon={Brain}>
      <div className="grid grid-cols-2 gap-2">
        <StateTile
          icon={FileText}
          label="Memórias"
          value={String(memories.length)}
          active={memories.length > 0}
        />
        <StateTile
          icon={ListTodo}
          label="Notas vault"
          value={String(vaultStats?.total_notes ?? vaultStats?.total_memories ?? '-')}
          active={!!vaultStats}
        />
      </div>

      <div className="mt-4 space-y-2">
        {memoryPreview.length > 0 ? (
          memoryPreview.map((memory, index) => (
            <div
              key={memory.id ?? index}
              className="rounded-lg border border-white/10 bg-black/20 p-3"
            >
              <div className="line-clamp-1 text-sm font-medium text-slate-200">
                {memory.title || memory.memory || memory.text || 'Memória registrada'}
              </div>
              <div className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">
                {memory.content || memory.text || memory.memory || 'Sem conteúdo textual exposto.'}
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-white/10 bg-black/20 p-3 text-sm text-slate-500">
            Memórias aparecem aqui quando o backend responder em `/memory`.
          </div>
        )}
      </div>

      {personaTraits.length > 0 && (
        <div className="mt-4">
          <div className="mb-2 text-xs text-slate-500 uppercase">Traços de persona</div>
          <div className="space-y-2">
            {personaTraits.map(([trait, value]) => (
              <Meter
                key={trait}
                label={trait}
                value={Number(value) * 100}
                icon={Sparkles}
                tone="bg-sky-300"
              />
            ))}
          </div>
        </div>
      )}
    </Panel>
  );
}

function KnowledgeCapturePanel({
  memoryDraft,
  noteDraft,
  saveStatus,
  isSaving,
  onMemoryDraftChange,
  onNoteDraftChange,
  onSaveMemory,
  onSaveNote,
}: {
  memoryDraft: {
    title: string;
    content: string;
    project: string;
    keywords: string;
    importance: string;
  };
  noteDraft: { title: string; body: string };
  saveStatus: SaveStatus;
  isSaving: boolean;
  onMemoryDraftChange: (value: {
    title: string;
    content: string;
    project: string;
    keywords: string;
    importance: string;
  }) => void;
  onNoteDraftChange: (value: { title: string; body: string }) => void;
  onSaveMemory: () => Promise<void>;
  onSaveNote: () => Promise<void>;
}) {
  return (
    <Panel title="Captura de conhecimento" icon={FileText}>
      <div className="space-y-4">
        <div className="rounded-lg border border-white/10 bg-black/20 p-3">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-white">Memória episódica</div>
              <div className="text-xs text-slate-500">POST /vault-memory</div>
            </div>
            <Database className="size-4 text-cyan-200" />
          </div>
          <div className="space-y-2">
            <input
              value={memoryDraft.title}
              onChange={(event) =>
                onMemoryDraftChange({ ...memoryDraft, title: event.target.value })
              }
              placeholder="Titulo da memoria"
              className="h-9 w-full rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <textarea
              value={memoryDraft.content}
              onChange={(event) =>
                onMemoryDraftChange({ ...memoryDraft, content: event.target.value })
              }
              rows={4}
              placeholder="O que o Jarvis deve lembrar?"
              className="w-full resize-none rounded-lg border border-white/10 bg-white/4 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <div className="grid gap-2 sm:grid-cols-2">
              <input
                value={memoryDraft.project}
                onChange={(event) =>
                  onMemoryDraftChange({ ...memoryDraft, project: event.target.value })
                }
                placeholder="Projeto"
                className="h-9 rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
              />
              <select
                value={memoryDraft.importance}
                onChange={(event) =>
                  onMemoryDraftChange({ ...memoryDraft, importance: event.target.value })
                }
                className="h-9 rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none focus:border-cyan-200/40"
              >
                <option value="BAIXA">Baixa</option>
                <option value="MEDIA">Media</option>
                <option value="ALTA">Alta</option>
                <option value="CRITICA">Critica</option>
              </select>
            </div>
            <input
              value={memoryDraft.keywords}
              onChange={(event) =>
                onMemoryDraftChange({ ...memoryDraft, keywords: event.target.value })
              }
              placeholder="keywords, separadas, por virgula"
              className="h-9 w-full rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <button
              onClick={onSaveMemory}
              disabled={isSaving}
              className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-lg bg-cyan-200 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:bg-slate-700 disabled:text-slate-500"
            >
              <Send className="size-4" />
              Salvar memoria
            </button>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-black/20 p-3">
          <div className="mb-3 text-sm font-semibold text-white">Nota rápida</div>
          <div className="space-y-2">
            <input
              value={noteDraft.title}
              onChange={(event) => onNoteDraftChange({ ...noteDraft, title: event.target.value })}
              placeholder="Titulo da nota"
              className="h-9 w-full rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <textarea
              value={noteDraft.body}
              onChange={(event) => onNoteDraftChange({ ...noteDraft, body: event.target.value })}
              rows={3}
              placeholder="Conteudo para /notes"
              className="w-full resize-none rounded-lg border border-white/10 bg-white/4 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <button
              onClick={onSaveNote}
              disabled={isSaving}
              className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/6 text-sm font-semibold text-slate-100 transition hover:border-emerald-200/30 hover:bg-emerald-200/10 disabled:text-slate-500"
            >
              <FileText className="size-4" />
              Criar nota
            </button>
          </div>
        </div>

        {saveStatus.type !== 'idle' && (
          <div
            className={cn(
              'rounded-lg border px-3 py-2 text-sm',
              saveStatus.type === 'success'
                ? 'border-emerald-300/20 bg-emerald-300/10 text-emerald-100'
                : 'border-rose-300/20 bg-rose-300/10 text-rose-100'
            )}
          >
            {saveStatus.message}
          </div>
        )}
      </div>
    </Panel>
  );
}

function VisionPanel({ screenshot, objects }: { screenshot?: string; objects: string[] }) {
  return (
    <Panel title="Visão e capturas" icon={Camera}>
      <div className="aspect-video overflow-hidden rounded-lg border border-white/10 bg-black/30">
        {screenshot ? (
          // Backend screenshots are local runtime artifacts, so a plain img keeps them unconfigured and live.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={jarvisApi(`/screenshots/${screenshot}`)}
            alt="Ultima captura do Jarvis"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="grid h-full place-items-center text-center text-sm text-slate-500">
            <div>
              <Search className="mx-auto mb-2 size-6 text-slate-600" />
              Aguardando capturas
            </div>
          </div>
        )}
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span>{screenshot || 'sem arquivo recente'}</span>
        <span>{objects.length} objetos</span>
      </div>
    </Panel>
  );
}

function ConsolePanel({ logs }: { logs: string[] }) {
  return (
    <Panel title="Logs de hoje" icon={Terminal}>
      <div className="max-h-72 space-y-2 overflow-y-auto rounded-lg border border-white/10 bg-[#06080d] p-3 font-mono text-xs">
        {logs.length > 0 ? (
          logs.map((line, index) => (
            <div key={`${line}-${index}`} className="flex gap-2 text-slate-400">
              <span className="text-cyan-300">{'>'}</span>
              <span className="line-clamp-2">{line}</span>
            </div>
          ))
        ) : (
          <div className="text-slate-600">Sem logs carregados para hoje.</div>
        )}
      </div>
    </Panel>
  );
}
