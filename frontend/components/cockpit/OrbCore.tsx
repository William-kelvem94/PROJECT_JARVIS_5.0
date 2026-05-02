'use client';
import { motion } from 'motion/react';

type Status = 'idle' | 'listening' | 'thinking' | 'speaking';

export default function OrbCore({ status = 'idle' }: { status: Status }) {
  const colors = {
    idle: '#00f2ff',
    listening: '#00ff88',
    thinking: '#7000ff',
    speaking: '#ff3e3e',
  };

  const activeColor = colors[status];

  return (
    <div className="relative w-64 h-64 flex items-center justify-center arc-glow">
      {/* Camada 1: Anel Externo Giratório */}
      <motion.div 
        className="absolute inset-0 border-2 border-dashed rounded-full opacity-20"
        style={{ borderColor: activeColor }}
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
      />

      {/* Camada 2: Anel Hexagonal Interno */}
      <motion.div 
        className="absolute inset-4 border border-cyan-500/40 rounded-full"
        animate={{ scale: [1, 1.05, 1], opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: 2, repeat: Infinity }}
      />

      {/* Camada 3: O Núcleo Pulsante */}
      <motion.div 
        className="w-32 h-32 rounded-full flex items-center justify-center relative z-10"
        style={{ 
          background: `radial-gradient(circle, ${activeColor}22 0%, transparent 70%)`,
          boxShadow: `inset 0 0 30px ${activeColor}44, 0 0 50px ${activeColor}22`
        }}
        animate={{ 
          scale: status === 'speaking' ? [1, 1.2, 1] : 1 
        }}
        transition={{ duration: 0.3, repeat: status === 'speaking' ? Infinity : 0 }}
      >
        <span className="text-5xl font-black fui-header" style={{ color: activeColor }}>
          J
        </span>

        {/* Bits Orbitais */}
        {[0, 90, 180, 270].map((angle) => (
           <motion.div 
             key={angle}
             className="absolute w-2 h-2 rounded-sm"
             style={{ 
               backgroundColor: activeColor,
               transform: `rotate(${angle}deg) translateY(-60px)` 
             }}
             animate={{ opacity: [0.2, 1, 0.2] }}
             transition={{ duration: 1, delay: angle/360, repeat: Infinity }}
           />
        ))}
      </motion.div>

      {/* Efeito de Flare */}
      <div className="absolute w-full h-[1px] bg-cyan-400/20 blur-sm" />
      <div className="absolute w-[1px] h-full bg-cyan-400/20 blur-sm" />
    </div>
  );
}
