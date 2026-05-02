'use client';
import { motion } from 'framer-motion';

export default function HudRing({ status }: { status: 'idle' | 'listening' | 'thinking' | 'speaking' }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      {/* Anel de Rotação Lenta */}
      <motion.div
        className="absolute w-[300px] h-[300px] border border-cyan-500/20 rounded-full"
        style={{ borderStyle: 'dashed', borderDasharray: '10 20' }}
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />
      
      {/* Anel de Rotação Rápida (Ativo em Listening) */}
      <motion.div
        className="absolute w-[280px] h-[280px] border-t-2 border-b-2 border-cyan-400/40 rounded-full"
        animate={{ 
            rotate: status === 'listening' ? -360 : -180,
            scale: status === 'speaking' ? 1.05 : 1
        }}
        transition={{ 
            rotate: { duration: status === 'listening' ? 2 : 10, repeat: Infinity, ease: 'linear' },
            scale: { duration: 0.5 }
        }}
      />

      {/* Elementos Decorativos Orbitais */}
      {[0, 90, 180, 270].map((angle) => (
        <motion.div
          key={angle}
          className="absolute w-2 h-8 bg-cyan-400/30"
          style={{ 
            transform: `rotate(${angle}deg) translateY(-160px)`,
            borderRadius: '2px'
          }}
          animate={{ opacity: status === 'thinking' ? [0.2, 1, 0.2] : 0.4 }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      ))}
    </div>
  );
}
