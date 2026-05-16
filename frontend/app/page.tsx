'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Cpu, Database, HardDrive, LayoutDashboard, RefreshCcw } from 'lucide-react';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { JarvisProvider, useJarvis } from '@/context/JarvisContext';
import { useJarvisData } from '@/hooks/use-jarvis-data';
import { jarvisApi } from '@/lib/jarvis-endpoints';
import { cn } from '@/lib/shadcn/utils';

import { SystemPanel } from '@/components/cockpit/system-panel';
import { ModulePanel } from '@/components/cockpit/module-panel';
import { CommandCenter } from '@/components/cockpit/command-center';
import { TimelinePanel } from '@/components/cockpit/timeline-panel';
import { PerceptionPanel } from '@/components/cockpit/perception-panel';
import { BrainPanel } from '@/components/cockpit/brain-panel';
import { KnowledgeCapturePanel } from '@/components/cockpit/knowledge-capture-panel';
import { VisionPanel } from '@/components/cockpit/vision-panel';
import { ConsolePanel } from '@/components/cockpit/console-panel';
import { StatusBadge } from '@/components/cockpit/status-badge';
import { HeaderMetric } from '@/components/cockpit/header-metric';
import { useProjectData, normalizeDetectedObjects } from '@/components/cockpit/use-project-data';
import type { SaveStatus } from '@/components/cockpit/types';

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
