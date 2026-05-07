'use client';

import { Eye, ImageIcon, ListTodo } from 'lucide-react';

interface StatsStripProps {
  objects: string[];
  todos: number;
  screenshot?: string;
}

export function StatsStrip({ objects, todos, screenshot }: StatsStripProps) {
  const objectsLabel = objects.length > 0 ? objects.slice(0, 3).join(', ') : 'Nenhum objeto';

  return (
    <div className="flex flex-wrap justify-center gap-3">
      {/* Objetos detectados */}
      <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 backdrop-blur-sm">
        <Eye className="h-4 w-4 shrink-0 text-cyan-300" />
        <span className="max-w-48 truncate text-sm text-white/70">{objectsLabel}</span>
        {objects.length > 3 && <span className="text-xs text-white/40">+{objects.length - 3}</span>}
      </div>

      {/* Tarefas Obsidian */}
      <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 backdrop-blur-sm">
        <ListTodo className="h-4 w-4 shrink-0 text-yellow-300" />
        <span className="text-sm text-white/70">
          {todos} tarefa{todos !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Screenshot ativo */}
      {screenshot && (
        <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 backdrop-blur-sm">
          <ImageIcon className="h-4 w-4 shrink-0 text-purple-300" />
          <span className="text-sm text-white/70">Visão ativa</span>
        </div>
      )}
    </div>
  );
}
