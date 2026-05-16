'use client';

import { Activity, Database, MessageSquareText, Mic, Power, Send, ShieldCheck, Sparkles } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';
import { Panel } from '@/components/cockpit/panel';
import { FocusSignal } from '@/components/cockpit/focus-signal';

export function CommandCenter({
  status,
  connected,
  error,
  draft,
  setDraft,
  onSend,
  onConnect,
  onDisconnect,
  messages,
}: {
  status: string;
  connected: boolean;
  error: string | null;
  draft: string;
  setDraft: (value: string) => void;
  onSend: () => Promise<void>;
  onConnect: () => Promise<void>;
  onDisconnect: () => void;
  messages: { role: 'user' | 'assistant'; content: string; timestamp: string }[];
}) {
  return (
    <Panel
      title="Centro de comando"
      icon={MessageSquareText}
      className="min-h-[420px]"
      action={
        <button
          onClick={connected ? onDisconnect : onConnect}
          className={cn(
            'inline-flex h-9 items-center gap-2 rounded-lg px-3 text-xs font-semibold transition',
            connected
              ? 'bg-rose-400/12 text-rose-100 hover:bg-rose-400/20'
              : 'bg-emerald-300/12 text-emerald-100 hover:bg-emerald-300/20'
          )}
        >
          <Power className="size-4" />
          {connected ? 'Desconectar' : 'Ativar voz'}
        </button>
      }
    >
      <div className="grid min-h-[340px] gap-4 lg:grid-cols-[1fr_260px]">
        <div className="flex min-h-0 flex-col rounded-lg border border-white/10 bg-[#080b11]/80">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <div>
              <div className="text-sm font-medium text-white">Conversas e comandos</div>
              <div className="text-xs text-slate-500">{error || status}</div>
            </div>
            <Mic className={cn('size-5', connected ? 'text-emerald-200' : 'text-slate-600')} />
          </div>

          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
            <AnimatePresence initial={false}>
              {messages.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="grid h-full min-h-40 place-items-center text-center"
                >
                  <div>
                    <Sparkles className="mx-auto mb-3 size-8 text-cyan-200/70" />
                    <p className="text-sm font-medium text-slate-200">Pronto para operar.</p>
                    <p className="mt-1 max-w-sm text-sm text-slate-500">
                      Digite um comando ou ative a voz para conversar com o Jarvis.
                    </p>
                  </div>
                </motion.div>
              ) : (
                messages.slice(-8).map((message, index) => (
                  <motion.div
                    key={`${message.timestamp}-${index}`}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn(
                      'max-w-[88%] rounded-lg px-3 py-2 text-sm',
                      message.role === 'user'
                        ? 'ml-auto bg-cyan-300/[0.12] text-cyan-50'
                        : 'bg-white/8 text-slate-100'
                    )}
                  >
                    <div className="mb-1 text-[10px] text-slate-500 uppercase">
                      {message.role === 'user' ? 'Will' : 'Jarvis'} · {message.timestamp}
                    </div>
                    <div className="leading-relaxed">{message.content}</div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>

          <div className="border-t border-white/10 p-3">
            <div className="flex gap-2">
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    onSend();
                  }
                }}
                rows={2}
                placeholder="Ex: resumir logs de hoje, salvar memoria, analisar capturas..."
                className="min-h-12 flex-1 resize-none rounded-lg border border-white/10 bg-white/4 px-3 py-2 text-sm text-white transition outline-none placeholder:text-slate-600 focus:border-cyan-200/40"
              />
              <button
                onClick={onSend}
                className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-cyan-200 text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-500"
                disabled={!draft.trim()}
                title="Enviar comando"
              >
                <Send className="size-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="grid content-start gap-3">
          <FocusSignal
            label="Escuta"
            value={connected ? 'ativa' : 'manual'}
            icon={Mic}
            active={connected}
          />
          <FocusSignal
            label="Pipeline"
            value={error ? 'erro' : 'pronto'}
            icon={Activity}
            active={!error}
          />
          <FocusSignal label="Memória" value="consulta HTTP" icon={Database} active />
          <FocusSignal label="Segurança" value="Sentinel" icon={ShieldCheck} active />
        </div>
      </div>
    </Panel>
  );
}
