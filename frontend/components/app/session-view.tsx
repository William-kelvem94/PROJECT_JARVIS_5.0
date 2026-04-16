'use client';

import React, { useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useJarvis } from '@/context/JarvisContext';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { SessionDiagnostics } from './session-diagnostics';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { cn } from '@/lib/shadcn/utils';
import dynamic from 'next/dynamic';
import { ActiveConsole } from './active-console';
import { EngineeringHUD } from './engineering-hud';

const VantaOrb = dynamic(
  () => import('@/components/app/vanta-engine').then((mod) => mod.VantaOrb as any),
  { ssr: false, loading: () => null }
);
const VantaController = dynamic(
  () => import('@/components/app/vanta-engine').then((mod) => mod.VantaController as any),
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
  const { 
    isConnected, 
    isSpeaking, 
    messages, 
    connect, 
    disconnect, 
    isCameraEnabled,
    localStream
  } = useJarvis();
  
  const [chatOpen, setChatOpen] = useState(false);
  const vantaEffectRef = useRef<any>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const { errors, clear: clearErrors } = useAgentErrors();

  const handleDisconnect = () => {
    if (onManualDisconnect) onManualDisconnect();
    disconnect();
  };

  // Cores dinâmicas baseadas no estado
  const currentGlow = isSpeaking ? "rgba(112, 0, 255, 0.4)" : "rgba(0, 242, 255, 0.2)";

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
      <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-jarvis-cyan/5 to-transparent pointer-events-none" />

      {errors.length > 0 && <SessionDiagnostics errors={errors} onClear={clearErrors} />}

      {isConnected && (
        <VantaController 
            // @ts-ignore - Componente dinâmico
            vantaRef={vantaEffectRef} 
            isConnected={isConnected} 
        />
      )}

      {/* ── LADO DIREITO: Telemetria ────────────────────────────────────────── */}
      <EngineeringHUD />

      {/* ── LADO ESQUERDO: Console de Atividade ─────────────────────────────── */}
      <div className="absolute left-6 top-6 z-30 flex flex-col gap-4 max-w-sm pointer-events-none">
        <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-2 mb-2"
        >
            <div className="size-1.5 bg-jarvis-cyan rounded-full animate-pulse shadow-[0_0_8px_#00f2ff]" />
            <span className="text-[10px] font-bold uppercase tracking-[0.4em] text-white/40">Real-time Stream</span>
        </motion.div>
        <ActiveConsole externalLogs={messages} />
      </div>

      {/* ── CENTRO: O Núcleo (Orb) ─────────────────────────────────────────── */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
         {/* Circulos decorativos rotativos (Aesthetics) */}
         <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute size-[500px] border border-white/5 rounded-full"
         />
         <motion.div 
          animate={{ rotate: -360 }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
          className="absolute size-[700px] border border-white/[0.02] rounded-full"
         />

        <div className="relative flex flex-col items-center">
            <VantaOrb
                // @ts-ignore - Componente dinâmico
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
                        className="mt-8 px-8 py-3 cyber-glass rounded-full text-jarvis-cyan text-[10px] font-bold uppercase tracking-[0.5em] animate-pulse"
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
            className="absolute top-6 right-72 z-30 w-56 h-36 cyber-glass rounded-xl overflow-hidden border-jarvis-cyan/20"
          >
            <video 
              ref={videoRef} 
              autoPlay 
              muted 
              playsInline 
              className="w-full h-full object-cover grayscale brightness-125 opacity-70"
            />
            <div className="absolute inset-0 bg-blue-500/10 pointer-events-none" />
            <div className="absolute top-2 left-2 flex items-center gap-1.5">
                <div className="size-1 bg-red-500 rounded-full animate-pulse" />
                <span className="text-[8px] font-mono text-white/50 tracking-tighter">CMD_VISION_ALPHA</span>
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
        <div className="cyber-glass p-2 rounded-2xl border-white/5">
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

