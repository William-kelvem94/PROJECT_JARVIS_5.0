'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Code,
  FileJson,
  GitBranch,
  Loader,
  Terminal,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';
import { LogHistoryModal } from './log-history-modal';

interface ActivityLog {
  id: string;
  title: string;
  detail: string;
  log_type: 'cmd' | 'edit' | 'git' | 'info';
  status: 'pending' | 'success' | 'error';
  timestamp: string;
}

interface ExternalLog {
  type?: 'activity_log' | string;
  log_type?: 'cmd' | 'edit' | 'git' | 'info';
  title?: string;
  text?: string;
  detail?: string;
  role?: 'user' | 'assistant' | string;
  status?: 'pending' | 'success' | 'error';
}

interface ActiveConsoleProps {
  externalLogs?: ExternalLog[]; // Logs vindos do WebSocket Nativo
}

export function ActiveConsole({ externalLogs = [] }: ActiveConsoleProps) {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Converte mensagens do WebSocket em logs visuais do console
  useEffect(() => {
    if (!externalLogs || externalLogs.length === 0) return;

    const latest = externalLogs[externalLogs.length - 1];
    if (!latest) return;

    // Se for um log de atividade (comando, edição, etc)
    if (latest.type === 'activity_log' || latest.log_type) {
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
        title: latest.title || (latest.role === 'user' ? 'Input do Usuário' : 'Resposta Jarvis'),
        detail: latest.detail || latest.text || '',
        log_type: (latest.log_type as any) || 'info',
        status: (latest.status as any) || 'success',
        timestamp: new Date().toLocaleTimeString(),
      };

      setLogs((prev) => [...prev.slice(-9), newLog]);
    }
  }, [externalLogs]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  if (logs.length === 0) return null;

  const getLogIcon = (log: ActivityLog) => {
    if (log.status === 'pending') return <Loader className="size-3 animate-spin text-yellow-400" />;

    switch (log.log_type) {
      case 'cmd':
        return <Terminal className="size-3 text-yellow-400" />;
      case 'edit':
        return <Code className="size-3 text-blue-400" />;
      case 'git':
        return <GitBranch className="size-3 text-orange-400" />;
      case 'info':
        return <FileJson className="size-3 animate-pulse text-cyan-400" />;
      default:
        return <FileJson className="size-3 text-emerald-400" />;
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === 'success') return <CheckCircle2 className="size-2 text-emerald-500" />;
    if (status === 'error') return <AlertTriangle className="size-2 text-red-500" />;
    return null;
  };

  return (
    <>
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="cyber-glass fixed bottom-32 left-6 z-50 w-80 overflow-hidden rounded-xl border border-[#1da3b9]/20"
      >
        <div className="flex items-center justify-between border-b border-[#1da3b9]/20 bg-[#1da3b9]/10 p-2">
          <div className="flex items-center gap-2">
            <Terminal className="size-3 text-[#1da3b9]" />
            <span className="font-mono text-[9px] tracking-widest text-white/50 uppercase">
              Active Action Log (Offline)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsHistoryOpen(true)}
              className="rounded bg-white/5 p-1 transition-colors hover:bg-white/10"
              title="Ver Histórico Completo"
            >
              <FileJson className="size-3 text-[#1da3b9]" />
            </button>
            <div className="size-1.5 rounded-full bg-emerald-500/50" />
            <div className="size-1.5 animate-pulse rounded-full bg-[#1da3b9]/50" />
          </div>
        </div>

        <div
          ref={scrollRef}
          className="scrollbar-none max-h-56 space-y-3 overflow-y-auto p-3 font-mono text-[10px]"
        >
          <AnimatePresence mode="popLayout">
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10, scale: 0.95 }}
                animate={{
                  opacity: 1,
                  x: 0,
                  scale: 1,
                  boxShadow: log.log_type === 'info' ? '0 0 15px rgba(34, 211, 238, 0.1)' : 'none',
                }}
                className={cn(
                  'group ml-1 flex flex-col gap-1 border-l pl-2 transition-all duration-300',
                  log.log_type === 'info'
                    ? 'border-cyan-400/50 bg-cyan-400/5 py-1 ring-1 ring-cyan-400/20'
                    : 'border-white/5 bg-white/0'
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getLogIcon(log)}
                    <span className="font-bold tracking-tight text-white/90">{log.title}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(log.status)}
                    <span className="text-[8px] text-white/20">[{log.timestamp}]</span>
                  </div>
                </div>
                {log.detail && (
                  <div className="ml-5 rounded-sm bg-white/5 p-1 text-[9px] leading-relaxed break-all text-white/40">
                    {log.detail}
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      <LogHistoryModal isOpen={isHistoryOpen} onClose={() => setIsHistoryOpen(false)} />
    </>
  );
}
