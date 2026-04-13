'use client';

import { AnimatePresence, motion } from 'motion/react';
import { useState } from 'react';
import type { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(SessionView);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.5,
    ease: 'linear' as const,
  },
};

interface ViewControllerProps {
  appConfig: AppConfig;
  onParticipantNameChange?: (name: string) => void;
}

export function ViewController({ appConfig, onParticipantNameChange }: ViewControllerProps) {
  const [isActive, setIsActive] = useState(false);

  const handleStart = async (opts?: any) => {
    // Extract user_name from metadata if provided
    if (opts?.metadata && onParticipantNameChange) {
      try {
        const metadata = JSON.parse(opts.metadata);
        if (metadata.user_name) {
          onParticipantNameChange(metadata.user_name);
        }
      } catch (e) {
        console.error('Erro ao processar metadata:', e);
      }
    }
    setIsActive(true);
  };

  const handleDisconnect = () => {
    setIsActive(false);
  };

  return (
    <AnimatePresence mode="wait">
      {/* Welcome view */}
      {!isActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={handleStart}
        />
      )}
      {/* Session view */}
      {isActive && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
          onManualDisconnect={handleDisconnect}
        />
      )}
    </AnimatePresence>
  );
}
