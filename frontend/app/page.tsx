'use client';
import { useState, useEffect } from 'react';
import OrbCore from '@/components/cockpit/OrbCore';
import HudRing from '@/components/cockpit/HudRing';
import FuiPanel from '@/components/cockpit/FuiPanel';
import { useVoice } from '@/hooks/useVoice';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Zap, Cpu, Shield, Activity, 
  Database, Eye, MessageSquare, 
  Terminal as TerminalIcon 
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
    <main className="min-h-screen w-full bg-[#02040a] text-cyan-400 overflow-hidden relative perspective-container scanlines">
      {/* Camadas Decorativas */}
      <div className="absolute inset-0 hexagon-grid opacity-10" />
      
      {/* INTERFACE DO COCKPIT */}
      <div className="relative z-10 h-screen flex flex-col p-6 space-y-6">
        
        {/* SECTION: TOP BAR (System Diagnostics) */}
        <div className="flex justify-between items-start">
          <FuiPanel className="flex items-center gap-6 px-6 py-2">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-cyan-500" />
              <span className="text-[10px] font-black tracking-widest uppercase">Encryption Active</span>
            </div>
            <div className="w-[1px] h-4 bg-cyan-500/20" />
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-500" />
              <span className="text-[10px] font-black tracking-widest uppercase">Core Load: 12.4%</span>
            </div>
          </FuiPanel>

          <div className="flex flex-col items-end">
            <h1 className="text-xl font-black tracking-[0.5em] text-glow-cyan uppercase">JARVIS 5.0</h1>
            <span className="text-[8px] text-cyan-500/40 tracking-[0.2em]">AUTONOMOUS INTELLIGENCE INTERFACE</span>
          </div>
        </div>

        {/* SECTION: MAIN CONTENT (Asymmetric Layout) */}
        <div className="flex-1 grid grid-cols-12 gap-6 items-center">
          
          {/* LEFT COLUMN: Data & Knowledge */}
          <div className="col-span-3 space-y-6 h-full flex flex-col justify-center">
            <FuiPanel title="Neural Network" side="left">
              <div className="space-y-4 py-2">
                {[
                  { label: 'Synaptic Link', val: '98%', color: 'bg-cyan-500' },
                  { label: 'Pattern Recog', val: 'Active', color: 'bg-emerald-500' },
                  { label: 'Latency', val: '0.04ms', color: 'bg-cyan-500' }
                ].map((item) => (
                  <div key={item.label} className="space-y-1">
                    <div className="flex justify-between text-[8px] uppercase tracking-wider font-bold">
                      <span>{item.label}</span>
                      <span>{item.val}</span>
                    </div>
                    <div className="h-[2px] bg-white/5 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: item.val }}
                        className={`h-full ${item.color}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </FuiPanel>

            <FuiPanel title="Obsidian Graph" side="left">
               <div className="h-40 flex items-center justify-center border border-cyan-500/10 rounded bg-black/20 overflow-hidden relative">
                  <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle,var(--jarvis-cyan)_1px,transparent_1px)] bg-[size:10px_10px]" />
                  <Database className="w-8 h-8 text-cyan-500/20 animate-pulse" />
                  <span className="absolute bottom-2 text-[8px] text-cyan-500/40 uppercase">Mapping Knowledge...</span>
               </div>
            </FuiPanel>
          </div>

          {/* CENTER: THE ORB (Core) */}
          <div className="col-span-6 flex flex-col items-center justify-center relative">
             <div 
              className="relative cursor-pointer group transform hover:scale-105 transition-transform duration-500"
              onClick={startListening}
             >
                <HudRing status={status} />
                <OrbCore status={status} />
                
                {/* Status Indicator Orbiting */}
                <motion.div 
                  className="absolute -inset-10 border border-cyan-500/10 rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
                >
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 px-2 py-1 bg-cyan-500/10 backdrop-blur-md border border-cyan-500/30 rounded text-[8px] font-black uppercase">
                    Core {status}
                  </div>
                </motion.div>
             </div>
          </div>

          {/* RIGHT COLUMN: Perception & Feedback */}
          <div className="col-span-3 space-y-6 h-full flex flex-col justify-center">
            <FuiPanel title="Visual Perception" side="right">
               <div className="h-40 rounded border border-cyan-500/20 bg-black/40 flex flex-col items-center justify-center relative overflow-hidden">
                  <Eye className="w-10 h-10 text-cyan-500/30 mb-2" />
                  <div className="absolute inset-0 border border-cyan-500/10 flex items-center justify-center">
                     <div className="w-full h-[1px] bg-cyan-500/10 animate-scanline" />
                  </div>
                  <span className="text-[8px] text-cyan-500/40 uppercase font-mono">Tracking Active</span>
               </div>
            </FuiPanel>

            <FuiPanel title="System Logs" side="right">
               <div className="font-mono text-[9px] text-cyan-500/60 space-y-1 h-32 overflow-hidden">
                  <p className="text-cyan-400">[0.001] BOOT SEQUENCE START</p>
                  <p>[0.042] NEURAL LINK ESTABLISHED</p>
                  <p>[0.129] PERCEPTION ENGINE ONLINE</p>
                  <p>[0.215] OBSIDIAN GRAPH SYNCED</p>
                  <p className="animate-pulse text-white">{"> "} LISTENING FOR INPUT...</p>
               </div>
            </FuiPanel>
          </div>
        </div>

        {/* SECTION: FOOTER (Voice Interaction) */}
        <div className="h-32 grid grid-cols-12 gap-6 items-end">
           <FuiPanel className="col-start-4 col-span-6 min-h-[80px] flex flex-col justify-center items-center relative overflow-hidden">
              <AnimatePresence mode="wait">
                {transcript ? (
                  <motion.div 
                    key="voice"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="flex flex-col items-center"
                  >
                    <div className="flex items-center gap-2 mb-1">
                       <MessageSquare className="w-3 h-3 text-cyan-500" />
                       <span className="text-[8px] font-black uppercase tracking-widest text-cyan-500/60">Voice Command</span>
                    </div>
                    <p className="text-lg font-black italic text-white text-center leading-tight">
                      "{transcript}"
                    </p>
                  </motion.div>
                ) : (
                  <div className="flex flex-col items-center text-cyan-500/20 animate-pulse">
                     <Zap className="w-6 h-6 mb-2" />
                     <span className="text-[10px] font-black uppercase tracking-[0.4em]">Awaiting Authorization</span>
                  </div>
                )}
              </AnimatePresence>
              
              {/* Audio Wave Sim (Fake) */}
              <div className="absolute bottom-0 left-0 right-0 h-1 flex items-end gap-[1px]">
                 {[...Array(60)].map((_, i) => (
                   <motion.div 
                    key={i}
                    animate={{ 
                      height: status === 'speaking' || status === 'listening' 
                        ? Math.random() * 100 + '%' 
                        : '2px' 
                    }}
                    className="flex-1 bg-cyan-500/30"
                   />
                 ))}
              </div>
           </FuiPanel>
        </div>

      </div>

      {/* Decorative Overlays */}
      <div className="absolute top-0 right-0 p-12 pointer-events-none opacity-20">
         <TerminalIcon className="w-32 h-32 text-cyan-500" />
      </div>
      
    </main>
  );
}
