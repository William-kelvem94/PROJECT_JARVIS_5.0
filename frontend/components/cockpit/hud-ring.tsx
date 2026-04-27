'use client';

import { motion } from 'motion/react';

interface HudRingProps {
  value: number;
  label: string;
  color: string;
}

export function HudRing({ value, label, color }: HudRingProps) {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const clampedValue = Math.min(100, Math.max(0, value));
  const offset = circumference - (clampedValue / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="80" height="80" viewBox="0 0 80 80" aria-label={`${label}: ${clampedValue}%`}>
        {/* Track */}
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="4"
        />
        {/* Progress */}
        <motion.circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          transform="rotate(-90 40 40)"
          style={{ filter: `drop-shadow(0 0 4px ${color})` }}
        />
        {/* Label text */}
        <text
          x="40"
          y="40"
          textAnchor="middle"
          dominantBaseline="central"
          fill="white"
          fontSize="12"
          fontFamily="monospace"
          fontWeight="600"
        >
          {clampedValue}%
        </text>
      </svg>
      <span className="text-xs text-white/50 font-mono tracking-widest uppercase">{label}</span>
    </div>
  );
}
