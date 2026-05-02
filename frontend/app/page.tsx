'use client';
import { useState, useEffect } from 'react';
import OrbCore from '@/components/cockpit/OrbCore';
import HudRing from '@/components/cockpit/HudRing';
import { useVoice } from '@/hooks/useVoice';
import { motion, AnimatePresence } from 'motion/react';
import { Shield, Cpu, Database, Eye, MessageSquare } from 'lucide-react';

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
    <main className="h-screen w-screen bg-[#020205] text-[#00f2ff] overflow-hidden flex flex-col p-6 relative font-mono">
      {/* Background Sutil */}
      <div className="absolute inset-0 dot-matrix-bg opacity-30 z-0 pointer-events-none" />

      {/* --- CABEÇALHO --- */}
      <header className="w-full flex justify-between items-start z-10">
        <div className="glass-panel p-3 px-6 rounded border-l-4 border-[#00f2ff]">
          <h1 className="text-xl font-bold tracking-widest text-white">JARVIS 5.3</h1>
          <p className="text-xs text-[#00f2ff]/60 uppercase tracking-widest mt-1">Autonomous System Online</p>
        </div>

        <div className="text-right space-y-1">
          <p className="text-xs text-white/50 tracking-widest uppercase">Location: São Paulo, BR</p>
          <div className="flex justify-end items-center gap-3 mt-2">
            <div className="flex items-center gap-1 text-xs">
              <Cpu className="w-4 h-4" /> 12%
            </div>
            <div className="flex items-center gap-1 text-xs">
              <Shield className="w-4 h-4 text-emerald-400" /> OK
            </div>
          </div>
        </div>
      </header>

      {/* --- CORPO PRINCIPAL (GRID 3 COLUNAS) --- */}
      <div className="flex-1 w-full grid grid-cols-3 gap-6 my-6 z-10">
        
        {/* COLUNA ESQUERDA: Telemetria */}
        <div className="flex flex-col justify-center gap-6">
          <div className="glass-panel p-4 rounded border-t-2 border-[#00f2ff]/50">
            <div className="flex items-center gap-2 mb-4 border-b border-[#00f2ff]/20 pb-2">
              <Database className="w-4 h-4" />
              <h2 className="text-xs font-bold tracking-widest uppercase text-white">Neural Network</h2>
            </div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-[10px] mb-1">
                  <span>Synaptic Load</span>
                  <span className="text-white">42%</span>
                </div>
                <div className="w-full h-1 bg-white/10 rounded"><div className="w-[42%] h-full bg-[#00f2ff]" /></div>
              </div>
              <div>
                <div className="flex justify-between text-[10px] mb-1">
                  <span>Memory Core</span>
                  <span className="text-white">Stable</span>
                </div>
                <div className="w-full h-1 bg-white/10 rounded"><div className="w-full h-full bg-[#7000ff]" /></div>
              </div>
            </div>
          </div>
        </div>

        {/* COLUNA CENTRAL: O Núcleo (Orb) */}
        <div className="flex flex-col items-center justify-center relative">
          <div 
            className="relative cursor-pointer group flex items-center justify-center"
            onClick={startListening}
          >
            {/* Sombras de piso */}
            <div className="absolute -bottom-10 w-48 h-8 bg-[#00f2ff]/20 blur-xl rounded-full pointer-events-none" />
            
            <HudRing status={status} />
            <OrbCore status={status} />
          </div>
          
          <div className="mt-12 px-4 py-1 border border-[#00f2ff]/30 bg-[#00f2ff]/10 rounded text-[10px] uppercase tracking-[0.3em]">
            State: <span className="text-white font-bold">{status}</span>
          </div>
        </div>

        {/* COLUNA DIREITA: Percepção e Logs */}
        <div className="flex flex-col justify-center gap-6">
          <div className="glass-panel p-4 rounded border-b-2 border-[#00f2ff]/50">
            <div className="flex items-center gap-2 mb-4 border-b border-[#00f2ff]/20 pb-2">
              <Eye className="w-4 h-4" />
              <h2 className="text-xs font-bold tracking-widest uppercase text-white">System Feed</h2>
            </div>
            <div className="text-[10px] space-y-2 text-white/60">
              <p className="text-[#00f2ff]">[SYSTEM] Boot sequence complete.</p>
              <p>[SENSORS] Camera online.</p>
              <p>[NETWORK] Subsystems linked.</p>
              <p className="animate-pulse text-white mt-4">{">_"} Awaiting input...</p>
            </div>
          </div>
        </div>

      </div>

      {/* --- RODAPÉ: Comando de Voz --- */}
      <footer className="w-full flex flex-col items-center justify-end z-10 min-h-[120px]">
        <AnimatePresence mode="wait">
          {transcript && (
            <motion.div 
              key="transcription"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="text-center mb-4"
            >
              <p className="text-[10px] uppercase tracking-widest text-[#00f2ff]/50 mb-1">User Input</p>
              <p className="text-lg font-bold text-white italic">"{transcript}"</p>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="glass-panel w-full max-w-2xl p-4 rounded-t-xl border-t-2 border-[#7000ff]/50 text-center">
          <div className="flex items-center justify-center gap-2 mb-2 text-[#7000ff]">
            <MessageSquare className="w-4 h-4 animate-pulse" />
            <span className="text-[10px] font-bold tracking-widest uppercase">Response Output</span>
          </div>
          <p className="text-sm text-white font-bold">
            {response || "Standing by."}
          </p>
        </div>
      </footer>

    </main>
  );
}
