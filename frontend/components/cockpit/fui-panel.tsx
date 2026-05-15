'use client';

import { ReactNode } from 'react';
import { motion } from 'motion/react';

interface FuiPanelProps {
  title?: string;
  children: ReactNode;
  className?: string;
  side?: 'left' | 'right' | 'top' | 'bottom';
}

export default function FuiPanel({ title, children, className = '', side }: FuiPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, x: side === 'left' ? -20 : side === 'right' ? 20 : 0 }}
      animate={{ opacity: 1, scale: 1, x: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`fui-panel fui-border-glow group relative p-4 ${className}`}
    >
      {/* Corner Accents */}
      <div className="absolute top-0 left-0 h-2 w-2 border-t-2 border-l-2 border-cyan-400" />
      <div className="absolute top-0 right-0 h-2 w-2 border-t-2 border-r-2 border-cyan-400" />
      <div className="absolute bottom-0 left-0 h-2 w-2 border-b-2 border-l-2 border-cyan-400" />
      <div className="absolute right-0 bottom-0 h-2 w-2 border-r-2 border-b-2 border-cyan-400" />

      {title && (
        <div className="mb-3 flex items-center gap-2 border-b border-cyan-500/20 pb-1">
          <div className="h-3 w-1 bg-cyan-400" />
          <span className="text-[10px] font-black tracking-[0.3em] text-cyan-400/80 uppercase">
            {title}
          </span>
        </div>
      )}

      <div className="relative z-10">{children}</div>

      {/* Decorative Data Strip */}
      <div className="absolute top-1/4 -right-1 h-1/2 w-[1px] bg-cyan-400/30" />
    </motion.div>
  );
}
