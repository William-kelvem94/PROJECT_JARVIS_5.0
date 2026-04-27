'use client';

import { motion } from 'motion/react';

interface HudRingProps {
  label: string;
  value: number;       // 0–100
  color?: string;
  size?: number;
}

export function HudRing({ label, value, color = '#00f2ff', size = 130 }: HudRingProps) {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedValue = Math.min(100, Math.max(0, value));
  const offset = circumference * (1 - clampedValue / 100);

  return (
    <div className="flex flex-col items-center gap-1 select-none">
      <svg width={size} height={size} className="overflow-visible">
        <defs>
          <filter id={`glow-${label}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={8}
        />

        {/* Value arc */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circumference}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          style={{
            rotate: '-90deg',
            transformOrigin: 'center',
            filter: `drop-shadow(0 0 6px ${color})`,
          }}
        />

        {/* Label + value */}
        <text
          x="50%"
          y="48%"
          dominantBaseline="middle"
          textAnchor="middle"
          fontSize="22"
          fontWeight="bold"
          fill="white"
        >
          {Math.round(clampedValue)}
        </text>
        <text
          x="50%"
          y="65%"
          dominantBaseline="middle"
          textAnchor="middle"
          fontSize="10"
          fill="rgba(255,255,255,0.5)"
          letterSpacing="2"
        >
          {label}
        </text>
      </svg>
    </div>
  );
}
