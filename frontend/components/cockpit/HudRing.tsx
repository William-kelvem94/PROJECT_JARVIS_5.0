'use client';
import { motion } from 'motion/react';

export default function HudRing({ status }: { status: 'idle' | 'listening' | 'thinking' | 'speaking' }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      {/* Anel de Compasso Externo */}
      <motion.div
        className="absolute w-[440px] h-[440px] border border-cyan-500/10 rounded-full flex items-center justify-center"
        animate={{ rotate: 360 }}
        transition={{ duration: 60, repeat: Infinity, ease: 'linear' }}
      >
        {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
          <div 
            key={angle}
            className="absolute h-4 w-[1px] bg-cyan-500/30"
            style={{ transform: `rotate(${angle}deg) translateY(-210px)` }}
          />
        ))}
      </motion.div>

      {/* Anel de Rotação Principal */}
      <motion.div
        className="absolute w-[360px] h-[360px] border-2 border-dashed border-cyan-500/20 rounded-full"
        animate={{ 
          rotate: status === 'listening' ? -360 : 360,
          scale: status === 'speaking' ? 1.05 : 1
        }}
        transition={{ 
          rotate: { duration: 20, repeat: Infinity, ease: 'linear' },
          scale: { duration: 0.5 }
        }}
      />

      {/* Detalhes de "Suporte" da Lente */}
      {[0, 120, 240].map((angle) => (
        <motion.div
          key={angle}
          className="absolute w-1 h-12 bg-cyan-500/40"
          style={{ transform: `rotate(${angle}deg) translateY(-180px)` }}
          animate={{ opacity: status === 'thinking' ? [0.2, 1, 0.2] : 0.6 }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      ))}

      {/* Anel de Varredura de Dados (Scanning) */}
      {status === 'listening' && (
        <motion.div
          className="absolute w-[340px] h-[340px] border-t-2 border-cyan-400 rounded-full"
          initial={{ rotate: 0 }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        />
      )}
    </div>
  );
}
