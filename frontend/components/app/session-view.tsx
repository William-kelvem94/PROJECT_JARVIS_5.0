'use client';

import React, { useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { AnimatePresence, motion } from 'motion/react';
import { Crosshair, Eye, Broadcast, Aperture } from '@phosphor-icons/react';
import type { AppConfig } from '@/app-config';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';
import { useJarvis } from '@/context/JarvisContext';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { ActiveConsole } from './active-console';
import { ChatTranscript } from './chat-transcript';
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

  React.useEffect(() => {
    connect();
  }, []);

  React.useEffect(() => {
    if (videoRef.current && isCameraEnabled && localStream) {
      videoRef.current.srcObject = localStream;
    }
  }, [isCameraEnabled, localStream]);

  return (
    <section className="bg-jarvis-bg relative flex h-svh w-svw flex-col overflow-hidden" {...props}>
      {/* Background Layers */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(10,10,35,1)_0%,rgba(2,2,8,1)_100%)]" />
      
      {/* HUD Grid Overlay */}
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] opacity-20" />

      {/* Decorative Cockpit Borders */}
      <div className="pointer-events-none absolute inset-0 z-10 border-[30px] border-black/20" style={{ clipPath: 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 5% 5%, 5% 95%, 95% 95%, 95% 5%, 5% 5%)' }} />
      
      {/* UI Elements */}
      {errors.length > 0 && <SessionDiagnostics errors={errors} onClear={clearErrors} />}
      {isConnected && <VantaController vantaRef={vantaEffectRef} isConnected={isConnected} />}

      {/* ── LADO DIREITO: Telemetria ────────────────────────────────────────── */}
      <EngineeringHUD />

      {/* ── LADO ESQUERDO: Console de Atividade ─────────────────────────────── */}
      <div className="pointer-events-none absolute top-8 left-8 z-30 flex max-w-sm flex-col gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <div className="relative">
            <Broadcast className="text-jarvis-cyan size-5" />
            <motion.div 
              animate={{ scale: [1, 2], opacity: [1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="absolute inset-0 rounded-full bg-jarvis-cyan/40"
            />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] font-black tracking-[0.4em] text-white/90 uppercase font-mono">
              Neural Stream
            </span>
            <span className="text-[7px] font-bold tracking-[0.2em] text-jarvis-cyan/40 uppercase font-mono">
              Buffer Status: Optimal
            </span>
          </div>
        </motion.div>
        <ActiveConsole externalLogs={messages} />
      </div>

      {/* ── TRANSCRIÇÃO DE CHAT ──────────────────────────────── */}
      <ChatTranscript hidden={!chatOpen} messages={messages} className="pointer-events-none z-20" />

      {/* ── CENTRO: O Núcleo (Orb) ─────────────────────────────────────────── */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        {/* Animated Rings */}
        <div className="relative flex items-center justify-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
            className="absolute size-[550px] rounded-full border border-jarvis-cyan/5 border-dashed"
          />
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
            className="absolute size-[700px] rounded-full border border-white/2"
          />
          
          {/* Target Reticle */}
          <motion.div 
            animate={{ opacity: [0.2, 0.5, 0.2] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute flex items-center justify-center"
          >
            <Crosshair className="text-jarvis-cyan/20 size-96 font-thin" />
          </motion.div>

          <div className="relative flex flex-col items-center">
            <VantaOrb
              isConnected={isConnected}
              color={isSpeaking ? 0x7000ff : 0x1da3b9}
              vantaRef={vantaEffectRef}
            />

            <AnimatePresence>
              {isSpeaking && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, y: 10 }}
                  className="cyber-glass mt-12 flex items-center gap-3 rounded-full border-jarvis-violet/30 px-10 py-4 ring-1 ring-jarvis-violet/20"
                >
                  <motion.div 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                    className="size-2 rounded-full bg-jarvis-violet shadow-[0_0_12px_#7000ff]"
                  />
                  <span className="text-jarvis-violet font-mono text-[11px] font-black tracking-[0.6em] uppercase drop-shadow-[0_0_8px_#7000ff]">
                    Transmitting
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* ── CANTO SUPERIOR DIREITO: Vision Preview ──────────────────────────── */}
      <AnimatePresence>
        {isCameraEnabled && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, x: 50 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.9, x: 50 }}
            className="cyber-glass border-jarvis-cyan/30 absolute top-8 right-80 z-30 h-44 w-72 overflow-hidden rounded-2xl shadow-[0_0_30px_rgba(0,242,255,0.1)]"
          >
            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="h-full w-full object-cover opacity-80 brightness-110 grayscale contrast-125"
            />
            {/* Scanline and Tint on video */}
            <div className="pointer-events-none absolute inset-0 bg-jarvis-cyan/10" />
            
            {/* Vision HUD Elements */}
            <div className="absolute inset-4 flex flex-col justify-between pointer-events-none">
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2 rounded-md bg-black/60 px-2 py-1 backdrop-blur-md">
                  <Aperture className="size-3 text-red-500 animate-spin-slow" />
                  <span className="font-mono text-[8px] font-bold text-red-500/80 tracking-widest">REC_MODE</span>
                </div>
                <Eye className="size-4 text-jarvis-cyan/50" />
              </div>
              
              <div className="flex justify-between items-end">
                <div className="flex flex-col gap-0.5">
                  <span className="font-mono text-[7px] text-white/40">FRM_RT: 60.00</span>
                  <span className="font-mono text-[7px] text-white/40">RES: 1080P_RAW</span>
                </div>
                <div className="h-6 w-6 border-b-2 border-r-2 border-jarvis-cyan/40" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex-1" />

      {/* ── RODAPÉ: Controls ────────────────────────────────────────────────── */}
      <motion.div
        initial={{ y: 80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 1, type: "spring", damping: 20 }}
        className="relative z-40 mx-auto mb-10 w-full max-w-3xl px-6"
      >
        <div className="cyber-glass rounded-3xl border-white/10 bg-black/60 p-3 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
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
            onLeave={handleDisconnect}
          />
        </div>
      </motion.div>

      {/* Decorative Side Elements (Branding) */}
      <div className="pointer-events-none absolute bottom-8 left-8 flex flex-col gap-1 z-30">
        <span className="font-mono text-[8px] font-bold text-white/10 tracking-[0.5em] uppercase">
          Neural Interface System
        </span>
        <div className="h-px w-24 bg-white/5" />
      </div>
    </section>
  );
};
