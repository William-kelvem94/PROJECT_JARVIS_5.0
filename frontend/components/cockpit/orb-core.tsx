'use client';

import { motion } from 'motion/react';

interface OrbCoreProps {
  thinking: boolean;
}

export function OrbCore({ thinking }: OrbCoreProps) {
  return (
    <div className="relative w-48 h-48 flex items-center justify-center">
      {/* Glow externo pulsante */}
      <motion.div
        className="absolute inset-0 rounded-full"
        style={{
          background:
            'radial-gradient(circle, rgba(0,242,255,0.18) 0%, rgba(112,0,255,0.08) 50%, transparent 70%)',
        }}
        animate={{
          scale: thinking ? [1, 1.18, 1] : [1, 1.06, 1],
          opacity: thinking ? [0.5, 0.9, 0.5] : [0.3, 0.55, 0.3],
        }}
        transition={{
          duration: thinking ? 1.2 : 3.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Anel orbital externo */}
      <motion.div
        className="absolute w-44 h-44 rounded-full border border-cyan-500/20"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />

      {/* Anel orbital interno */}
      <motion.div
        className="absolute w-36 h-36 rounded-full border border-violet-500/20"
        animate={{ rotate: -360 }}
        transition={{ duration: 14, repeat: Infinity, ease: 'linear' }}
      />

      {/* Núcleo da esfera */}
      <motion.div
        className="relative w-32 h-32 rounded-full"
        style={{
          background:
            'radial-gradient(circle at 35% 35%, rgba(0,242,255,0.5) 0%, rgba(112,0,255,0.35) 45%, rgba(0,0,0,0.95) 100%)',
          boxShadow: thinking
            ? '0 0 60px rgba(0,242,255,0.5), 0 0 30px rgba(112,0,255,0.3), inset 0 0 20px rgba(0,242,255,0.15)'
            : '0 0 30px rgba(0,242,255,0.25), inset 0 0 15px rgba(0,242,255,0.08)',
        }}
        animate={{ scale: thinking ? [1, 1.04, 1] : 1 }}
        transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut' }}
      >
        {/* Reflexo interno */}
        <div
          className="absolute top-3 left-4 w-8 h-5 rounded-full opacity-30"
          style={{
            background: 'radial-gradient(ellipse, rgba(255,255,255,0.6), transparent)',
            transform: 'rotate(-30deg)',
          }}
        />
      </motion.div>

      {/* Indicador de estado */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2">
        <motion.div
          className="w-1.5 h-1.5 rounded-full bg-cyan-400"
          animate={{ opacity: thinking ? [1, 0.2, 1] : 1 }}
          transition={{ duration: 0.6, repeat: thinking ? Infinity : 0 }}
        />
      </div>
    </div>
  );
}
