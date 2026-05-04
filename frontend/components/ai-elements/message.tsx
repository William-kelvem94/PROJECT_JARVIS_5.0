'use client';

import React, { useState, useEffect } from 'react';
import { HTMLAttributes } from 'react';
import { cn } from '@/lib/shadcn/utils';

interface MessageProps extends HTMLAttributes<HTMLDivElement> {
  from: 'user' | 'assistant';
  text: string;
  senderType?: 'local' | 'cloud';
  timestamp?: string;
}

const Typewriter = ({ text, speed = 20 }: { text: string; speed?: number }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        {
          setDisplayedText((prev) => prev + text[currentIndex]);
          setCurrentIndex((prev) => prev + 1);
        },
        speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return <span>{displayedText}</span>;
};

export const Message = ({ className, from, text, senderType = 'local', timestamp, ...props }: MessageProps) => {
  const isUser = from === 'user';
  const isLocal = senderType === 'local';

  return (
    <div
      className={cn(
        'group flex w-full max-w-[95%] flex-col gap-2 mb-4',
        isUser ? 'ml-auto items-end' : 'mr-auto items-start',
        className
      )}
      {...props}
    >
      <div className={cn(
        'relative p-4 rounded-lg backdrop-blur-xl border transition-all duration-500 font-mono text-sm',
        isUser
          ? 'bg-slate-800/40 border-slate-500/30 text-slate-200'
          : isLocal
            ? 'bg-cyan-500/10 border-cyan-500/50 text-cyan-100 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
            : 'bg-purple-500/10 border-purple-500/50 text-purple-100 shadow-[0_0_15px_rgba(168,85,247,0.2)]'
      )}>
        {!isUser && (
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              "text-[10px] font-bold uppercase tracking-tighter",
              isLocal ? 'text-cyan-400' : 'text-purple-400'
            )}>
              {isLocal ? '⚡ LOCAL_AI' : '☁️ CLOUD_CORE'}
            </span>
            {timestamp && <span className="text-[9px] text-gray-500">{timestamp}</span>}
          </div>
        )}

        <div className="relative z-10 leading-relaxed">
          {!isUser ? (
            <>
              <Typewriter text={text} />
              <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
            </>
          ) : (
            text
          )}
        </div>

        {!isUser && (
          <div className={cn(
            "absolute -inset-0.5 rounded-lg blur opacity-30 pointer-events-none",
            isLocal ? 'bg-cyan-500' : 'bg-purple-500'
          )} />
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
