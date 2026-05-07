'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { Camera, ChevronLeft, ChevronRight, Maximize2, X } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';

interface ScreenshotGalleryProps {
  apiUrl?: string;
  className?: string;
}

export function ScreenshotGallery({ apiUrl, className }: ScreenshotGalleryProps) {
  const [screenshots, setScreenshots] = useState<string[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);

  const fetchScreenshots = useCallback(async () => {
    try {
      const baseUrl = apiUrl || window.location.origin;
      const res = await fetch(`${baseUrl}/screenshots`);
      const data = await res.json();
      if (data.screenshots && data.screenshots.length > 0) {
        setScreenshots(data.screenshots);
      }
    } catch (e) {
      console.error('Error fetching screenshots:', e);
    }
  }, [apiUrl]);

  useEffect(() => {
    fetchScreenshots();
    const interval = setInterval(fetchScreenshots, 30000); // Polling cada 30s para performance
    return () => clearInterval(interval);
  }, [fetchScreenshots]);

  if (screenshots.length === 0) return null;

  const currentScreenshot = screenshots[selectedIndex];
  const screenshotUrl = `${apiUrl || window.location.origin}/screenshots/${currentScreenshot}`;

  return (
    <div className={cn('pointer-events-auto', className)}>
      {/* Mini Preview Float */}
      <AnimatePresence>
        {!isExpanded && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="group relative cursor-pointer overflow-hidden rounded-xl border border-white/10 bg-black/40 shadow-2xl backdrop-blur-md"
            onClick={() => setIsExpanded(true)}
          >
            <div className="absolute inset-0 bg-[#1da3b9]/5 transition-colors group-hover:bg-[#1da3b9]/10" />
            {/* Runtime screenshots come from the local backend and are not known to Next image config. */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={screenshotUrl}
              alt="Latest view"
              className="h-20 w-32 object-cover opacity-60 transition-opacity group-hover:opacity-100"
            />
            <div className="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity group-hover:opacity-100">
              <div className="rounded-full border border-white/20 bg-black/60 p-2">
                <Maximize2 className="size-4 text-white" />
              </div>
            </div>
            <div className="absolute bottom-1 left-2 flex items-center gap-1">
              <Camera className="size-2 text-[#1da3b9]" />
              <span className="font-mono text-[8px] tracking-tighter text-white/50 uppercase">
                Live View
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Expanded Modal */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed inset-4 z-100 flex flex-col gap-4 rounded-3xl border border-white/10 bg-black/80 p-6 shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-2xl md:inset-20"
          >
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-[#1da3b9]/20 p-2">
                  <Camera className="size-5 text-[#1da3b9]" />
                </div>
                <div>
                  <h3 className="text-sm font-bold tracking-wider text-white uppercase">
                    Visual Memory Hub
                  </h3>
                  <p className="font-mono text-[10px] text-white/40 italic">{currentScreenshot}</p>
                </div>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="rounded-full p-2 text-white/40 transition-colors hover:bg-white/5 hover:text-white"
              >
                <X className="size-6" />
              </button>
            </div>

            <div className="group relative flex-1 overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/50">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={screenshotUrl}
                alt="Expanded view"
                className="h-full w-full object-contain"
              />

              {/* Navigation Controls */}
              <div className="absolute inset-x-4 top-1/2 flex -translate-y-1/2 justify-between opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  disabled={selectedIndex === screenshots.length - 1}
                  onClick={() => setSelectedIndex((s) => Math.min(screenshots.length - 1, s + 1))}
                  className="rounded-full border border-white/10 bg-black/60 p-3 transition-all hover:border-[#1da3b9]/40 hover:bg-[#1da3b9]/20 disabled:opacity-20"
                >
                  <ChevronLeft className="size-6 text-white" />
                </button>
                <button
                  disabled={selectedIndex === 0}
                  onClick={() => setSelectedIndex((s) => Math.max(0, s - 1))}
                  className="rounded-full border border-white/10 bg-black/60 p-3 transition-all hover:border-[#1da3b9]/40 hover:bg-[#1da3b9]/20 disabled:opacity-20"
                >
                  <ChevronRight className="size-6 text-white" />
                </button>
              </div>
            </div>

            {/* Thumbnails Strip */}
            <div className="scrollbar-none flex gap-2 overflow-x-auto py-2">
              {screenshots.map((s, i) => (
                <button
                  key={s}
                  onClick={() => setSelectedIndex(i)}
                  className={cn(
                    'relative h-16 w-24 flex-none overflow-hidden rounded-lg border-2 transition-all',
                    selectedIndex === i
                      ? 'scale-105 border-[#1da3b9]'
                      : 'border-transparent opacity-40 hover:opacity-100'
                  )}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={`${apiUrl || window.location.origin}/screenshots/${s}`}
                    alt={`Screenshot ${i + 1}`}
                    className="h-full w-full object-cover"
                  />
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
