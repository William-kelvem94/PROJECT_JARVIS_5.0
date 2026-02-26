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
import { Track } from 'livekit-client';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { TileLayout } from '@/components/app/tile-layout';
import { cn } from '@/lib/shadcn/utils';
import { Shimmer } from '../ai-elements/shimmer';
import dynamic from 'next/dynamic';

const VantaOrb = dynamic(() => import('@/components/app/vanta-engine').then(mod => ({ default: mod.VantaOrb })), { ssr: false });
const VantaController = dynamic(() => import('@/components/app/vanta-engine').then(mod => ({ default: mod.VantaController })), { ssr: false });


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
  };
  const currentColor = PERSONA_COLORS[agentPersona as keyof typeof PERSONA_COLORS] || PERSONA_COLORS.jarvis;


  const controls: AgentControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsScreenShare,
  };

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
        <div className="flex-1 flex items-center justify-center">
          <div className="text-zinc-800 text-xs italic">Modo Economia de Energia Ativo</div>
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

        {isConnected && (
          <div className="relative z-10">
            <TileLayout chatOpen={chatOpen} />
          </div>
        )}
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
