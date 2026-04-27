'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  Warning,
  CheckCircle,
  Code,
  FileJs,
  GitBranch,
  CircleNotch,
  Terminal,
  Pulse,
  Archive,
} from '@phosphor-icons/react';
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
  content?: string;
  timestamp?: string;
  status?: 'pending' | 'success' | 'error';
}

type ActivityLogType = ActivityLog['log_type'];
type ActivityStatus = ActivityLog['status'];

interface ActiveConsoleProps {
  externalLogs?: ExternalLog[];
}

export function ActiveConsole({ externalLogs = [] }: ActiveConsoleProps) {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  useEffect(() => {
    if (!externalLogs || externalLogs.length === 0) return;

    const latest = externalLogs[externalLogs.length - 1];
    if (!latest) return;

    if (latest.type === 'activity_log' || latest.log_type) {
      const newLog: ActivityLog = {
        id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        title: latest.title || (latest.role === 'user' ? 'Input Usuário' : 'Processamento Jarvis'),
        detail: latest.detail || latest.text || '',
        log_type: (latest.log_type as ActivityLogType) || 'info',
        status: (latest.status as ActivityStatus) || 'success',
        timestamp: new Date().toLocaleTimeString(),
      };

      setLogs((prev) => [...prev.slice(-14), newLog]);
      return;
    }

    if (latest.role && latest.content) {
      const newLog: ActivityLog = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
        title: latest.role === 'user' ? 'Comando Recebido' : 'Resposta Sistema',
        detail: latest.content,
        log_type: 'info',
        status: 'success',
        timestamp: latest.timestamp || new Date().toLocaleTimeString(),
      };
      setLogs((prev) => [...prev.slice(-14), newLog]);
    }
  }, [externalLogs]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [logs]);

  if (logs.length === 0) return null;

  const getLogIcon = (log: ActivityLog) => {
    if (log.status === 'pending') return <CircleNotch className="size-3.5 animate-spin text-amber-400" />;

    switch (log.log_type) {
      case 'cmd': return <Terminal weight="bold" className="size-3.5 text-amber-400" />;
      case 'edit': return <Code weight="bold" className="size-3.5 text-blue-400" />;
      case 'git': return <GitBranch weight="bold" className="size-3.5 text-orange-400" />;
      default: return <Pulse weight="bold" className="size-3.5 text-jarvis-cyan" />;
    }
  };

  const getStatusColor = (status: string) => {
    if (status === 'success') return 'text-green-500';
    if (status === 'error') return 'text-red-500';
    return 'text-amber-500';
  };

  return (
    <>
      <motion.div
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="cyber-glass fixed bottom-32 left-6 z-50 w-80 overflow-hidden rounded-xl border-jarvis-cyan/20 shadow-[0_0_20px_rgba(0,242,255,0.1)]"
      >
        {/* Header Console */}
        <div className="flex items-center justify-between border-b border-white/5 bg-white/[0.03] px-3 py-2.5">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Terminal weight="duotone" className="size-4 text-jarvis-cyan" />
              <motion.div 
                animate={{ opacity: [0, 1, 0] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="absolute -right-1 bottom-0 size-1 rounded-full bg-jarvis-cyan"
              />
            </div>
            <span className="font-mono text-[9px] font-bold tracking-[0.2em] text-white/50 uppercase">
              Terminal Output
            </span>
          </div>
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setIsHistoryOpen(true)}
              className="group relative rounded-md bg-white/5 p-1.5 transition-all hover:bg-jarvis-cyan/20"
              title="Histórico Completo"
            >
              <Archive weight="duotone" className="size-3.5 text-jarvis-cyan/60 group-hover:text-jarvis-cyan" />
            </button>
            <div className="flex gap-1">
              <div className="size-1 rounded-full bg-jarvis-cyan/40 animate-pulse" />
              <div className="size-1 rounded-full bg-jarvis-cyan/20" />
            </div>
          </div>
        </div>

        {/* Content Area */}
        <div
          ref={scrollRef}
          className="scrollbar-none max-h-[320px] space-y-1.5 overflow-y-auto p-2 font-mono text-[10px]"
        >
          <AnimatePresence initial={false} mode="popLayout">
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10, filter: 'blur(4px)' }}
                animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={cn(
                  'relative group flex flex-col gap-1 rounded-lg border border-white/0 px-2 py-1.5 transition-all hover:bg-white/[0.03]',
                  log.status === 'error' ? 'bg-red-500/5 border-red-500/10' : '',
                  log.log_type === 'cmd' ? 'bg-amber-500/5 border-amber-500/10' : ''
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="shrink-0">{getLogIcon(log)}</div>
                    <span className="font-bold tracking-tight text-white/80 line-clamp-1">{log.title}</span>
                  </div>
                  <span className="shrink-0 text-[7px] text-white/20 tabular-nums">
                    [{log.timestamp}]
                  </span>
                </div>
                
                {log.detail && (
                  <div className="ml-5 mt-0.5 border-l border-white/5 pl-2 font-mono text-[9px] leading-relaxed text-white/40 group-hover:text-white/60 transition-colors">
                    <div className="line-clamp-3 overflow-hidden text-ellipsis italic">
                      {">"} {log.detail}
                    </div>
                  </div>
                )}

                {/* Status Indicator Bar */}
                <div className={cn(
                  "absolute left-0 top-1 bottom-1 w-0.5 rounded-full",
                  log.status === 'success' ? 'bg-green-500/40' : 
                  log.status === 'error' ? 'bg-red-500/40' : 'bg-amber-500/40'
                )} />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Console Footer Decorator */}
        <div className="flex h-1 bg-linear-to-r from-transparent via-jarvis-cyan/10 to-transparent" />
      </motion.div>

      <LogHistoryModal isOpen={isHistoryOpen} onClose={() => setIsHistoryOpen(false)} />
    </>
  );
}
