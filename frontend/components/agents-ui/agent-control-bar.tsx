import { type ComponentProps, useEffect, useRef, useState } from 'react';
import { Loader, MessageSquareTextIcon, Pin, SendHorizontal, Mic, MicOff, PhoneOff, Monitor, Video, VideoOff } from 'lucide-react';
import { motion } from 'motion/react';
import { Button } from '@/components/ui/button';
import { Toggle } from '@/components/ui/toggle';
import { cn } from '@/lib/shadcn/utils';
import { useJarvis } from '@/context/JarvisContext';

interface AgentChatInputProps {
  chatOpen: boolean;
  onSend?: (message: string) => void;
  className?: string;
}

function AgentChatInput({ chatOpen, onSend = async () => { }, className }: AgentChatInputProps) {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [isSending, setIsSending] = useState(false);
  const [message, setMessage] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
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
    <form onSubmit={handleSubmit} className={cn('mb-3 flex grow items-end gap-2 rounded-md pl-1 text-sm', className)}>
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
                handleSubmit(e as any);
            }
        }}
        className="field-sizing-content max-h-16 min-h-8 flex-1 py-2 [scrollbar-width:thin] focus:outline-none disabled:cursor-not-allowed bg-transparent text-white"
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
  variant?: 'default' | 'outline' | 'livekit';
  controls?: AgentControlBarControls;
  isChatOpen?: boolean;
  onIsChatOpenChange?: (open: boolean) => void;
  className?: string;
}

export function AgentControlBar({
  variant = 'default',
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
    sendMessage 
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
        opacity: isVisible || isChatOpen || isChatOpenUncontrolled || isLocked ? 1 : 0
      }}
      transition={{ duration: 0.4, ease: "easeInOut" }}
      className={cn("relative mx-auto w-fit min-w-75 z-50", !isVisible && !isChatOpen && !isChatOpenUncontrolled && !isLocked && "pointer-events-none transition-all")}
      onMouseEnter={() => {
        setIsVisible(true);
        if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
      }}
    >
      <div
        className={cn(
          'backdrop-blur-xl bg-black/40 border-[#1da3b9]/20 flex flex-col border p-3 shadow-2xl shadow-[#1da3b9]/5',
          variant === 'livekit' ? 'rounded-[31px]' : 'rounded-xl',
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
            className={cn(variant === 'livekit' && '[&_button]:rounded-full')}
          />
        </motion.div>

        <div className="flex gap-1 items-center">
          <div className="flex grow gap-2 items-center">
            <button
              onClick={() => setIsLocked(!isLocked)}
              className={cn(
                "p-2 rounded-full transition-all duration-300 mr-1",
                isLocked ? "text-[#43d9f0] bg-[#1da3b9]/20" : "text-white/40 hover:text-white/60 hover:bg-white/5"
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
                className={cn(!isMicEnabled && "text-red-400 bg-red-400/10")}
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
                className={cn(isCameraEnabled ? "text-[#43d9f0] bg-[#1da3b9]/10" : "text-white/40")}
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
                    "rounded-md",
                    isScreenSharing ? "text-[#43d9f0] bg-[#1da3b9]/10" : "text-white/40 hover:text-[#1da3b9] hover:bg-[#1da3b9]/10"
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

          <div className="mx-2 h-6 w-[1px] bg-white/10" />

          {controls?.leave !== false && (
            <Button
              onClick={() => disconnect()}
              disabled={!isConnected}
              variant="destructive"
              className="rounded-full font-mono text-xs font-bold tracking-wider px-6 h-9"
            >
               ENCERRAR
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

