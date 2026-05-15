'use client';

import { AnimatePresence, type HTMLMotionProps, motion } from 'motion/react';
import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';
import type { Message } from '@/context/JarvisContext';
import { cn } from '@/lib/shadcn/utils';

type ReceivedMessage = Message;

const MotionContainer = motion.create('div');

const CONTAINER_MOTION_PROPS = {
  variants: {
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeOut' as const,
        duration: 0.3,
      },
    },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.2,
        ease: 'easeOut' as const,
        duration: 0.3,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface ChatTranscriptProps {
  hidden?: boolean;
  messages?: ReceivedMessage[];
}

export function ChatTranscript({
  hidden = false,
  messages = [],
  className,
  ...props
}: ChatTranscriptProps & Omit<HTMLMotionProps<'div'>, 'ref'>) {
  // const { state: agentState } = useAgent();
  const agentState = 'idle'; // Mock para a versão nativa

  return (
    <div className="absolute top-0 bottom-33.75 flex w-full flex-col md:bottom-42.5">
      <AnimatePresence>
        {!hidden && (
          <MotionContainer
            {...props}
            {...CONTAINER_MOTION_PROPS}
            className={cn('flex h-full w-full flex-col gap-4', className)}
          >
            <AgentChatTranscript
              agentState={agentState}
              messages={messages}
              className="mx-auto w-full max-w-2xl [&_.is-user>div]:rounded-[22px] [&>div>div]:px-4 [&>div>div]:pt-40 md:[&>div>div]:px-6"
            />
          </MotionContainer>
        )}
      </AnimatePresence>
    </div>
  );
}
