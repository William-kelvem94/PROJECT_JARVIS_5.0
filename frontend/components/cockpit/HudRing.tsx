'use client';
import { motion } from 'motion/react';

export default function HudRing({ status }: { status: 'idle' | 'listening' | 'thinking' | 'speaking' }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none scale-75 lg:scale-100">
      {/* Anel de Compasso Ultra-Fino */}
      <motion.div
        className="absolute w-[500px] h-[500px] border border-cyan-500/10 rounded-full"
        animate={{ rotate: -360 }}
        transition={{ duration: 100, repeat: Infinity, ease: 'linear' }}
      >
        {[...Array(12)].map((_, i) => (
          <div 
            key={i}
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[1px] h-3 bg-cyan-500/20"
            style={{ transform: `rotate(${i * 30}deg) translateY(-250px)` }}
          />
        ))}
      </motion.div>

      {/* Anel de Status Dinâmico */}
      <motion.div
        className="absolute w-[400px] h-[400px] border-t-2 border-b-2 border-cyan-400/30 rounded-full"
        animate={{ 
          rotate: status === 'listening' ? 360 : 0,
          scale: status === 'speaking' ? 1.1 : 1
        }}
        transition={{ 
          rotate: { duration: 2, repeat: Infinity, ease: 'linear' },
          scale: { duration: 0.5 }
        }}
      />

      {/* Crosshair Central */}
      <div className="absolute w-40 h-[1px] bg-cyan-500/10" />
      <div className="absolute h-40 w-[1px] bg-cyan-500/10" />
    </div>
  );
}
