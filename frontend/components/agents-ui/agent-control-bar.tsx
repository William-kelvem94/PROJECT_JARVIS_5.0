import { type ComponentProps, useEffect, useRef, useState } from 'react';
import {
  Loader,
  MessageSquareTextIcon,
  Mic,
  MicOff,
  Monitor,
  PhoneOff,
  Pin,
  SendHorizontal,
  Video,
  VideoOff,
} from 'lucide-react';
import { motion } from 'motion/react';
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
    if (chatOpen) return;
    inputRef.current?.focus();
  }, [chatOpen]);

  return (
    <form
      onSubmit={handleSubmit}
      className={cn('mb-3 flex grow items-end gap-2 rounded-md pl-1 text-sm', className)}
    >
      <textarea
        autoFocus
        ref={inputRef}
        value={message}
        disabled={!chatOpen}
        placeholder="Digite algo para o Jarvis Native..."
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
        className="field-sizing-content max-h-16 min-h-8 flex-1 bg-transparent py-2 text-white [scrollbar-width:thin] focus:outline-none disabled:cursor-not-allowed"
      />
      <Button
        size="icon"
        type="submit"
        disabled={isDisabled}
        variant={isDisabled ? 'secondary' : 'default'}
        className="self-end disabled:cursor-not-allowed"
      >
        {isSending ? <Loader className="animate-spin" /> : <SendHorizontal />}
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
  className?: string;
}

export function AgentControlBar({
  controls,
  isChatOpen = false,
  onIsChatOpenChange,
  className,
  ...props
}: AgentControlBarProps & ComponentProps<'div'>) {
  const [isChatOpenUncontrolled, setIsChatOpenUncontrolled] = useState(isChatOpen);
  const [isVisible, setIsVisible] = useState(true);
  const [isLocked, setIsLocked] = useState(false);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const {
    isConnected,
    isMicEnabled,
    isCameraEnabled,
    isScreenSharing,
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
        }, 5000); // 5 seguntos de visibilidade
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
        'relative z-50 mx-auto w-fit min-w-75',
        !isVisible &&
          !isChatOpen &&
          !isChatOpenUncontrolled &&
          !isLocked &&
          'pointer-events-none transition-all'
      )}
      onMouseEnter={() => {
        setIsVisible(true);
        if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
      }}
    >
      <div
        className={cn(
          'flex flex-col rounded-xl border border-[#1da3b9]/20 bg-black/40 p-3 shadow-2xl shadow-[#1da3b9]/5 backdrop-blur-xl',
          className
        )}
        {...props}
      >
        <motion.div
          animate={isChatOpen || isChatOpenUncontrolled ? 'visible' : 'hidden'}
          variants={{
            hidden: { height: 0, opacity: 0, marginBottom: 0 },
            visible: { height: 'auto', opacity: 1, marginBottom: 12 },
          }}
          className="border-input/50 flex w-full items-start overflow-hidden border-b"
        >
          <AgentChatInput
            chatOpen={isChatOpen || isChatOpenUncontrolled}
            onSend={handleSendMessage}
            className="[&_button]:rounded-md"
          />
        </motion.div>

        <div className="flex items-center gap-1">
          <div className="flex grow items-center gap-2">
            <button
              onClick={() => setIsLocked(!isLocked)}
              className={cn(
                'mr-1 rounded-full p-2 transition-all duration-300',
                isLocked
                  ? 'bg-[#1da3b9]/20 text-[#43d9f0]'
                  : 'text-white/40 hover:bg-white/5 hover:text-white/60'
              )}
              title="Fixar Barra"
            >
              <Pin className="size-4" />
            </button>

            {controls?.microphone !== false && (
              <Toggle
                aria-label="Alternar microfone"
                pressed={isMicEnabled}
                onPressedChange={() => toggleMic()}
                className={cn(!isMicEnabled && 'bg-red-400/10 text-red-400')}
                disabled={!isConnected}
              >
                {!isMicEnabled ? <MicOff className="size-4" /> : <Mic className="size-4" />}
              </Toggle>
            )}

            {controls?.camera !== false && (
              <Toggle
                aria-label="Alternar câmera"
                pressed={isCameraEnabled}
                onPressedChange={() => toggleCamera()}
                className={cn(isCameraEnabled ? 'bg-[#1da3b9]/10 text-[#43d9f0]' : 'text-white/40')}
                disabled={!isConnected}
              >
                {!isCameraEnabled ? <VideoOff className="size-4" /> : <Video className="size-4" />}
              </Toggle>
            )}

            {controls?.screenShare !== false && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => toggleScreenShare()}
                className={cn(
                  'rounded-md',
                  isScreenSharing
                    ? 'bg-[#1da3b9]/10 text-[#43d9f0]'
                    : 'text-white/40 hover:bg-[#1da3b9]/10 hover:text-[#1da3b9]'
                )}
                title="Compartilhar Tela"
                disabled={!isConnected}
              >
                <Monitor className="size-4" />
              </Button>
            )}

            {controls?.chat !== false && (
              <Toggle
                pressed={isChatOpen || isChatOpenUncontrolled}
                onPressedChange={(state: boolean) => {
                  if (!onIsChatOpenChange) setIsChatOpenUncontrolled(state);
                  else onIsChatOpenChange(state);
                }}
              >
                <MessageSquareTextIcon className="size-4" />
              </Toggle>
            )}
          </div>

          <div className="mx-2 h-6 w-px bg-white/10" />

          {controls?.leave !== false && (
            <Button
              onClick={() => disconnect()}
              disabled={!isConnected}
              variant="destructive"
              className="h-9 rounded-full px-6 font-mono text-xs font-bold tracking-wider"
            >
              ENCERRAR
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
