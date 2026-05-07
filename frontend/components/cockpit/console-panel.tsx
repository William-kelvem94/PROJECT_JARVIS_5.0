'use client';

import { useEffect, useRef } from 'react';

export function ConsolePanel({ logs, emptyText }: { logs: string[]; emptyText?: string }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView?.({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="h-64 overflow-y-auto rounded-xl border border-white/10 bg-black/60 p-4 font-mono text-xs backdrop-blur">
      {logs.length === 0 && (
        <div className="italic text-white/40">
          {emptyText || 'Nenhum log de sistema ainda — o Jarvis está ouvindo.'}
        </div>
      )}
      {logs.map((line, i) => (
        <div key={i} className="text-green-400/80 transition-colors hover:text-green-300">
          <span className="text-cyan-500">{`> `}</span>
          {line}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
