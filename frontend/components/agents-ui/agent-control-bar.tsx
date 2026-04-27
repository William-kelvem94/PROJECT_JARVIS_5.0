'use client';

import { type ComponentProps, useEffect, useRef, useState } from 'react';
import {
  ChatCircleText,
  Microphone,
  MicrophoneSlash,
  Monitor,
  Video,
  VideoCameraSlash,
  PaperPlaneRight,
  PushPin,
  CircleNotch,
  Power,
} from '@phosphor-icons/react';
import { AnimatePresence, motion } from 'motion/react';
import { Button } from '@/components/ui/button';
import { Toggle } from '@/components/ui/toggle';
import { useJarvis } from '@/context/JarvisContext';
import { cn } from '@/lib/shadcn/utils';

interface AgentChatInputProps {
  chatOpen: boolean;
  onSend?: (message: string) => void;
  className?: string;
}

function AgentChatInput({ chatOpen, onSend = async () => {}, className }: AgentChatInputProps) {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [isSending, setIsSending] = useState(false);
  const [message, setMessage] = useState<string>('');

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement> | React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    e.preventDefault();
    if (!message.trim()) return;
    try {
      setIsSending(true);
      await onSend(message);
      setMessage('');
    } finally {
      setIsSending(false);
    }
  };

  const isDisabled = isSending || message.trim().length === 0;

  useEffect(() => {
    if (chatOpen) {
      inputRef.current?.focus();
    }
  }, [chatOpen]);

  return (
    <form
      onSubmit={handleSubmit}
      className={cn('mb-4 flex grow items-end gap-3 rounded-xl border border-white/5 bg-white/[0.03] p-2 transition-all focus-within:border-jarvis-cyan/30 focus-within:bg-white/[0.06]', className)}
    >
      <textarea
        ref={inputRef}
        value={message}
        disabled={!chatOpen}
        placeholder="Transmitir comando de texto..."
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
        className="field-sizing-content max-h-24 min-h-10 flex-1 bg-transparent px-3 py-2.5 font-mono text-xs tracking-wide text-white [scrollbar-width:thin] focus:outline-none disabled:cursor-not-allowed placeholder:text-white/10"
      />
      <Button
        size="icon"
        type="submit"
        disabled={isDisabled}
        className={cn(
          "size-10 shrink-0 rounded-lg transition-all",
          isDisabled ? "bg-white/5 text-white/20" : "bg-jarvis-cyan text-black shadow-[0_0_15px_rgba(0,242,255,0.3)] hover:scale-105 active:scale-95"
        )}
      >
        {isSending ? <CircleNotch className="animate-spin size-5" /> : <PaperPlaneRight weight="fill" className="size-5" />}
      </Button>
    </form>
  );
}

export interface AgentControlBarControls {
  leave?: boolean;
  camera?: boolean;
  microphone?: boolean;
  screenShare?: boolean;
  chat?: boolean;
}

export interface AgentControlBarProps {
  controls?: AgentControlBarControls;
  isChatOpen?: boolean;
  onIsChatOpenChange?: (open: boolean) => void;
  onLeave?: () => void;
  className?: string;
}

export function AgentControlBar({
  controls,
  isChatOpen = false,
  onIsChatOpenChange,
  onLeave,
  className,
  ...props
}: AgentControlBarProps & ComponentProps<'div'>) {
  const [isChatOpenUncontrolled, setIsChatOpenUncontrolled] = useState(isChatOpen);
  const [isVisible, setIsVisible] = useState(true);
  const [isLocked, setIsLocked] = useState(false);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const {
    isMicEnabled,
    isCameraEnabled,
    isScreenSharing,
    localStream,
    toggleMic,
    toggleCamera,
    toggleScreenShare,
    disconnect,
    sendMessage,
  } = useJarvis();

  useEffect(() => {
    const handleMouseMove = () => {
      setIsVisible(true);
      if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
      if (!isChatOpen && !isChatOpenUncontrolled && !isLocked) {
        hideTimeoutRef.current = setTimeout(() => {
          setIsVisible(false);
        }, 5000);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    handleMouseMove();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
    };
  }, [isChatOpen, isChatOpenUncontrolled, isLocked]);

  const handleSendMessage = async (message: string) => {
    sendMessage(message);
  };

  return (
    <motion.div
      initial={false}
      animate={{
        y: isVisible || isChatOpen || isChatOpenUncontrolled || isLocked ? 0 : 20,
        opacity: isVisible || isChatOpen || isChatOpenUncontrolled || isLocked ? 1 : 0,
      }}
      transition={{ duration: 0.4, ease: 'easeInOut' }}
      className={cn(
        'relative z-50 mx-auto w-fit min-w-80',
        !isVisible && !isChatOpen && !isChatOpenUncontrolled && !isLocked && 'pointer-events-none'
      )}
      onMouseEnter={() => {
        setIsVisible(true);
        if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
      }}
    >
      <div
        className={cn(
          'flex flex-col overflow-hidden rounded-2xl border border-white/10 bg-black/40 p-4 shadow-[0_0_40px_rgba(0,0,0,0.5)] backdrop-blur-2xl',
          className
        )}
        {...props}
      >
        <AnimatePresence>
          {(isChatOpen || isChatOpenUncontrolled) && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <AgentChatInput
                chatOpen={isChatOpen || isChatOpenUncontrolled}
                onSend={handleSendMessage}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setIsLocked(!isLocked)}
              className={cn(
                'group relative rounded-lg p-2.5 transition-all',
                isLocked ? 'bg-jarvis-cyan/20 text-jarvis-cyan' : 'text-white/20 hover:bg-white/5 hover:text-white/40'
              )}
              title="Fixar Barra de Controle"
            >
              <PushPin weight={isLocked ? "fill" : "regular"} className="size-4" />
              {isLocked && <motion.div layoutId="active-dot" className="absolute top-1 right-1 size-1 rounded-full bg-jarvis-cyan shadow-[0_0_5px_#00f2ff]" />}
            </button>

            <div className="mx-1 h-4 w-px bg-white/5" />

            {controls?.microphone !== false && (
              <Toggle
                pressed={isMicEnabled}
                onPressedChange={() => toggleMic()}
                disabled={!localStream}
                className={cn(
                  "size-10 rounded-lg transition-all",
                  isMicEnabled ? "text-jarvis-cyan bg-jarvis-cyan/10" : "text-red-500 bg-red-500/10"
                )}
              >
                {isMicEnabled ? <Microphone weight="duotone" className="size-5" /> : <MicrophoneSlash weight="duotone" className="size-5" />}
              </Toggle>
            )}

            {controls?.camera !== false && (
              <Toggle
                pressed={isCameraEnabled}
                onPressedChange={() => toggleCamera()}
                className={cn(
                  "size-10 rounded-lg transition-all",
                  isCameraEnabled ? "text-jarvis-cyan bg-jarvis-cyan/10" : "text-white/20 hover:bg-white/5"
                )}
              >
                {isCameraEnabled ? <Video weight="duotone" className="size-5" /> : <VideoCameraSlash weight="duotone" className="size-5" />}
              </Toggle>
            )}

            {controls?.screenShare !== false && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => toggleScreenShare()}
                className={cn(
                  "size-10 rounded-lg transition-all",
                  isScreenSharing ? "text-jarvis-cyan bg-jarvis-cyan/10" : "text-white/20 hover:bg-white/5"
                )}
              >
                <Monitor weight="duotone" className="size-5" />
              </Button>
            )}

            {controls?.chat !== false && (
              <Toggle
                pressed={isChatOpen || isChatOpenUncontrolled}
                onPressedChange={(state: boolean) => {
                  if (!onIsChatOpenChange) setIsChatOpenUncontrolled(state);
                  else onIsChatOpenChange(state);
                }}
                className={cn(
                  "size-10 rounded-lg transition-all",
                  (isChatOpen || isChatOpenUncontrolled) ? "text-jarvis-cyan bg-jarvis-cyan/10" : "text-white/20 hover:bg-white/5"
                )}
              >
                <ChatCircleText weight="duotone" className="size-5" />
              </Toggle>
            )}
          </div>

          {controls?.leave !== false && (
            <Button
              onClick={() => { onLeave ? onLeave() : disconnect(); }}
              className="group relative flex h-10 items-center gap-2 overflow-hidden rounded-lg bg-red-500/10 px-5 font-mono text-[10px] font-black tracking-[0.2em] text-red-500 transition-all hover:bg-red-500 hover:text-white"
            >
              <Power weight="bold" className="size-4" />
              <span>TERMINAR</span>
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
