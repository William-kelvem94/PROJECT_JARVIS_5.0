'use client';

import React, { useEffect, useState } from 'react';
import { Eye, Globe, Maximize2, Pin, PinOff, RefreshCw } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';

interface VisionPiPProps {
  apiUrl?: string;
}

export function VisionPiP({ apiUrl = 'http://localhost:8000' }: VisionPiPProps) {
  const [latestImage, setLatestImage] = useState<string>('');
  const [isOpen, setIsOpen] = useState(true);
  const [isPinned, setIsPinned] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const updateImage = () => {
    // Apenas geramos a URL com cache-buster. O navegador cuida do resto de forma assíncrona.
    const imageUrl = `${apiUrl}/screenshots/last_browser_state.png?t=${Date.now()}`;
    setLatestImage(imageUrl);
    setLastUpdate(new Date().toLocaleTimeString());
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        updateImage();
      }
    }, 12000); // 12 segundos e apenas se visível
    updateImage();
    return () => clearInterval(interval);
  }, [apiUrl]);

  if (!latestImage && !loading) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ scale: 0.8, opacity: 0, x: 20 }}
          animate={{ scale: 1, opacity: 1, x: 0 }}
          exit={{ scale: 0.8, opacity: 0, x: 20 }}
          className={cn(
            'cyber-glass fixed top-24 right-6 z-40 w-64 overflow-hidden rounded-xl border border-[#1da3b9]/40 shadow-2xl transition-all duration-300',
            isPinned ? 'border-[#1da3b9]/80 shadow-[#1da3b9]/20' : 'opacity-90 hover:opacity-100'
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-[#1da3b9]/20 bg-[#1da3b9]/10 p-2">
            <div className="flex items-center gap-2">
              <Eye className="size-3 text-[#1da3b9]" />
              <span className="font-mono text-[9px] tracking-widest text-white/50 uppercase">
                Jarvis Vision
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsPinned(!isPinned)}
                className={cn(
                  'rounded p-1 transition-colors hover:bg-white/5',
                  isPinned ? 'text-[#1da3b9]' : 'text-white/30'
                )}
              >
                {isPinned ? <Pin className="size-3" /> : <PinOff className="size-3" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded p-1 text-white/30 transition-colors hover:bg-white/5 hover:text-white"
              >
                <span className="text-[10px]">✕</span>
              </button>
            </div>
          </div>

          {/* Viewport */}
          <div className="group relative aspect-video overflow-hidden bg-black/40">
            {latestImage ? (
              <img
                src={latestImage}
                alt="Jarvis View"
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <RefreshCw className="size-6 animate-spin text-[#1da3b9]/20" />
              </div>
            )}

            {/* Overlay Controls */}
            <div className="absolute inset-0 flex items-end bg-gradient-to-t from-black/60 via-transparent to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
              <div className="flex w-full items-center justify-between">
                <div className="flex items-center gap-1 font-mono text-[8px] text-white/60">
                  <Globe className="size-2.5" />
                  <span>LIVE BROWSER</span>
                </div>
                <span className="font-mono text-[8px] text-white/30">{lastUpdate}</span>
              </div>
            </div>
          </div>

          {/* Footer Info */}
          <div className="flex items-center justify-center gap-2 bg-black/40 p-1.5">
            <div className="size-1 animate-pulse rounded-full bg-emerald-500" />
            <span className="font-mono text-[8px] tracking-tighter text-white/40 uppercase">
              Synchronized with Agent Browser
            </span>
          </div>
        </motion.div>
      )}

      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="cyber-glass fixed top-24 right-6 z-40 rounded-full border border-[#1da3b9]/40 p-2 text-[#1da3b9]/60 transition-all hover:scale-110 hover:text-[#1da3b9]"
        >
          <Eye className="size-5" />
        </button>
      )}
    </AnimatePresence>
  );
}
