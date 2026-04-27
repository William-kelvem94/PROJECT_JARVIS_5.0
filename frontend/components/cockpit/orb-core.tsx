'use client';

import { motion } from 'motion/react';

interface OrbCoreProps {
  thinking?: boolean;
}

export function OrbCore({ thinking = false }: OrbCoreProps) {
  return (
    <div className="relative flex items-center justify-center w-48 h-48 select-none">
      {/* Glow backdrop */}
      <div className="absolute inset-0 rounded-full bg-jarvis-cyan/10 blur-2xl" />

      {/* Orbital rings */}
      {[0, 60, 120].map((angle, i) => (
        <motion.div
          key={i}
          className="absolute inset-4 rounded-full border border-jarvis-cyan/30"
          style={{ rotate: angle }}
          animate={{ rotate: angle + 360 }}
          transition={{ duration: thinking ? 4 + i : 8 + i * 2, repeat: Infinity, ease: 'linear' }}
        />
      ))}

      {/* Sphere */}
      <motion.div
        className="relative z-10 w-28 h-28 rounded-full"
        style={{
          background:
            'radial-gradient(circle at 35% 35%, #00f2ff55, #7000ff88 60%, #020205 100%)',
          boxShadow: thinking
            ? '0 0 60px #00f2ffaa, 0 0 120px #7000ff66'
            : '0 0 40px #00f2ff66, 0 0 80px #7000ff44',
        }}
        animate={{ scale: thinking ? [1, 1.08, 1] : [1, 1.04, 1] }}
        transition={{ duration: thinking ? 1.5 : 3, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  );
}
