'use client';
import { useState, useEffect } from 'react';
import OrbCore from '@/components/cockpit/OrbCore';
import HudRing from '@/components/cockpit/HudRing';
import { useVoice } from '@/hooks/useVoice';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Zap, Cpu, Shield, Activity, 
  Database, Eye, MessageSquare 
} from 'lucide-react';

export default function Home() {
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  const { isListening, transcript, response, startListening } = useVoice();

  useEffect(() => {
    if (isListening) setStatus('listening');
    else if (transcript && !response) setStatus('thinking');
    else if (response) setStatus('speaking');
    else setStatus('idle');
  }, [isListening, transcript, response]);

  return (
    <main className="relative h-screen w-screen bg-[#02040a] overflow-hidden">
      <div className="hud-bg" />
      <div className="scanlines" />

      {/* TOP LEFT: System Status */}
      <div className="absolute top-8 left-8 flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <div className="w-1 h-8 bg-cyan-500" />
          <div className="flex flex-col">
            <span className="fui-header text-sm">JARVIS OS V5.3</span>
            <span className="text-[10px] text-cyan-500/40 tracking-widest uppercase font-bold">Terminal Active // Secure Link</span>
          </div>
        </div>
        <div className="flex gap-4 mt-2">
            <div className="flex items-center gap-1 text-[9px] text-cyan-400">
                <Cpu className="w-3 h-3" /> 12.4%
            </div>
            <div className="flex items-center gap-1 text-[9px] text-cyan-400">
                <Shield className="w-3 h-3" /> ONLINE
            </div>
        </div>
      </div>

      {/* TOP RIGHT: Global Telemetry */}
      <div className="absolute top-8 right-8 text-right space-y-1">
        <p className="text-[10px] text-cyan-500/60 font-bold uppercase tracking-tighter">Loc: São Paulo, BR // 23.5505 S</p>
        <p className="fui-header text-xs">PWR: STABLE</p>
        <div className="flex justify-end gap-[1px] h-2 w-24 bg-white/5 mt-1">
            {[...Array(12)].map((_, i) => (
                <div key={i} className={`flex-1 ${i < 8 ? 'bg-cyan-500' : 'bg-white/10'}`} />
            ))}
        </div>
      </div>

      {/* CENTER: CORE INTERFACE */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div 
          className="relative cursor-pointer transition-transform duration-500 hover:scale-105"
          onClick={startListening}
        >
          <HudRing status={status} />
          <OrbCore status={status} />
          
          {/* Status Overlay */}
          <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 flex flex-col items-center">
            <span className="text-[10px] font-black tracking-[0.6em] text-cyan-500 animate-pulse uppercase">
                {status === 'idle' ? 'INITIATE' : status}
            </span>
          </div>
        </div>
      </div>

      {/* BOTTOM LEFT: Knowledge Graph Status */}
      <div className="absolute bottom-8 left-8 w-64 p-4 border border-cyan-500/20 bg-black/40 backdrop-blur-md rounded-sm">
        <div className="flex items-center gap-2 mb-3">
          <Database className="w-4 h-4 text-cyan-500" />
          <span className="text-[10px] font-bold tracking-widest text-cyan-400">SECOND BRAIN</span>
        </div>
        <div className="space-y-2">
            <div className="flex justify-between text-[9px] text-white/40">
                <span>Obsidian Nodes</span>
                <span>1,248</span>
            </div>
            <div className="w-full h-[1px] bg-cyan-500/20" />
            <div className="flex justify-between text-[9px] text-white/40">
                <span>Semantic Links</span>
                <span>8,402</span>
            </div>
        </div>
      </div>

      {/* BOTTOM RIGHT: Interaction & Response */}
      <div className="absolute bottom-8 right-8 w-80 p-5 border-l-4 border-cyan-500 bg-black/60 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-black text-cyan-500 tracking-widest uppercase">Response Stream</span>
          <MessageSquare className="w-4 h-4 text-cyan-500 animate-pulse" />
        </div>
        <p className="text-sm font-bold text-white leading-tight min-h-[40px]">
          {response || "System standing by for vocal authorization..."}
        </p>
      </div>

      {/* CENTER BOTTOM: Transcription Bar */}
      <AnimatePresence>
        {transcript && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-12 left-1/2 -translate-x-1/2 w-full max-w-xl text-center px-10"
          >
            <div className="v-scanner" />
            <p className="text-lg font-black italic tracking-tight text-white uppercase drop-shadow-[0_0_10px_#00f2ff]">
                "{transcript}"
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Screen Edge Decoration */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 h-1 w-64 bg-cyan-500/20 rounded-b-full" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-1 w-32 bg-cyan-500/20 rounded-t-full" />
      
    </main>
  );
}
