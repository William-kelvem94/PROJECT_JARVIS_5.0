'use client';
<<<<<<< HEAD

import { useEffect, useRef } from 'react';

interface ConsolePanelProps {
  logs: string[];
}

export function ConsolePanel({ logs }: ConsolePanelProps) {
=======
import { useEffect, useRef } from 'react';

export function ConsolePanel({ logs, emptyText }: { logs: string[]; emptyText?: string }) {
>>>>>>> main
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
<<<<<<< HEAD
    <div className="bg-black/60 backdrop-blur-md rounded-xl border border-white/10 p-4 h-64 overflow-y-auto font-mono text-xs">
      {logs.length === 0 ? (
        <p className="text-white/40 italic">Nenhum log de sistema ainda — o Jarvis está ouvindo.</p>
      ) : (
        logs.map((line, i) => (
          <div
            key={i}
            className="text-green-400/80 hover:text-green-300 transition-colors leading-relaxed"
          >
            <span className="text-cyan-500 select-none">&gt; </span>
            {line}
          </div>
        ))
      )}
=======
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
>>>>>>> main
      <div ref={bottomRef} />
    </div>
  );
}
