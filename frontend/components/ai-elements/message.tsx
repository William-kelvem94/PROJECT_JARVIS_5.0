'use client';

import React, { HTMLAttributes, ReactNode, useEffect, useState } from 'react';
import { cn } from '@/lib/shadcn/utils';

interface MessageProps extends HTMLAttributes<HTMLDivElement> {
  from: 'user' | 'assistant';
  text?: string;
  children?: ReactNode;
  senderType?: 'local' | 'cloud';
  timestamp?: string;
}

const Typewriter = ({ text, speed = 20 }: { text: string; speed?: number }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return <span>{displayedText}</span>;
};

export const Message = ({
  className,
  from,
  text,
  children,
  senderType = 'local',
  timestamp,
  ...props
}: MessageProps) => {
  const isUser = from === 'user';
  const isLocal = senderType === 'local';

  return (
    <div
      className={cn(
        'group mb-4 flex w-full max-w-[95%] flex-col gap-2',
        isUser ? 'ml-auto items-end' : 'mr-auto items-start',
        className
      )}
      {...props}
    >
      <div
        className={cn(
          'relative rounded-lg border p-4 font-mono text-sm backdrop-blur-xl transition-all duration-500',
          isUser
            ? 'border-slate-500/30 bg-slate-800/40 text-slate-200'
            : isLocal
              ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-100 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
              : 'border-purple-500/50 bg-purple-500/10 text-purple-100 shadow-[0_0_15px_rgba(168,85,247,0.2)]'
        )}
      >
        {!isUser && (
          <div className="mb-1 flex items-center gap-2">
            <span
              className={cn(
                'text-[10px] font-bold tracking-tighter uppercase',
                isLocal ? 'text-cyan-400' : 'text-purple-400'
              )}
            >
              {isLocal ? '⚡ LOCAL_AI' : '☁️ CLOUD_CORE'}
            </span>
            {timestamp && <span className="text-[9px] text-gray-500">{timestamp}</span>}
          </div>
        )}

        <div className="relative z-10 leading-relaxed">
          {children ??
            (!isUser ? (
              <>
                <Typewriter text={text ?? ''} />
                <span className="ml-1 inline-block h-4 w-2 animate-pulse bg-current" />
              </>
            ) : (
              text
            ))}
        </div>

        {!isUser && (
          <div
            className={cn(
              'pointer-events-none absolute -inset-0.5 rounded-lg opacity-30 blur',
              isLocal ? 'bg-cyan-500' : 'bg-purple-500'
            )}
          />
        )}
      </div>
    </div>
  );
};

export type MessageContentProps = HTMLAttributes<HTMLDivElement>;

export const MessageContent = ({ children, className, ...props }: MessageContentProps) => (
  <div
    className={cn(
      'flex w-fit max-w-full min-w-0 flex-col gap-2 overflow-hidden text-sm',
      className
    )}
    {...props}
  >
    {children}
  </div>
);

export const MessageResponse = ({ children, className, ...props }: MessageContentProps) => (
  <div className={cn('break-words whitespace-pre-wrap', className)} {...props}>
    {children}
  </div>
);
