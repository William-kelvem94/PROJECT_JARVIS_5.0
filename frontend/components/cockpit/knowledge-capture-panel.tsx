'use client';

import { Database, FileText, Send } from 'lucide-react';
import { cn } from '@/lib/shadcn/utils';
import { Panel } from '@/components/cockpit/panel';
import type { SaveStatus } from '@/components/cockpit/types';

export function KnowledgeCapturePanel({
  memoryDraft,
  noteDraft,
  saveStatus,
  isSaving,
  onMemoryDraftChange,
  onNoteDraftChange,
  onSaveMemory,
  onSaveNote,
}: {
  memoryDraft: {
    title: string;
    content: string;
    project: string;
    keywords: string;
    importance: string;
  };
  noteDraft: { title: string; body: string };
  saveStatus: SaveStatus;
  isSaving: boolean;
  onMemoryDraftChange: (value: {
    title: string;
    content: string;
    project: string;
    keywords: string;
    importance: string;
  }) => void;
  onNoteDraftChange: (value: { title: string; body: string }) => void;
  onSaveMemory: () => Promise<void>;
  onSaveNote: () => Promise<void>;
}) {
  return (
    <Panel title="Captura de conhecimento" icon={FileText}>
      <div className="space-y-4">
        <div className="rounded-lg border border-white/10 bg-black/20 p-3">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-white">Memória episódica</div>
              <div className="text-xs text-slate-500">POST /vault-memory</div>
            </div>
            <Database className="size-4 text-cyan-200" />
          </div>
          <div className="space-y-2">
            <input
              value={memoryDraft.title}
              onChange={(event) =>
                onMemoryDraftChange({ ...memoryDraft, title: event.target.value })
              }
              placeholder="Titulo da memoria"
              className="h-9 w-full rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <textarea
              value={memoryDraft.content}
              onChange={(event) =>
                onMemoryDraftChange({ ...memoryDraft, content: event.target.value })
              }
              rows={4}
              placeholder="O que o Jarvis deve lembrar?"
              className="w-full resize-none rounded-lg border border-white/10 bg-white/4 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <div className="grid gap-2 sm:grid-cols-2">
              <input
                value={memoryDraft.project}
                onChange={(event) =>
                  onMemoryDraftChange({ ...memoryDraft, project: event.target.value })
                }
                placeholder="Projeto"
                className="h-9 rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
              />
              <select
                value={memoryDraft.importance}
                onChange={(event) =>
                  onMemoryDraftChange({ ...memoryDraft, importance: event.target.value })
                }
                className="h-9 rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none focus:border-cyan-200/40"
              >
                <option value="BAIXA">Baixa</option>
                <option value="MEDIA">Media</option>
                <option value="ALTA">Alta</option>
                <option value="CRITICA">Critica</option>
              </select>
            </div>
            <input
              value={memoryDraft.keywords}
              onChange={(event) =>
                onMemoryDraftChange({ ...memoryDraft, keywords: event.target.value })
              }
              placeholder="keywords, separadas, por virgula"
              className="h-9 w-full rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <button
              onClick={onSaveMemory}
              disabled={isSaving}
              className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-lg bg-cyan-200 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:bg-slate-700 disabled:text-slate-500"
            >
              <Send className="size-4" />
              Salvar memoria
            </button>
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-black/20 p-3">
          <div className="mb-3 text-sm font-semibold text-white">Nota rápida</div>
          <div className="space-y-2">
            <input
              value={noteDraft.title}
              onChange={(event) => onNoteDraftChange({ ...noteDraft, title: event.target.value })}
              placeholder="Titulo da nota"
              className="h-9 w-full rounded-lg border border-white/10 bg-white/4 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <textarea
              value={noteDraft.body}
              onChange={(event) => onNoteDraftChange({ ...noteDraft, body: event.target.value })}
              rows={3}
              placeholder="Conteudo para /notes"
              className="w-full resize-none rounded-lg border border-white/10 bg-white/4 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
            />
            <button
              onClick={onSaveNote}
              disabled={isSaving}
              className="inline-flex h-9 w-full items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/6 text-sm font-semibold text-slate-100 transition hover:border-emerald-200/30 hover:bg-emerald-200/10 disabled:text-slate-500"
            >
              <FileText className="size-4" />
              Criar nota
            </button>
          </div>
        </div>

        {saveStatus.type !== 'idle' && (
          <div
            className={cn(
              'rounded-lg border px-3 py-2 text-sm',
              saveStatus.type === 'success'
                ? 'border-emerald-300/20 bg-emerald-300/10 text-emerald-100'
                : 'border-rose-300/20 bg-rose-300/10 text-rose-100'
            )}
          >
            {saveStatus.message}
          </div>
        )}
      </div>
    </Panel>
  );
}
