'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useRoomContext } from '@livekit/components-react';
import { RoomEvent } from 'livekit-client';
import { Cpu, HardDrive, Battery, Shield, Zap, Globe } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/shadcn/utils';

interface TelemetryData {
    type: string;
    cpu: number;
    ram: number;
    battery: number;
    gpu?: number;
    gpu_mem?: number;
    model: string;
    persona: string;
}

export function EngineeringHUD() {
    const room = useRoomContext();
    const [data, setData] = useState<TelemetryData | null>(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        if (!room) return;

        const handleData = (payload: Uint8Array, participant: any, kind: any, topic?: string) => {
            if (topic === 'telemetry') {
                try {
                    const decoder = new TextDecoder();
                    const json = JSON.parse(decoder.decode(payload));
                    if (json.type === 'telemetry_update') {
                        setData(json);
                        if (!isVisible) setIsVisible(true);
                    }
                } catch (e) {
                    console.error('Error parsing telemetry:', e);
                }
            }
        };

        room.on(RoomEvent.DataReceived, handleData);
        return () => {
            room.off(RoomEvent.DataReceived, handleData);
        };
    }, [room, isVisible]);

    if (!data) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 300, opacity: 0 }}
                className="fixed right-6 top-1/2 -translate-y-1/2 z-50 w-64 cyber-glass p-4 rounded-2xl flex flex-col gap-6"
            >
                <div className="flex items-center gap-2 border-b border-white/10 pb-2">
                    <Shield className="size-4 jarvis-cyan-text" />
                    <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-white/70">System Telemetry</span>
                </div>

                {/* CPU */}
                <div className="flex flex-col gap-2">
                    <div className="flex justify-between items-center text-[11px]">
                        <div className="flex items-center gap-2 text-white/50">
                            <Cpu className="size-3" />
                            <span>PROCESSOR</span>
                        </div>
                        <span className="jarvis-cyan-text font-mono">{data.cpu.toFixed(1)}%</span>
                    </div>
                    <Progress value={data.cpu} className="h-1 bg-white/5" indicatorClassName="bg-[#1da3b9] shadow-[0_0_10px_#1da3b9]" />
                </div>

                {/* RAM */}
                <div className="flex flex-col gap-2">
                    <div className="flex justify-between items-center text-[11px]">
                        <div className="flex items-center gap-2 text-white/50">
                            <HardDrive className="size-3" />
                            <span>MEMORY</span>
                        </div>
                        <span className="jarvis-cyan-text font-mono">{data.ram.toFixed(1)}%</span>
                    </div>
                    <Progress value={data.ram} className="h-1 bg-white/5" indicatorClassName="bg-[#1da3b9] shadow-[0_0_10px_#1da3b9]" />
                </div>

                {/* GPU - Show only if exists */}
                {(data.gpu !== undefined && data.gpu > 0) && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="flex flex-col gap-2"
                    >
                        <div className="flex justify-between items-center text-[11px]">
                            <div className="flex items-center gap-2 text-white/50">
                                <Zap className="size-3 text-yellow-400" />
                                <span>GRAPHICS</span>
                            </div>
                            <span className="text-yellow-400 font-mono italic">{data.gpu.toFixed(1)}%</span>
                        </div>
                        <Progress value={data.gpu} className="h-1 bg-white/5" indicatorClassName="bg-yellow-400 shadow-[0_0_10px_#facc15]" />
                    </motion.div>
                )}

                {/* Battery */}
                <div className="flex flex-col gap-2">
                    <div className="flex justify-between items-center text-[11px]">
                        <div className="flex items-center gap-2 text-white/50">
                            <Battery className="size-3" />
                            <span>ENERGY</span>
                        </div>
                        <span className={cn("font-mono", data.battery < 20 ? "text-red-500" : "jarvis-cyan-text")}>
                            {data.battery}%
                        </span>
                    </div>
                    <Progress value={data.battery} className="h-1 bg-white/5" indicatorClassName={cn(data.battery < 20 ? "bg-red-500" : "bg-[#1da3b9]")} />
                </div>

                <div className="mt-2 pt-4 border-t border-white/10 flex flex-col gap-3">
                    <div className="flex items-center justify-between text-[9px] text-white/30 uppercase tracking-widest">
                        <span>Neural Core</span>
                        <span className="text-white/60">{data.model}</span>
                    </div>
                    <div className="flex items-center justify-between text-[9px] text-white/30 uppercase tracking-widest">
                        <span>Active Agent</span>
                        <span className="jarvis-cyan-text">{data.persona.toUpperCase()}</span>
                    </div>
                </div>

                {/* Decoration */}
                <div className="absolute -left-1 top-10 bottom-10 w-[2px] bg-linear-to-b from-transparent via-[#1da3b9]/40 to-transparent" />
            </motion.div>
        </AnimatePresence>
    );
}
