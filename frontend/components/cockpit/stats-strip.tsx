'use client';

import { Eye, ListTodo } from 'lucide-react';

interface StatsStripProps {
  objects: string[];
  todos: number;
}

export function StatsStrip({ objects, todos }: StatsStripProps) {
  return (
    <div className="flex flex-wrap items-center gap-6 px-2">
      {/* Objects detected */}
      <div className="flex items-center gap-2 text-sm text-white/70">
        <Eye className="w-4 h-4 text-cyan-400" />
        <span className="font-medium">{objects.length}</span>
        <span className="text-white/40">objeto{objects.length !== 1 ? 's' : ''} detectado{objects.length !== 1 ? 's' : ''}</span>
        {objects.length > 0 && (
          <span className="text-white/30 text-xs truncate max-w-50">
            {objects.slice(0, 3).join(', ')}
          </span>
        )}
      </div>

      {/* Todos */}
      <div className="flex items-center gap-2 text-sm text-white/70">
        <ListTodo className="w-4 h-4 text-purple-400" />
        <span className="font-medium">{todos}</span>
        <span className="text-white/40">tarefa{todos !== 1 ? 's' : ''} ativa{todos !== 1 ? 's' : ''}</span>
      </div>
    </div>
  );
}
