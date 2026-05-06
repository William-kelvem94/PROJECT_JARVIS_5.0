'use client';
import { motion } from 'motion/react';
import { ReactNode } from 'react';

interface FuiPanelProps {
  title?: string;
  children: ReactNode;
  className?: string;
  side?: 'left' | 'right' | 'top' | 'bottom';
}

export default function FuiPanel({ title, children, className = "", side }: FuiPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, x: side === 'left' ? -20 : side === 'right' ? 20 : 0 }}
      animate={{ opacity: 1, scale: 1, x: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`fui-panel fui-border-glow p-4 relative group ${className}`}
    >
      {/* Corner Accents */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-cyan-400" />
      <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-cyan-400" />
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-cyan-400" />
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-cyan-400" />

      {title && (
        <div className="flex items-center gap-2 mb-3 border-b border-cyan-500/20 pb-1">
          <div className="w-1 h-3 bg-cyan-400" />
          <span className="text-[10px] font-black tracking-[0.3em] uppercase text-cyan-400/80">
            {title}
          </span>
        </div>
      )}

      <div className="relative z-10">
        {children}
      </div>

      {/* Decorative Data Strip */}
      <div className="absolute -right-1 top-1/4 h-1/2 w-[1px] bg-cyan-400/30" />
    </motion.div>
  );
}
