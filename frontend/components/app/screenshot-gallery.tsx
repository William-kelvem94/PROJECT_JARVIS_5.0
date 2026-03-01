'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Camera, X, ChevronLeft, ChevronRight, Maximize2 } from 'lucide-react';
import { cn } from '@/lib/shadcn/utils';

interface ScreenshotGalleryProps {
    apiUrl?: string;
    className?: string;
}

export function ScreenshotGallery({ apiUrl, className }: ScreenshotGalleryProps) {
    const [screenshots, setScreenshots] = useState<string[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [isOpen, setIsOpen] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    const fetchScreenshots = async () => {
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
    };

    useEffect(() => {
        fetchScreenshots();
        const interval = setInterval(fetchScreenshots, 12000); // Polling cada 12s para performance
        return () => clearInterval(interval);
    }, [apiUrl]);

    if (screenshots.length === 0) return null;

    const currentScreenshot = screenshots[selectedIndex];
    const screenshotUrl = `${apiUrl || window.location.origin}/screenshots/${currentScreenshot}`;

    return (
        <div className={cn("pointer-events-auto", className)}>
            {/* Mini Preview Float */}
            <AnimatePresence>
                {!isExpanded && (
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="group relative cursor-pointer overflow-hidden rounded-xl border border-white/10 bg-black/40 backdrop-blur-md shadow-2xl"
                        onClick={() => setIsExpanded(true)}
                    >
                        <div className="absolute inset-0 bg-[#1da3b9]/5 group-hover:bg-[#1da3b9]/10 transition-colors" />
                        <img
                            src={screenshotUrl}
                            alt="Latest view"
                            className="h-20 w-32 object-cover opacity-60 group-hover:opacity-100 transition-opacity"
                        />
                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="bg-black/60 p-2 rounded-full border border-white/20">
                                <Maximize2 className="size-4 text-white" />
                            </div>
                        </div>
                        <div className="absolute bottom-1 left-2 flex items-center gap-1">
                            <Camera className="size-2 text-[#1da3b9]" />
                            <span className="text-[8px] text-white/50 font-mono uppercase tracking-tighter">Live View</span>
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
                        className="fixed inset-4 z-[100] flex flex-col gap-4 rounded-3xl border border-white/10 bg-black/80 p-6 backdrop-blur-2xl shadow-[0_0_50px_rgba(0,0,0,0.5)] md:inset-20"
                    >
                        <div className="flex items-center justify-between border-b border-white/5 pb-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-[#1da3b9]/20 rounded-lg">
                                    <Camera className="size-5 text-[#1da3b9]" />
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-white uppercase tracking-wider">Visual Memory Hub</h3>
                                    <p className="text-[10px] text-white/40 font-mono italic">{currentScreenshot}</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsExpanded(false)}
                                className="p-2 hover:bg-white/5 rounded-full text-white/40 hover:text-white transition-colors"
                            >
                                <X className="size-6" />
                            </button>
                        </div>

                        <div className="relative flex-1 group overflow-hidden rounded-2xl bg-zinc-900/50 border border-white/5">
                            <img
                                src={screenshotUrl}
                                alt="Expanded view"
                                className="h-full w-full object-contain"
                            />

                            {/* Navigation Controls */}
                            <div className="absolute inset-x-4 top-1/2 -translate-y-1/2 flex justify-between opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    disabled={selectedIndex === screenshots.length - 1}
                                    onClick={() => setSelectedIndex(s => Math.min(screenshots.length - 1, s + 1))}
                                    className="p-3 bg-black/60 border border-white/10 rounded-full hover:bg-[#1da3b9]/20 hover:border-[#1da3b9]/40 disabled:opacity-20 transition-all"
                                >
                                    <ChevronLeft className="size-6 text-white" />
                                </button>
                                <button
                                    disabled={selectedIndex === 0}
                                    onClick={() => setSelectedIndex(s => Math.max(0, s - 1))}
                                    className="p-3 bg-black/60 border border-white/10 rounded-full hover:bg-[#1da3b9]/20 hover:border-[#1da3b9]/40 disabled:opacity-20 transition-all"
                                >
                                    <ChevronRight className="size-6 text-white" />
                                </button>
                            </div>
                        </div>

                        {/* Thumbnails Strip */}
                        <div className="flex gap-2 overflow-x-auto py-2 scrollbar-none">
                            {screenshots.map((s, i) => (
                                <button
                                    key={s}
                                    onClick={() => setSelectedIndex(i)}
                                    className={cn(
                                        "relative flex-none h-16 w-24 rounded-lg overflow-hidden border-2 transition-all",
                                        selectedIndex === i ? "border-[#1da3b9] scale-105" : "border-transparent opacity-40 hover:opacity-100"
                                    )}
                                >
                                    <img src={`${apiUrl || window.location.origin}/screenshots/${s}`} className="h-full w-full object-cover" />
                                </button>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
