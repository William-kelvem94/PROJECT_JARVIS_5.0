'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Terminal, Code, GitBranch, FileJson, Loader, CheckCircle2, AlertTriangle } from 'lucide-react';
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

interface ActiveConsoleProps {
    externalLogs?: any[]; // Logs vindos do WebSocket Nativo
}

export function ActiveConsole({ externalLogs = [] }: ActiveConsoleProps) {
    const [logs, setLogs] = useState<ActivityLog[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Converte mensagens do WebSocket em logs visuais do console
    useEffect(() => {
        if (externalLogs.length === 0) return;

        const latest = externalLogs[externalLogs.length - 1];
        
        // Se for um log de atividade (comando, edição, etc)
        if (latest.type === 'activity_log' || latest.log_type) {
            const newLog: ActivityLog = {
                id: Math.random().toString(36).substr(2, 9),
                title: latest.title || (latest.role === 'user' ? 'Input do Usuário' : 'Resposta Jarvis'),
                detail: latest.detail || latest.text || "",
                log_type: latest.log_type || 'info',
                status: latest.status || "success",
                timestamp: new Date().toLocaleTimeString(),
            };
            
            setLogs(prev => [...prev.slice(-9), newLog]);
        }
    }, [externalLogs]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    if (logs.length === 0) return null;

    const getLogIcon = (log: ActivityLog) => {
        if (log.status === 'pending') return <Loader className="size-3 animate-spin text-yellow-400" />;

        switch (log.log_type) {
            case 'cmd': return <Terminal className="size-3 text-yellow-400" />;
            case 'edit': return <Code className="size-3 text-blue-400" />;
            case 'git': return <GitBranch className="size-3 text-orange-400" />;
            case 'info': return <FileJson className="size-3 text-cyan-400 animate-pulse" />;
            default: return <FileJson className="size-3 text-emerald-400" />;
        }
    };

    const getStatusIcon = (status: string) => {
        if (status === 'success') return <CheckCircle2 className="size-2 text-emerald-500" />;
        if (status === 'error') return <AlertTriangle className="size-2 text-red-500" />;
        return null;
    };

    const [isHistoryOpen, setIsHistoryOpen] = useState(false);

    return (
        <>
            <motion.div
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="fixed left-6 bottom-32 z-50 w-80 cyber-glass rounded-xl overflow-hidden border border-[#1da3b9]/20"
            >
                <div className="bg-[#1da3b9]/10 p-2 flex items-center justify-between border-b border-[#1da3b9]/20">
                    <div className="flex items-center gap-2">
                        <Terminal className="size-3 text-[#1da3b9]" />
                        <span className="text-[9px] font-mono text-white/50 uppercase tracking-widest">Active Action Log (Offline)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setIsHistoryOpen(true)}
                            className="bg-white/5 hover:bg-white/10 p-1 rounded transition-colors"
                            title="Ver Histórico Completo"
                        >
                            <FileJson className="size-3 text-[#1da3b9]" />
                        </button>
                        <div className="size-1.5 rounded-full bg-emerald-500/50" />
                        <div className="size-1.5 rounded-full bg-[#1da3b9]/50 animate-pulse" />
                    </div>
                </div>

                <div
                    ref={scrollRef}
                    className="p-3 max-h-56 overflow-y-auto font-mono text-[10px] space-y-3 scrollbar-none"
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
                                    boxShadow: log.log_type === 'info' ? "0 0 15px rgba(34, 211, 238, 0.1)" : "none"
                                }}
                                className={cn(
                                    "group flex flex-col gap-1 border-l pl-2 ml-1 transition-all duration-300",
                                    log.log_type === 'info'
                                        ? "border-cyan-400/50 bg-cyan-400/5 ring-1 ring-cyan-400/20 py-1"
                                        : "border-white/5 bg-white/0"
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
                                    <div className="text-[9px] text-white/40 leading-relaxed break-all bg-white/5 p-1 rounded-sm ml-5">
                                        {log.detail}
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </motion.div>

            <LogHistoryModal
                isOpen={isHistoryOpen}
                onClose={() => setIsHistoryOpen(false)}
            />
        </>
    );
}
