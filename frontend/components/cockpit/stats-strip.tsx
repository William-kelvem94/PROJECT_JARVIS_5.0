'use client';
import { Eye, ListTodo } from 'lucide-react';

interface StatsStripProps {
  objects: string[];
  todos: number;
  noObjectsText?: string;
  tasksText?: (count: number) => string;
}

export function StatsStrip({ objects, todos, noObjectsText, tasksText }: StatsStripProps) {
  const noObjects = noObjectsText || 'Nenhum objeto';
  const tasks = tasksText ? tasksText(todos) : `${todos} tarefa${todos !== 1 ? 's' : ''}`;

  return (
    <div className="flex flex-wrap justify-center gap-4">
      <div className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2">
        <Eye className="h-4 w-4 text-cyan-300" />
        <span className="text-sm text-white/70">
          {objects.length > 0 ? objects.slice(0, 3).join(', ') : noObjects}
        </span>
      </div>
      <div className="flex items-center gap-2 rounded-lg bg-white/5 px-3 py-2">
        <ListTodo className="h-4 w-4 text-yellow-300" />
        <span className="text-sm text-white/70">{tasks}</span>
      </div>
    </div>
  );
}
