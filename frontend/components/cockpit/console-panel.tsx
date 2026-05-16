'use client';

import { Terminal } from 'lucide-react';
import { Panel } from '@/components/cockpit/panel';

export function ConsolePanel({ logs }: { logs: string[] }) {
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
