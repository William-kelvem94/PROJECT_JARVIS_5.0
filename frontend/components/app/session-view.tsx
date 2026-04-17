'use client';

import React, { useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { AnimatePresence, motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { useJarvis } from '@/context/JarvisContext';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { cn } from '@/lib/shadcn/utils';
import { ActiveConsole } from './active-console';
import { EngineeringHUD } from './engineering-hud';
import { SessionDiagnostics } from './session-diagnostics';

const VantaOrb = dynamic(
  async () => {
    const mod = await import('@/components/app/vanta-engine');
    return mod.VantaOrb;
  },
  { ssr: false, loading: () => null }
);
const VantaController = dynamic(
  async () => {
    const mod = await import('@/components/app/vanta-engine');
    return mod.VantaController;
  },
  { ssr: false, loading: () => null }
);

interface SessionViewProps {
  appConfig: AppConfig;
  onManualDisconnect?: () => void;
}

export const SessionView = ({
  appConfig,
  onManualDisconnect,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  const { isConnected, isSpeaking, messages, connect, disconnect, isCameraEnabled, localStream } =
    useJarvis();

  const [chatOpen, setChatOpen] = useState(false);
  const vantaEffectRef = useRef<{
    setVolume: (volume: number) => void;
    setColor: (color: number) => void;
  } | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const { errors, clear: clearErrors } = useAgentErrors();

  const handleDisconnect = () => {
    if (onManualDisconnect) onManualDisconnect();
    disconnect();
  };

  // Cores dinâmicas baseadas no estado
  const currentGlow = isSpeaking ? 'rgba(112, 0, 255, 0.4)' : 'rgba(0, 242, 255, 0.2)';

  React.useEffect(() => {
    if (!isConnected) connect();
  }, [isConnected, connect]);

  React.useEffect(() => {
    if (videoRef.current && isCameraEnabled && localStream) {
      videoRef.current.srcObject = localStream;
    }
  }, [isCameraEnabled, localStream]);

  return (
    <section className="relative flex h-svh w-svw flex-col overflow-hidden bg-[#020205]" {...props}>
      {/* Camada de Background Ambient Gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(10,10,25,1)_0%,rgba(2,2,5,1)_100%)]" />

      {/* Sombras e Reflexos de Cockpit */}
      <div className="from-jarvis-cyan/5 pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b to-transparent" />

      {errors.length > 0 && <SessionDiagnostics errors={errors} onClear={clearErrors} />}

      {isConnected && (
        <VantaController
          vantaRef={vantaEffectRef}
          isConnected={isConnected}
        />
      )}

      {/* ── LADO DIREITO: Telemetria ────────────────────────────────────────── */}
      <EngineeringHUD />

      {/* ── LADO ESQUERDO: Console de Atividade ─────────────────────────────── */}
      <div className="pointer-events-none absolute top-6 left-6 z-30 flex max-w-sm flex-col gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-2 flex items-center gap-2"
        >
          <div className="bg-jarvis-cyan size-1.5 animate-pulse rounded-full shadow-[0_0_8px_#00f2ff]" />
          <span className="text-[10px] font-bold tracking-[0.4em] text-white/40 uppercase">
            Real-time Stream
          </span>
        </motion.div>
        <ActiveConsole externalLogs={messages} />
      </div>

      {/* ── CENTRO: O Núcleo (Orb) ─────────────────────────────────────────── */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        {/* Circulos decorativos rotativos (Aesthetics) */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          className="absolute size-[500px] rounded-full border border-white/5"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
          className="absolute size-[700px] rounded-full border border-white/[0.02]"
        />

        <div className="relative flex flex-col items-center">
          <VantaOrb
            isConnected={isConnected}
            color={isSpeaking ? 0x7000ff : 0x1da3b9}
            vantaRef={vantaEffectRef}
          />

          <AnimatePresence>
            {isSpeaking && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="cyber-glass text-jarvis-cyan mt-8 animate-pulse rounded-full px-8 py-3 text-[10px] font-bold tracking-[0.5em] uppercase"
              >
                Transmitting...
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* ── CANTO SUPERIOR DIREITO: Vision Preview ──────────────────────────── */}
      <AnimatePresence>
        {isCameraEnabled && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="cyber-glass border-jarvis-cyan/20 absolute top-6 right-72 z-30 h-36 w-56 overflow-hidden rounded-xl"
          >
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="h-full w-full object-cover opacity-70 brightness-125 grayscale"
            />
            <div className="pointer-events-none absolute inset-0 bg-blue-500/10" />
            <div className="absolute top-2 left-2 flex items-center gap-1.5">
              <div className="size-1 animate-pulse rounded-full bg-red-500" />
              <span className="font-mono text-[8px] tracking-tighter text-white/50">
                CMD_VISION_ALPHA
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex-1" />

      {/* ── RODAPÉ: Controls ────────────────────────────────────────────────── */}
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1 }}
        className="relative z-40 mx-auto mb-8 w-full max-w-2xl px-4"
      >
        <div className="cyber-glass rounded-2xl border-white/5 p-2">
          <AgentControlBar
            controls={{
              leave: true,
              microphone: true,
              chat: appConfig.supportsChatInput,
              camera: true,
              screenShare: true,
            }}
            isChatOpen={chatOpen}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </motion.div>
    </section>
  );
};
