'use client';

import { Brain, FileText, ListTodo, Sparkles } from 'lucide-react';
import { Panel } from '@/components/cockpit/panel';
import { Meter } from '@/components/cockpit/meter';
import { StateTile } from '@/components/cockpit/state-tile';
import type { MemoryItem, VaultStats } from '@/components/cockpit/types';

export function BrainPanel({
  memories,
  vaultStats,
  personaTraits,
}: {
  memories: MemoryItem[];
  vaultStats: VaultStats | null;
  personaTraits: [string, number][];
}) {
  const memoryPreview = memories.slice(0, 3);
  return (
    <Panel title="Segundo cerebro" icon={Brain}>
      <div className="grid grid-cols-2 gap-2">
        <StateTile
          icon={FileText}
          label="Memórias"
          value={String(memories.length)}
          active={memories.length > 0}
        />
        <StateTile
          icon={ListTodo}
          label="Notas vault"
          value={String(vaultStats?.total_notes ?? vaultStats?.total_memories ?? '-')}
          active={!!vaultStats}
        />
      </div>

      <div className="mt-4 space-y-2">
        {memoryPreview.length > 0 ? (
          memoryPreview.map((memory, index) => (
            <div
              key={memory.id ?? index}
              className="rounded-lg border border-white/10 bg-black/20 p-3"
            >
              <div className="line-clamp-1 text-sm font-medium text-slate-200">
                {memory.title || memory.memory || memory.text || 'Memória registrada'}
              </div>
              <div className="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">
                {memory.content || memory.text || memory.memory || 'Sem conteúdo textual exposto.'}
              </div>
            </div>
          ))
        ) : (
          <div className="rounded-lg border border-white/10 bg-black/20 p-3 text-sm text-slate-500">
            Memórias aparecem aqui quando o backend responder em `/memory`.
          </div>
        )}
      </div>

      {personaTraits.length > 0 && (
        <div className="mt-4">
          <div className="mb-2 text-xs text-slate-500 uppercase">Traços de persona</div>
          <div className="space-y-2">
            {personaTraits.map(([trait, value]) => (
              <Meter
                key={trait}
                label={trait}
                value={Number(value) * 100}
                icon={Sparkles}
                tone="bg-sky-300"
              />
            ))}
          </div>
        </div>
      )}
    </Panel>
  );
}
