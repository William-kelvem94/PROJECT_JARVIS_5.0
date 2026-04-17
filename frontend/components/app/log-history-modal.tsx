'use client';

import React, { useEffect, useState } from 'react';
import {
  Calendar,
  Code,
  Download,
  FileJson,
  Filter,
  GitBranch,
  Search,
  Terminal,
  X,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
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

export function LogHistoryModal({
  isOpen,
  onClose,
  apiUrl = 'http://localhost:8000',
}: LogHistoryModalProps) {
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetch(`${apiUrl}/logs`)
        .then((res) => res.json())
        .then((data) => {
          setDates(data.dates);
          if (data.dates.length > 0) setSelectedDate(data.dates[0]);
        });
    }
  }, [isOpen, apiUrl]);

  useEffect(() => {
    if (selectedDate) {
      setLoading(true);
      fetch(`${apiUrl}/logs/${selectedDate}`)
        .then((res) => res.json())
        .then((data) => {
          setLogs(data.logs);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }
  }, [selectedDate, apiUrl]);

  const filteredLogs = logs.filter(
    (log) =>
      log.title.toLowerCase().includes(filter.toLowerCase()) ||
      log.detail.toLowerCase().includes(filter.toLowerCase())
  );

  const getIcon = (type: string) => {
    switch (type) {
      case 'cmd':
        return <Terminal className="size-4 text-yellow-400" />;
      case 'edit':
        return <Code className="size-4 text-blue-400" />;
      case 'git':
        return <GitBranch className="size-4 text-orange-400" />;
      default:
        return <FileJson className="size-4 text-emerald-400" />;
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="cyber-glass flex h-[80vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-[#1da3b9]/30 shadow-2xl shadow-[#1da3b9]/20"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[#1da3b9]/20 bg-[#1da3b9]/5 p-6">
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-[#1da3b9]/20 p-2">
                <Terminal className="size-6 text-[#1da3b9]" />
              </div>
              <div>
                <h2 className="text-xl font-bold tracking-tight text-white">Audit Log History</h2>
                <p className="font-mono text-xs tracking-widest text-white/40 uppercase">
                  System Activity Record
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="rounded-full p-2 text-white/50 transition-colors hover:bg-white/5 hover:text-white"
            >
              <X className="size-6" />
            </button>
          </div>

          {/* Toolbar */}
          <div className="flex flex-wrap items-center gap-4 border-b border-white/5 bg-black/20 p-4">
            <div className="flex shrink-0 items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
              <Calendar className="size-4 text-[#1da3b9]" />
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="cursor-pointer bg-transparent text-sm text-white outline-none"
              >
                {dates.map((date) => (
                  <option key={date} value={date} className="bg-neutral-900">
                    {date}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex min-w-[200px] flex-1 items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2">
              <Search className="size-4 text-white/30" />
              <input
                type="text"
                placeholder="Filtrar por comando ou detalhe..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full bg-transparent text-sm text-white outline-none"
              />
            </div>

            <Button
              variant="outline"
              size="sm"
              className="gap-2 border-[#1da3b9]/20 hover:bg-[#1da3b9]/10"
            >
              <Download className="size-4" />
              <span className="hidden sm:inline">Export JSON</span>
            </Button>
          </div>

          {/* Content */}
          <div className="scrollbar-thin flex-1 overflow-y-auto p-0 font-mono text-sm">
            {loading ? (
              <div className="flex h-full flex-col items-center justify-center gap-4 text-white/20">
                <div className="size-12 animate-spin rounded-full border-t-2 border-[#1da3b9]" />
                <span className="text-xs tracking-widest uppercase">Acessing Archives...</span>
              </div>
            ) : filteredLogs.length > 0 ? (
              <table className="w-full border-collapse text-left">
                <thead className="sticky top-0 border-b border-white/5 bg-black/80 text-[10px] tracking-wider text-white/40 uppercase backdrop-blur-md">
                  <tr>
                    <th className="p-4 font-normal">Status</th>
                    <th className="p-4 font-normal text-[#1da3b9]">Type</th>
                    <th className="p-4 font-normal">Action</th>
                    <th className="p-4 font-normal">Details</th>
                    <th className="p-4 text-right font-normal">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map((log, i) => (
                    <tr
                      key={i}
                      className="group border-b border-white/5 transition-colors hover:bg-white/[0.02]"
                    >
                      <td className="p-4 whitespace-nowrap">
                        <div
                          className={cn(
                            'size-2 rounded-full',
                            log.status === 'success'
                              ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
                              : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'
                          )}
                        />
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          {getIcon(log.log_type)}
                          <span className="text-[10px] text-white/30 uppercase">
                            {log.log_type}
                          </span>
                        </div>
                      </td>
                      <td className="p-4 font-bold whitespace-nowrap text-white/90">{log.title}</td>
                      <td className="max-w-md p-4 text-xs break-all text-white/50">{log.detail}</td>
                      <td className="p-4 text-right text-[10px] whitespace-nowrap text-white/20">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="flex h-full flex-col items-center justify-center gap-2 text-white/10">
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
