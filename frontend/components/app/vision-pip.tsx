'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Eye, Maximize2, RefreshCw, Globe, Pin, PinOff } from 'lucide-react';
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
                        "fixed top-24 right-6 z-40 w-64 cyber-glass border border-[#1da3b9]/40 rounded-xl overflow-hidden shadow-2xl transition-all duration-300",
                        isPinned ? "border-[#1da3b9]/80 shadow-[#1da3b9]/20" : "opacity-90 hover:opacity-100"
                    )}
                >
                    {/* Header */}
                    <div className="p-2 bg-[#1da3b9]/10 border-b border-[#1da3b9]/20 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Eye className="size-3 text-[#1da3b9]" />
                            <span className="text-[9px] font-mono text-white/50 uppercase tracking-widest">Jarvis Vision</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <button
                                onClick={() => setIsPinned(!isPinned)}
                                className={cn("p-1 rounded hover:bg-white/5 transition-colors", isPinned ? "text-[#1da3b9]" : "text-white/30")}
                            >
                                {isPinned ? <Pin className="size-3" /> : <PinOff className="size-3" />}
                            </button>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="p-1 rounded hover:bg-white/5 transition-colors text-white/30 hover:text-white"
                            >
                                <span className="text-[10px]">✕</span>
                            </button>
                        </div>
                    </div>

                    {/* Viewport */}
                    <div className="relative aspect-video bg-black/40 overflow-hidden group">
                        {latestImage ? (
                            <img
                                src={latestImage}
                                alt="Jarvis View"
                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                            />
                        ) : (
                            <div className="absolute inset-0 flex items-center justify-center">
                                <RefreshCw className="size-6 text-[#1da3b9]/20 animate-spin" />
                            </div>
                        )}

                        {/* Overlay Controls */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2">
                            <div className="flex items-center justify-between w-full">
                                <div className="flex items-center gap-1 text-[8px] font-mono text-white/60">
                                    <Globe className="size-2.5" />
                                    <span>LIVE BROWSER</span>
                                </div>
                                <span className="text-[8px] font-mono text-white/30">{lastUpdate}</span>
                            </div>
                        </div>
                    </div>

                    {/* Footer Info */}
                    <div className="bg-black/40 p-1.5 flex items-center justify-center gap-2">
                        <div className="size-1 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[8px] font-mono text-white/40 uppercase tracking-tighter">Synchronized with Agent Browser</span>
                    </div>
                </motion.div>
            )}

            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed top-24 right-6 z-40 p-2 cyber-glass border border-[#1da3b9]/40 rounded-full text-[#1da3b9]/60 hover:text-[#1da3b9] transition-all hover:scale-110"
                >
                    <Eye className="size-5" />
                </button>
            )}
        </AnimatePresence>
    );
}
