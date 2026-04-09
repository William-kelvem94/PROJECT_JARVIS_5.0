'use client';

import React, { useEffect, useRef, useState } from 'react';
import { log } from '@/lib/logger';
import { AnimatePresence, motion } from 'motion/react';
import {
  useSessionContext,
  useSessionMessages,
  useTrackVolume,
  useVoiceAssistant,
  useRemoteParticipants,
} from '@livekit/components-react';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { SessionDiagnostics } from './session-diagnostics';
import { Track, RoomEvent } from 'livekit-client';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { TileLayout } from '@/components/app/tile-layout';
import { cn } from '@/lib/shadcn/utils';
import { Shimmer } from '../ai-elements/shimmer';
import dynamic from 'next/dynamic';
import { EngineeringHUD } from './engineering-hud';
import { ActiveConsole } from './active-console';

const VantaOrb = dynamic(
  () => import('@/components/app/vanta-engine').then(mod => ({ default: mod.VantaOrb })),
  { ssr: false, loading: () => null }
);
const VantaController = dynamic(
  () => import('@/components/app/vanta-engine').then(mod => ({ default: mod.VantaController })),
  { ssr: false, loading: () => null }
);


const MotionBottom = motion.create('div');

const MotionMessage = motion.create(Shimmer);

const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut' as const,
  },
};

const SHIMMER_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      transition: {
        ease: 'easeIn' as const,
        duration: 0.5,
        delay: 0.8,
      },
    },
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeIn' as const,
        duration: 0.5,
        delay: 0,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

interface SessionViewProps {
  appConfig: AppConfig;
  onManualDisconnect?: () => void;
}


export const SessionView = ({
  appConfig,
  onManualDisconnect,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  const session = useSessionContext();
  const { isConnected } = session;
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(false);
  const [isReasoning, setIsReasoning] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const vantaEffectRef = useRef<any>(null);

  // keep track of errors; the hook no longer ends the session automatically
  const { errors, clear: clearErrors } = useAgentErrors();

  // Monitora participantes para detectar Persona (Alice/Járvis)
  const participants = useRemoteParticipants();
  const agentParticipant = participants.find(p => !p.isLocal);
  const agentPersona = agentParticipant?.attributes?.["agent_persona"] || "jarvis";

  // Definição de Cores
  const PERSONA_COLORS = {
    alice: 0xff69b4,
    jarvis: 0x1da3b9,
    reasoning: 0x8a2be2, // BlueViolet
  };
  const currentColor = isReasoning
    ? PERSONA_COLORS.reasoning
    : (PERSONA_COLORS[agentPersona as keyof typeof PERSONA_COLORS] || PERSONA_COLORS.jarvis);


  const controls: AgentControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsScreenShare,
  };

  const [perception, setPerception] = useState<any>(null);

  useEffect(() => {
    if (!session.room) return;

    const handleData = (payload: Uint8Array, participant: any, kind: any, topic?: string) => {
      const decoder = new TextDecoder();
      try {
        const json = JSON.parse(decoder.decode(payload));
        if (topic === 'reasoning' && json.type === 'reasoning_state') {
          setIsReasoning(json.active);
        } else if (topic === 'perception' && json.type === 'perception_update') {
          setPerception(json);
        }
      } catch (e) {
        // console.error(e);
      }
    };

    session.room.on(RoomEvent.DataReceived, handleData);
    return () => {
      session.room?.off(RoomEvent.DataReceived, handleData);
    };
  }, [session.room]);

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;
    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleDisconnect = () => {
    if (onManualDisconnect) onManualDisconnect();
    try {
      if (session.end) session.end();
    } catch (e) {
      console.warn('Erro ao desconectar sessão:', e);
    }
  };

  if (appConfig.enableVanta === false) {
    return (
      <section className="relative flex h-svh w-svw flex-col overflow-hidden bg-black" {...props}>
        {errors.length > 0 && <SessionDiagnostics errors={errors} onClear={clearErrors} />}
        <div className="flex-1 flex flex-col items-center justify-center gap-6 p-10 text-center">
          <div className="size-20 rounded-full border-2 border-dashed border-[#1da3b9]/20 flex items-center justify-center animate-pulse">
            <div className="size-3 rounded-full bg-[#1da3b9]/40" />
          </div>
          <div className="space-y-2">
            <h3 className="text-[#1da3b9] font-mono text-sm uppercase tracking-widest">Sincronização Pendente</h3>
            <p className="text-white/40 text-[10px] max-w-xs mx-auto leading-relaxed">
              O Agente Jarvis ainda não ingressou na sala de comando. Verifique se o worker do backend está ativo.
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-[#1da3b9]/10 border border-[#1da3b9]/40 rounded-full text-[#1da3b9] text-[10px] font-mono hover:bg-[#1da3b9]/20 transition-all hover:scale-105 active:scale-95"
          >
            RECONECTAR JARVIS
          </button>
        </div>
        <div className="relative mx-auto max-w-2xl bg-transparent pb-3 md:pb-12">
          <AgentControlBar
            variant="livekit"
            controls={controls}
            isChatOpen={chatOpen}
            isConnected={true}
            onDisconnect={handleDisconnect}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </section>
    );
  }

  return (
    <section className="relative flex h-svh w-svw flex-col overflow-hidden bg-black" {...props}>
      {/* diagnostic overlay appears on top when there are errors */}
      {errors.length > 0 && <SessionDiagnostics errors={errors} onClear={clearErrors} />}

      {isConnected && (
        <VantaController vantaRef={vantaEffectRef} isConnected={isConnected} />
      )}

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center justify-center overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={session.isConnected ? `vanta-${agentPersona}` : 'vanta-disconnected'}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5, ease: 'easeInOut' }}
              className="p5-canvas-container absolute inset-0 flex items-center justify-center"
            >
              <VantaOrb
                isConnected={session.isConnected}
                color={currentColor}
                vantaRef={vantaEffectRef}
              />
            </motion.div>
          </AnimatePresence>
        </div>

        {isReasoning && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute z-20 top-[65%] flex flex-col items-center gap-4"
          >
            <div className="relative">
              {/* Pulsing Aura */}
              <div className="absolute inset-0 bg-violet-500/20 blur-2xl rounded-full animate-pulse" />

              <div className="relative px-6 py-2 bg-black/40 border border-violet-500/50 rounded-full backdrop-blur-xl shadow-[0_0_20px_rgba(138,43,226,0.2)]">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        animate={{ height: [4, 12, 4] }}
                        transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                        className="w-0.5 bg-violet-400 rounded-full"
                      />
                    ))}
                  </div>
                  <span className="text-[11px] font-bold text-violet-100 tracking-[0.4em] uppercase">
                    Neural Processing
                  </span>
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        animate={{ height: [4, 12, 4] }}
                        transition={{ duration: 1, repeat: Infinity, delay: (2 - i) * 0.2 }}
                        className="w-0.5 bg-violet-400 rounded-full"
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="text-[9px] text-violet-400/60 font-mono tracking-widest uppercase animate-pulse">
              Jarvis thinking deeper...
            </div>
          </motion.div>
        )}

        {/* Perception HUD */}
        {perception && perception.face_present && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute z-30 top-12 left-1/2 -translate-x-1/2 flex gap-4"
          >
            <div className="px-4 py-2 bg-black/60 border border-[#1da3b9]/30 rounded-lg backdrop-blur-sm flex items-center gap-3">
              <div className="size-2 rounded-full bg-green-500 animate-pulse" />
              <div className="flex flex-col">
                <span className="text-[9px] text-[#1da3b9] uppercase font-bold tracking-tighter">Human Detected</span>
                <span className="text-xs text-white/80 font-mono italic">
                  {perception.face_identity || "Unknown Entity"}
                </span>
              </div>
            </div>

            <div className="px-4 py-2 bg-black/60 border border-[#1da3b9]/30 rounded-lg backdrop-blur-sm flex items-center gap-3">
              <span className="text-lg">
                {perception.face_emotion === 'happy' ? '😊' :
                  perception.face_emotion === 'sad' ? '😢' :
                    perception.face_emotion === 'angry' ? '😠' :
                      perception.face_emotion === 'surprise' ? '😲' : '😐'}
              </span>
              <div className="flex flex-col">
                <span className="text-[9px] text-[#1da3b9] uppercase font-bold tracking-tighter">Affective State</span>
                <span className="text-xs text-white/80 font-mono uppercase">{perception.face_emotion || "neutral"}</span>
              </div>
            </div>

            {perception.hand_gesture && (
              <div className="px-4 py-2 bg-black/60 border border-yellow-500/30 rounded-lg backdrop-blur-sm flex items-center gap-3">
                <span className="text-xs text-yellow-500 font-mono uppercase">Gesture: {perception.hand_gesture}</span>
              </div>
            )}
          </motion.div>
        )}

        {isConnected && (
          <div className="relative z-10">
            <TileLayout chatOpen={chatOpen} appConfig={appConfig} />
          </div>
        )}

        {/* Engineering HUD e Active Console aparecem assim que o worker conecta, independente da IA */}
        <EngineeringHUD />
        <ActiveConsole />
      </div>

      <div className="pointer-events-none flex-1" />

      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="relative z-10 mx-auto mb-4 w-full max-w-3xl px-3"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <AnimatePresence>
            {messages.length === 0 && (
              <MotionMessage
                key="pre-connect-message"
                duration={2}
                aria-hidden={messages.length > 0}
                {...SHIMMER_MOTION_PROPS}
                className="pointer-events-none mx-auto block w-full max-w-2xl pb-8 text-center text-sm font-semibold"
              >
                O Jarvis está ouvindo, pode falar...
              </MotionMessage>
            )}
          </AnimatePresence>
        )}

        <div className="relative mx-auto max-w-2xl bg-transparent pb-3 md:pb-12">
          <AgentControlBar
            variant="livekit"
            controls={controls}
            isChatOpen={chatOpen}
            isConnected={true}
            onDisconnect={handleDisconnect}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </MotionBottom>
    </section>
  );
};
