'use client';

import { motion } from 'motion/react';

export default function HudRing({
  status,
}: {
  status: 'idle' | 'listening' | 'thinking' | 'speaking';
}) {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
      {/* Anel Externo Fino */}
      <motion.div
        className="h-64 w-64 rounded-full border-[1px] border-cyan-500/30"
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      >
        <div className="relative h-full w-full">
          <div className="absolute top-0 left-1/2 h-3 w-[2px] bg-cyan-400" />
          <div className="absolute bottom-0 left-1/2 h-3 w-[2px] bg-cyan-400" />
          <div className="absolute top-1/2 left-0 h-[2px] w-3 bg-cyan-400" />
          <div className="absolute top-1/2 right-0 h-[2px] w-3 bg-cyan-400" />
        </div>
      </motion.div>

      {/* Anel Interno Tracejado (Veloz) */}
      <motion.div
        className="absolute h-56 w-56 rounded-full border-t-2 border-r-2 border-cyan-400/50"
        animate={{
          rotate: status === 'listening' ? -360 : 360,
          scale: status === 'speaking' ? 1.05 : 1,
        }}
        transition={{
          rotate: { duration: status === 'listening' ? 1 : 10, repeat: Infinity, ease: 'linear' },
          scale: { duration: 0.3 },
        }}
      />
    </div>
  );
}
