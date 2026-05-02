'use client';
import { useState, useEffect } from 'react';
import OrbCore from '@/components/cockpit/OrbCore';
import HudRing from '@/components/cockpit/HudRing';
import { useVoice } from '@/hooks/useVoice';
import { motion, AnimatePresence } from 'motion/react';

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
    <main className="min-h-screen w-full bg-[#020205] text-cyan-400 overflow-hidden relative">
      {/* Camadas Holográficas de Fundo */}
      <div className="absolute inset-0 hologram-grid opacity-30" />
      <div className="absolute inset-0 hologram-lines opacity-20" />
      <div className="absolute inset-0 scanline" />
      
      {/* HUD PRINCIPAL */}
      <div className="relative z-10 h-screen flex flex-col p-8">
        
        {/* Top Header - Status do Sistema */}
        <div className="flex justify-between items-start">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
              <h1 className="text-sm font-black tracking-[0.4em] uppercase text-glow-cyan">
                JARVIS CORE V6.1
              </h1>
            </div>
            <p className="text-[10px] text-cyan-500/40 font-mono tracking-widest uppercase">
              Secure Local Instance // Authorized Access Only
            </p>
          </div>
          
          <div className="text-right font-mono text-[10px] text-cyan-500/60 uppercase tracking-tighter">
            <p>Lat: 23.5505 S / Long: 46.6333 W</p>
            <p>System Power: Stable</p>
            <p>Uptime: 14:23:09</p>
          </div>
        </div>

        {/* Centro - O Núcleo (ORB) */}
        <div className="flex-1 flex items-center justify-center relative">
          <div 
            className="relative cursor-pointer group"
            onClick={startListening}
          >
            {/* Efeito de Reflexo no Chão */}
            <div className="absolute -bottom-24 left-1/2 -translate-x-1/2 w-64 h-12 bg-cyan-500/10 blur-3xl rounded-full" />
            
            <HudRing status={status} />
            <OrbCore status={status} />
            
            {/* Label Central Flutuante */}
            <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center">
               <span className="text-[10px] font-black tracking-[0.5em] text-white/40 uppercase">
                 {status === 'idle' ? 'Tap to Wake' : status}
               </span>
               <div className="w-12 h-[1px] bg-cyan-500/20 mt-2" />
            </div>
          </div>
        </div>

        {/* Rodapé - Transcrições e Consoles */}
        <div className="grid grid-cols-3 gap-8 items-end">
          
          {/* Esquerda - Telemetria em tempo real */}
          <div className="cyber-glass p-4 rounded-lg space-y-3 border-l-2 border-cyan-500/50">
            <h3 className="text-[10px] font-bold tracking-widest text-white/50 uppercase">Neural Metrics</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-[10px]">
                <span>Synaptic Load</span>
                <span className="text-cyan-300">42.8%</span>
              </div>
              <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="w-[42.8%] h-full bg-cyan-500 shadow-[0_0_8px_var(--jarvis-cyan)]" />
              </div>
              <div className="flex justify-between text-[10px]">
                <span>Memory Cache</span>
                <span className="text-violet-400">Stable</span>
              </div>
            </div>
          </div>

          {/* Centro - Transcrição Principal (Dramática) */}
          <div className="col-span-1 h-32 flex flex-col justify-center px-4">
             <AnimatePresence mode="wait">
               {transcript && (
                 <motion.div 
                   key="transcript"
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   exit={{ opacity: 0 }}
                   className="text-center"
                 >
                   <p className="text-[9px] text-cyan-500/40 uppercase tracking-[0.3em] mb-2">Voice Input</p>
                   <p className="text-lg font-medium text-white italic tracking-tight leading-tight uppercase">
                     "{transcript}"
                   </p>
                 </motion.div>
               )}
             </AnimatePresence>
          </div>

          {/* Direita - Resposta JARVIS */}
          <div className="cyber-glass p-4 rounded-lg border-r-2 border-violet-500/50">
             <div className="flex items-center justify-between mb-2">
               <h3 className="text-[10px] font-bold tracking-widest text-white/50 uppercase">Output Stream</h3>
               <div className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
             </div>
             <p className="text-sm font-bold text-white leading-snug line-clamp-3">
               {response || "System standby. Waiting for vocal authorization..."}
             </p>
          </div>

        </div>

      </div>

      {/* Ornamentos de Canto (HUD Decor) */}
      <div className="absolute top-0 left-0 w-32 h-32 border-t border-l border-cyan-500/20 m-4 rounded-tl-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-32 h-32 border-b border-r border-cyan-500/20 m-4 rounded-br-3xl pointer-events-none" />
      
    </main>
  );
}
