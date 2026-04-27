'use client';

import { useEffect, useRef } from 'react';

interface ConsolePanelProps {
  logs: string[];
}

export function ConsolePanel({ logs }: ConsolePanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
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
      <div ref={bottomRef} />
    </div>
  );
}
