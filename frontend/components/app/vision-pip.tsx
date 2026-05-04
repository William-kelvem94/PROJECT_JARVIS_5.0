'use client';

import React, { useState, useEffect } from 'react';
import { Eye, Globe, Pin, PinOff, RefreshCw } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';

interface VisionPiPProps {
  apiUrl?: string;
  detections?: Array<{ label: string; box: [number, number, number, number] }>;
}

export function VisionPiP({
  apiUrl = process.env.NEXT_PUBLIC_JARVIS_API_URL || 'http://localhost:8000',
  detections = []
}: VisionPiPProps) {
  const [latestImage, setLatestImage] = useState<string>('');
  const [isOpen, setIsOpen] = useState(true);
  const [isPinned, setIsPinned] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  const updateImage = () => {
    const imageUrl = `${apiUrl}/screenshots/last_browser_state.png?t=${Date.now()}`;
    setLatestImage(imageUrl);
    setLastUpdate(new Date().toLocaleTimeString());
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        updateImage();
      }
    }, 12000);
    updateImage();
    return () => clearInterval(interval);
  }, [apiUrl]);

  if (!latestImage) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ scale: 0.8, opacity: 0, x: 20 }}
          animate={{ scale: 1, opacity: 1, x: 0 }}
          exit={{ scale: 0.8, opacity: 0, x: 20 }}
          className={cn(
            'fixed top-24 right-6 z-40 w-64 overflow-hidden rounded-lg border border-cyan-500/50 shadow-[0_0_20px_rgba(34,211,238,0.3)] backdrop-blur-md transition-all duration-300',
            isPinned ? 'border-cyan-500 shadow-cyan-500/20' : 'opacity-90 hover:opacity-100'
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-cyan-500/30 bg-cyan-500/10 p-2 font-mono">
            <div className="flex items-center gap-2">
              <Eye className="size-3 text-cyan-400" />
              <span className="text-[9px] tracking-widest text-cyan-400/70 uppercase">
                Vision_Active_v5
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsPinned(!isPinned)}
                className={cn(
                  'rounded p-1 transition-colors hover:bg-cyan-500/20',
                  isPinned ? 'text-cyan-400' : 'text-white/30'
                )}
              >
                {isPinned ? <Pin className="size-3" /> : <PinOff className="size-3" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded p-1 text-white/30 transition-colors hover:bg-cyan-500/20 hover:text-white"
              >
                <span className="text-[10px]">✕</span>
              </button>
            </div>
          </div>

          {/* Viewport */}
          <div className="group relative aspect-video overflow-hidden bg-black">
            {latestImage ? (
              <img
                src={latestImage}
                alt="Jarvis View"
                className="h-full w-full object-cover opacity-80 transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <RefreshCw className="size-6 animate-spin text-cyan-500/20" />
              </div>
            )}

            {/* Holographic Scanning Line */}
            <div
              className="absolute inset-x-0 h-0.5 bg-cyan-400/50 shadow-[0_0_10px_rgba(34,211,238,0.8)] z-10"
              style={{
                animation: 'scan-line 3s linear infinite'
              }}
            />

            {/* Bounding Boxes */}
            {detections.map((det, i) => (
              <div
                key={i}
                className="absolute border-2 border-cyan-400 text-cyan-400 text-[10px] font-bold z-20"
                style={{
                  left: `${det.box[0]}%`,
                  top: `${det.box[1]}%`,
                  width: `${det.box[2]}%`,
                  height: `${det.box[3]}%`,
                }}
              >
                <span className="absolute -top-4 left-0 bg-cyan-400 text-black px-1 font-bold">
                  {det.label}
                </span>
              </div>
            ))}

            {/* Overlay Controls */}
            <div className="absolute inset-0 flex items-end bg-linear-to-t from-black/80 via-transparent to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100 z-10">
              <div className="flex w-full items-center justify-between">
                <div className="flex items-center gap-1 font-mono text-[8px] text-cyan-400/80">
                  <Globe className="size-2.5" />
                  <span className="tracking-tighter">LIVE_SENSORS_ACTIVE</span>
                </div>
                <span className="font-mono text-[8px] text-cyan-400/40">{lastUpdate}</span>
              </div>
            </div>
          </div>

          {/* Footer Info */}
          <div className="flex items-center justify-center gap-2 bg-black/60 p-1.5 font-mono">
            <div className="size-1 animate-pulse rounded-full bg-cyan-500" />
            <span className="text-[8px] tracking-tighter text-cyan-400/60 uppercase">
              CORE_SYNC: STABLE // VIS_SENSORS: ON
            </span>
          </div>

          <style>{`
            @keyframes scan-line {
              0% { top: 0%; }
              100% { top: 100%; }
            }
          `}</style>
        </motion.div>
      )}

      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed top-24 right-6 z-40 rounded-full border border-cyan-500/40 bg-black/40 p-2 text-cyan-400/60 backdrop-blur-md transition-all hover:scale-110 hover:text-cyan-400"
        >
          <Eye className="size-5" />
        </button>
      )}
    </AnimatePresence>
  );
}
