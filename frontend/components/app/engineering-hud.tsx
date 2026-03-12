'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useRoomContext } from '@livekit/components-react';
import { RoomEvent } from 'livekit-client';
import { Cpu, HardDrive, Battery, Shield, Zap, User, Fingerprint, BrainCircuit } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/shadcn/utils';

interface TelemetryData {
    type: string;
    cpu: number;
    ram: number;
    battery: number;
    gpu?: number;
    model: string;
    persona: string;
    // Percepção vinda do perception_manager
    face_emotion?: string;
    face_identity?: string;
    speaker_identity?: string;
    is_reasoning?: boolean;
}

export function EngineeringHUD() {
    const room = useRoomContext();
    const [data, setData] = useState<TelemetryData | null>(null);

    useEffect(() => {
        if (!room) return;

        const handleData = (payload: Uint8Array, participant: any, kind: any, topic?: string) => {
            if (topic === 'telemetry') {
                try {
                    const decoder = new TextDecoder();
                    const json = JSON.parse(decoder.decode(payload));
                    if (json.type === 'telemetry_update') {
                        setData(prev => ({ ...prev, ...json }));
                    }
                } catch (e) {
                    console.error('Error parsing telemetry:', e);
                }
            } else if (topic === 'perception') {
                 // Captura atualizações de percepção enviadas via DataChannel pelo perception_manager
                 try {
                    const decoder = new TextDecoder();
                    const json = JSON.parse(decoder.decode(payload));
                    setData(prev => ({ ...prev, ...json }));
                } catch (e) { }
            }
        };

        room.on(RoomEvent.DataReceived, handleData);
        return () => {
            room.off(RoomEvent.DataReceived, handleData);
        };
    }, [room]);

    if (!data) return null;

    const getEmotionEmoji = (emotion: string) => {
        const emotions: Record<string, string> = {
            'happy': '😊', 'sad': '😢', 'angry': '😠', 'neutral': '😐', 'surprised': '😲', 'fearful': '😨'
        };
        return emotions[emotion.toLowerCase()] || '❓';
    };

    return (
        <AnimatePresence>
            <motion.div
                initial={{ x: 300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 300, opacity: 0 }}
                className="fixed right-6 top-1/2 -translate-y-1/2 z-50 w-64 cyber-glass p-1 rounded-2xl overflow-hidden"
            >
                <div className="bg-white/5 p-4 flex flex-col gap-5">
                    <div className="flex items-center justify-between border-b border-white/10 pb-2">
                        <div className="flex items-center gap-2">
                            <Shield className="size-4 jarvis-cyan-text" />
                            <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-white/70">OS Core 5.0</span>
                        </div>
                        <div className="size-2 rounded-full bg-green-500 animate-pulse" />
                    </div>

                    {/* Hardware Stats */}
                    <div className="space-y-4">
                        <StatRow icon={<Cpu />} label="CPU" value={data.cpu} />
                        <StatRow icon={<HardDrive />} label="RAM" value={data.ram} />
                        {data.gpu !== undefined && <StatRow icon={<Zap className="text-yellow-400" />} label="GPU" value={data.gpu} color="bg-yellow-400" />}
                        <StatRow icon={<Battery />} label="BAT" value={data.battery} color={data.battery < 20 ? "bg-red-500" : "bg-[#1da3b9]"} />
                    </div>

                    {/* Perception Module (The Mastery part) */}
                    <div className="mt-2 pt-4 border-t border-white/10 space-y-3">
                         <span className="text-[8px] uppercase tracking-[0.3em] font-bold text-white/30">Intelligence Layer</span>
                         
                         {/* Face Identity */}
                         <div className="flex items-center justify-between py-1 px-2 bg-white/5 rounded-lg border border-white/5">
                            <div className="flex items-center gap-2">
                                <User className="size-3 text-white/50" />
                                <span className="text-[9px] text-white/70 uppercase">Identify</span>
                            </div>
                            <span className="text-[10px] font-mono jarvis-cyan-text font-bold uppercase tracking-tight">
                                {data.face_identity || 'Unknown'}
                            </span>
                         </div>

                         {/* Emotion */}
                         <div className="flex items-center justify-between py-1 px-2 bg-white/5 rounded-lg border border-white/5">
                            <div className="flex items-center gap-2">
                                <Fingerprint className="size-3 text-white/50" />
                                <span className="text-[9px] text-white/70 uppercase">Affect</span>
                            </div>
                            <span className="text-[10px] font-mono text-violet-400 font-bold uppercase">
                                {data.face_emotion ? `${getEmotionEmoji(data.face_emotion)} ${data.face_emotion}` : 'Awaiting...'}
                            </span>
                         </div>

                         {/* Neural State */}
                         <div className="flex items-center justify-between py-1 px-2 bg-white/5 rounded-lg border border-white/5">
                            <div className="flex items-center gap-2">
                                <BrainCircuit className={cn("size-3", data.is_reasoning ? "text-violet-400 animate-pulse" : "text-white/30")} />
                                <span className="text-[9px] text-white/70 uppercase">Neural</span>
                            </div>
                            <span className={cn("text-[9px] font-bold px-2 rounded-sm", data.is_reasoning ? "bg-violet-500/20 text-violet-400" : "text-white/20")}>
                                {data.is_reasoning ? "THINKING" : "IDLE"}
                            </span>
                         </div>
                    </div>

                    <div className="mt-1 pt-3 flex flex-col gap-1">
                        <div className="flex items-center justify-between text-[8px] text-white/20 uppercase tracking-widest">
                            <span>Core Engine</span>
                            <span className="text-white/40">{data.model}</span>
                        </div>
                    </div>
                </div>
                
                {/* Decorative border */}
                <div className="absolute top-0 right-0 w-16 h-16 border-t-2 border-r-2 border-[#1da3b9]/20 rounded-tr-2xl" />
                <div className="absolute bottom-0 left-0 w-12 h-12 border-b-2 border-l-2 border-[#1da3b9]/10 rounded-bl-2xl" />
            </motion.div>
        </AnimatePresence>
    );
}

function StatRow({ icon, label, value, color = "bg-[#1da3b9]" }: { icon: React.ReactNode, label: string, value: number, color?: string }) {
    return (
        <div className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center text-[10px]">
                <div className="flex items-center gap-2 text-white/40">
                    {React.cloneElement(icon as React.ReactElement, { className: 'size-3' })}
                    <span className="font-mono tracking-tighter">{label}</span>
                </div>
                <span className="text-white/80 font-mono font-bold">{value.toFixed(0)}%</span>
            </div>
            <div className="h-[2px] w-full bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    className={cn("h-full", color, "shadow-[0_0_8px_currentColor]")}
                />
            </div>
        </div>
    );
}
