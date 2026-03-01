'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar, Search, Filter, Terminal, Code, GitBranch, FileJson, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/shadcn/utils';

interface LogHistoryModalProps {
    isOpen: boolean;
    onClose: () => void;
    apiUrl?: string;
}

interface ActivityLog {
    title: string;
    detail: string;
    log_type: 'cmd' | 'edit' | 'git' | 'info';
    status: 'pending' | 'success' | 'error';
    timestamp: string;
}

export function LogHistoryModal({ isOpen, onClose, apiUrl = 'http://localhost:8000' }: LogHistoryModalProps) {
    const [dates, setDates] = useState<string[]>([]);
    const [selectedDate, setSelectedDate] = useState<string>('');
    const [logs, setLogs] = useState<ActivityLog[]>([]);
    const [filter, setFilter] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetch(`${apiUrl}/logs`)
                .then(res => res.json())
                .then(data => {
                    setDates(data.dates);
                    if (data.dates.length > 0) setSelectedDate(data.dates[0]);
                });
        }
    }, [isOpen, apiUrl]);

    useEffect(() => {
        if (selectedDate) {
            setLoading(true);
            fetch(`${apiUrl}/logs/${selectedDate}`)
                .then(res => res.json())
                .then(data => {
                    setLogs(data.logs);
                    setLoading(false);
                })
                .catch(() => setLoading(false));
        }
    }, [selectedDate, apiUrl]);

    const filteredLogs = logs.filter(log =>
        log.title.toLowerCase().includes(filter.toLowerCase()) ||
        log.detail.toLowerCase().includes(filter.toLowerCase())
    );

    const getIcon = (type: string) => {
        switch (type) {
            case 'cmd': return <Terminal className="size-4 text-yellow-400" />;
            case 'edit': return <Code className="size-4 text-blue-400" />;
            case 'git': return <GitBranch className="size-4 text-orange-400" />;
            default: return <FileJson className="size-4 text-emerald-400" />;
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                    className="w-full max-w-4xl h-[80vh] cyber-glass border border-[#1da3b9]/30 rounded-2xl flex flex-col overflow-hidden shadow-2xl shadow-[#1da3b9]/20"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-[#1da3b9]/20 flex items-center justify-between bg-[#1da3b9]/5">
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-[#1da3b9]/20 rounded-lg">
                                <Terminal className="size-6 text-[#1da3b9]" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-white tracking-tight">Audit Log History</h2>
                                <p className="text-xs text-white/40 uppercase tracking-widest font-mono">System Activity Record</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/5 rounded-full transition-colors text-white/50 hover:text-white"
                        >
                            <X className="size-6" />
                        </button>
                    </div>

                    {/* Toolbar */}
                    <div className="p-4 border-b border-white/5 bg-black/20 flex flex-wrap gap-4 items-center">
                        <div className="flex items-center gap-2 bg-white/5 px-3 py-2 rounded-lg border border-white/10 shrink-0">
                            <Calendar className="size-4 text-[#1da3b9]" />
                            <select
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                className="bg-transparent text-sm text-white outline-none cursor-pointer"
                            >
                                {dates.map(date => (
                                    <option key={date} value={date} className="bg-neutral-900">{date}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex-1 flex items-center gap-2 bg-white/5 px-3 py-2 rounded-lg border border-white/10 min-w-[200px]">
                            <Search className="size-4 text-white/30" />
                            <input
                                type="text"
                                placeholder="Filtrar por comando ou detalhe..."
                                value={filter}
                                onChange={(e) => setFilter(e.target.value)}
                                className="bg-transparent text-sm text-white outline-none w-full"
                            />
                        </div>

                        <Button variant="outline" size="sm" className="gap-2 border-[#1da3b9]/20 hover:bg-[#1da3b9]/10">
                            <Download className="size-4" />
                            <span className="hidden sm:inline">Export JSON</span>
                        </Button>
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-y-auto p-0 font-mono text-sm scrollbar-thin">
                        {loading ? (
                            <div className="h-full flex flex-col items-center justify-center text-white/20 gap-4">
                                <div className="size-12 rounded-full border-t-2 border-[#1da3b9] animate-spin" />
                                <span className="text-xs uppercase tracking-widest">Acessing Archives...</span>
                            </div>
                        ) : filteredLogs.length > 0 ? (
                            <table className="w-full text-left border-collapse">
                                <thead className="sticky top-0 bg-black/80 backdrop-blur-md text-[10px] uppercase tracking-wider text-white/40 border-b border-white/5">
                                    <tr>
                                        <th className="p-4 font-normal">Status</th>
                                        <th className="p-4 font-normal text-[#1da3b9]">Type</th>
                                        <th className="p-4 font-normal">Action</th>
                                        <th className="p-4 font-normal">Details</th>
                                        <th className="p-4 font-normal text-right">Time</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredLogs.map((log, i) => (
                                        <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors group">
                                            <td className="p-4 whitespace-nowrap">
                                                <div className={cn(
                                                    "size-2 rounded-full",
                                                    log.status === 'success' ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"
                                                )} />
                                            </td>
                                            <td className="p-4">
                                                <div className="flex items-center gap-2">
                                                    {getIcon(log.log_type)}
                                                    <span className="text-[10px] text-white/30 uppercase">{log.log_type}</span>
                                                </div>
                                            </td>
                                            <td className="p-4 font-bold text-white/90 whitespace-nowrap">{log.title}</td>
                                            <td className="p-4 text-white/50 text-xs break-all max-w-md">{log.detail}</td>
                                            <td className="p-4 text-right text-white/20 text-[10px] whitespace-nowrap">
                                                {new Date(log.timestamp).toLocaleTimeString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-white/10 gap-2">
                                <Filter className="size-12 opacity-10" />
                                <span className="text-sm">Nenhum log encontrado para esta data ou filtro.</span>
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
