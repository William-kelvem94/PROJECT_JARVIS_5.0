'use client';
import { useState, useEffect } from 'react';
import OrbCore from '@/components/cockpit/OrbCore';
import HudRing from '@/components/cockpit/HudRing';
import { useVoice } from '@/hooks/useVoice';

export default function Home() {
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  const { isListening, transcript, response, speak, startListening } = useVoice();

  // Simulação de fluxo para demonstração
  useEffect(() => {
    if (isListening) {
      setStatus('listening');
    } else if (transcript && !response) {
      setStatus('thinking');
    } else if (response) {
      setStatus('speaking');
    } else {
      setStatus('idle');
    }
  }, [isListening, transcript, response]);

  return (
    <main className="min-h-screen bg-black text-cyan-300 flex flex-col items-center justify-center overflow-hidden relative font-mono">
      {/* Background Holográfico Profundo */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#0a1a2a_0%,#000000_100%)] opacity-80" />
      
      {/* Grade de fundo estilo Tron */}
      <div className="absolute inset-0 bg-grid-slate-900/[0.04] bg-[bottom_1px_center] border-b border-slate-900/[0.06] opacity-20" />
      
      <div className="relative z-10 flex flex-col items-center">
        {/* Container do HUD Central */}
        <div className="relative w-[400px] h-[400px] flex items-center justify-center cursor-pointer" onClick={startListening}>
          <HudRing status={status} />
          <OrbCore status={status} />
        </div>
        
        {/* Painel de Status e Texto */}
        <div className="mt-16 max-w-2xl w-full px-6 space-y-6 text-center">
          <div className="flex flex-col items-center space-y-2">
            <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full animate-pulse ${
                    status === 'listening' ? 'bg-green-400' : 
                    status === 'thinking' ? 'bg-pink-500' : 
                    status === 'speaking' ? 'bg-yellow-400' : 'bg-cyan-400'
                }`} />
                <h2 className="text-sm font-bold tracking-[0.3em] uppercase opacity-70">
                    Sytem State: <span className="text-white">{status}</span>
                </h2>
            </div>
          </div>

          <div className="h-32 flex flex-col justify-center space-y-4">
            {transcript && (
              <div className="animate-in fade-in slide-in-from-bottom-4">
                <p className="text-xs text-cyan-500/60 uppercase mb-1">User Input</p>
                <p className="text-lg text-white font-medium italic">"{transcript}"</p>
              </div>
            )}
            
            {response && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <p className="text-xs text-emerald-500/60 uppercase mb-1">Jarvis Response</p>
                <p className="text-xl text-emerald-400 font-bold tracking-tight">{response}</p>
              </div>
            )}

            {!transcript && !response && (
                <p className="text-sm text-cyan-400/40 animate-pulse uppercase tracking-widest">
                    Aguardando comando de voz...
                </p>
            )}
          </div>
        </div>
      </div>

      {/* Interface Periférica (HUD Estático) */}
      <div className="absolute top-10 left-10 text-[10px] space-y-1 opacity-40">
        <p>COCKPIT_V5.0</p>
        <p>COORD: 23.5505 S, 46.6333 W</p>
        <p>OS: PROJECT_JARVIS_6.1</p>
      </div>

      <div className="absolute bottom-10 right-10 text-[10px] space-y-1 opacity-40 text-right">
        <p>POWER: STABLE</p>
        <p>NETWORK: LOCAL_HOST_8000</p>
        <p>LATENCY: 14MS</p>
      </div>
    </main>
  );
}
