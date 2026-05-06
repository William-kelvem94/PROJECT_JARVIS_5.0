'use client';
import { motion } from 'motion/react';

export default function HudRing({ status }: { status: 'idle' | 'listening' | 'thinking' | 'speaking' }) {
  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">

      {/* Anel Externo Fino */}
      <motion.div
        className="w-64 h-64 border-[1px] border-cyan-500/30 rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
      >
        <div className="w-full h-full relative">
            <div className="absolute top-0 left-1/2 w-[2px] h-3 bg-cyan-400" />
            <div className="absolute bottom-0 left-1/2 w-[2px] h-3 bg-cyan-400" />
            <div className="absolute left-0 top-1/2 w-3 h-[2px] bg-cyan-400" />
            <div className="absolute right-0 top-1/2 w-3 h-[2px] bg-cyan-400" />
        </div>
      </motion.div>

      {/* Anel Interno Tracejado (Veloz) */}
      <motion.div
        className="absolute w-56 h-56 border-t-2 border-r-2 border-cyan-400/50 rounded-full"
        animate={{
            rotate: status === 'listening' ? -360 : 360,
            scale: status === 'speaking' ? 1.05 : 1
        }}
        transition={{
            rotate: { duration: status === 'listening' ? 1 : 10, repeat: Infinity, ease: 'linear' },
            scale: { duration: 0.3 }
        }}
      />

    </div>
  );
}
