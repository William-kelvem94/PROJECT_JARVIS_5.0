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
    <div className="w-full rounded-xl border border-white/10 bg-black/60 backdrop-blur-sm p-4 h-52 overflow-y-auto font-mono text-xs text-green-400 leading-relaxed">
      {logs.length === 0 ? (
        <p className="text-white/30 italic">
          Nenhum log de sistema ainda — o Jarvis está ouvindo.
        </p>
      ) : (
        logs.map((line, i) => (
          <div key={i} className="whitespace-pre-wrap break-all">
            {line}
          </div>
        ))
      )}
      <div ref={bottomRef} />
    </div>
  );
}
