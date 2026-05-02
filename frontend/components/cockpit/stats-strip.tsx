'use client';
<<<<<<< HEAD

import { Eye, ListTodo, ImageIcon } from 'lucide-react';
=======
import { Eye, ListTodo } from 'lucide-react';
>>>>>>> main

interface StatsStripProps {
  objects: string[];
  todos: number;
<<<<<<< HEAD
  screenshot?: string;
}

export function StatsStrip({ objects, todos, screenshot }: StatsStripProps) {
  const objectsLabel = objects.length > 0 ? objects.slice(0, 3).join(', ') : 'Nenhum objeto';

  return (
    <div className="flex flex-wrap gap-3 justify-center">
      {/* Objetos detectados */}
      <div className="flex items-center gap-2 bg-white/5 backdrop-blur-sm px-3 py-2 rounded-lg border border-white/10">
        <Eye className="w-4 h-4 text-cyan-300 shrink-0" />
        <span className="text-sm text-white/70 max-w-48 truncate">{objectsLabel}</span>
        {objects.length > 3 && (
          <span className="text-xs text-white/40">+{objects.length - 3}</span>
        )}
      </div>

      {/* Tarefas Obsidian */}
      <div className="flex items-center gap-2 bg-white/5 backdrop-blur-sm px-3 py-2 rounded-lg border border-white/10">
        <ListTodo className="w-4 h-4 text-yellow-300 shrink-0" />
        <span className="text-sm text-white/70">{todos} tarefa{todos !== 1 ? 's' : ''}</span>
      </div>

      {/* Screenshot ativo */}
      {screenshot && (
        <div className="flex items-center gap-2 bg-white/5 backdrop-blur-sm px-3 py-2 rounded-lg border border-white/10">
          <ImageIcon className="w-4 h-4 text-purple-300 shrink-0" />
          <span className="text-sm text-white/70">Visão ativa</span>
        </div>
      )}
=======
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
>>>>>>> main
    </div>
  );
}
