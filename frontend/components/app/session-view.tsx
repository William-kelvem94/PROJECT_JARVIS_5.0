'use client';

import React, { useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useJarvisVoice } from '@/hooks/useJarvisVoice';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { SessionDiagnostics } from './session-diagnostics';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { TileLayout } from '@/components/app/tile-layout';
import { cn } from '@/lib/shadcn/utils';
import { Shimmer } from '../ai-elements/shimmer';
import dynamic from 'next/dynamic';
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
    visible: { opacity: 1, translateY: '0%' },
    hidden: { opacity: 0, translateY: '100%' },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: { duration: 0.3, delay: 0.5, ease: 'easeOut' as const },
};

const SHIMMER_MOTION_PROPS = {
  variants: {
    visible: { opacity: 1, transition: { ease: 'easeIn' as const, duration: 0.5, delay: 0.8 } },
    hidden: { opacity: 0, transition: { ease: 'easeIn' as const, duration: 0.5, delay: 0 } },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface SessionViewProps {
  appConfig: AppConfig;
  onManualDisconnect?: () => void;
}

export const SessionView = ({
  appConfig,
  onManualDisconnect,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  // Substitui LiveKit Hook pelo nosso Native WebSocket Hook
  const { isConnected, isSpeaking, messages, connect, disconnect } = useJarvisVoice();
  const [chatOpen, setChatOpen] = useState(false);
  const vantaEffectRef = useRef<any>(null);

  const { errors, clear: clearErrors } = useAgentErrors();

  const PERSONA_COLORS = { jarvis: 0x1da3b9, reasoning: 0x8a2be2 };
  const currentColor = isSpeaking ? PERSONA_COLORS.reasoning : PERSONA_COLORS.jarvis;

  const controls: AgentControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: false, // Desativado via Local Voice
    screenShare: false,
  };

  const handleDisconnect = () => {
    if (onManualDisconnect) onManualDisconnect();
    disconnect();
  };

  // Se nao tiver conectado, conecta automaticamente ao montar
  React.useEffect(() => {
    if (!isConnected) {
       connect();
    }
  }, [isConnected, connect]);

  return (
    <section className="relative flex h-svh w-svw flex-col overflow-hidden bg-black" {...props}>
      {errors.length > 0 && <SessionDiagnostics errors={errors} onClear={clearErrors} />}

      {isConnected && (
        <VantaController vantaRef={vantaEffectRef} isConnected={isConnected} />
      )}

      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <div className="absolute inset-0 flex items-center justify-center">
          <VantaOrb
            isConnected={isConnected}
            color={currentColor}
            vantaRef={vantaEffectRef}
          />
        </div>

        {isSpeaking && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute z-20 top-[65%] flex flex-col items-center gap-4"
          >
            <div className="relative px-6 py-2 bg-black/40 border border-violet-500/50 rounded-full backdrop-blur-xl">
              <span className="text-[11px] font-bold text-violet-100 uppercase">Jarvis Falando...</span>
            </div>
          </motion.div>
        )}

        {isConnected && (
          <div className="relative z-10 pointer-events-auto">
            {/* TileLayout precisa ser refatorado futuramente para nao usar LiveKit se tiver chats nativos */}
          </div>
        )}

        <ActiveConsole />
      </div>

      <div className="pointer-events-none flex-1" />

      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="pointer-events-auto relative z-10 mx-auto mb-4 w-full max-w-3xl px-3"
      >
        <AnimatePresence>
          {messages.length === 0 && (
            <MotionMessage
              key="pre-connect-message"
              duration={2}
              {...SHIMMER_MOTION_PROPS}
              className="pointer-events-none mx-auto block w-full max-w-2xl pb-8 text-center text-sm font-semibold"
            >
              Jarvis Nativo está online e ouvindo...
            </MotionMessage>
          )}
        </AnimatePresence>

        <div className="relative mx-auto max-w-2xl bg-transparent pb-3 md:pb-12">
          <AgentControlBar
            variant="livekit"
            controls={controls}
            isChatOpen={chatOpen}
            isConnected={isConnected}
            onDisconnect={handleDisconnect}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </MotionBottom>
    </section>
  );
};
