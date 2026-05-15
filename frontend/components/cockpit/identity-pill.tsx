'use client';

import { Frown, Meh, Smile, User, Zap } from 'lucide-react';

const emotionMap: Record<string, { icon: React.ElementType; color: string }> = {
  feliz: { icon: Smile, color: 'text-yellow-400' },
  surpreso: { icon: Zap, color: 'text-cyan-400' },
  neutro: { icon: Meh, color: 'text-white/60' },
  triste: { icon: Frown, color: 'text-blue-400' },
  raiva: { icon: Frown, color: 'text-red-400' },
};

interface IdentityPillProps {
  name: string;
  emotion: string;
}

export function IdentityPill({ name, emotion }: IdentityPillProps) {
  const key = emotion.toLowerCase();
  const { icon: Icon, color } = emotionMap[key] ?? { icon: User, color: 'text-white/60' };

  return (
    <div className="flex items-center gap-3 rounded-full border border-cyan-500/30 bg-white/5 px-5 py-2 backdrop-blur-sm">
      <Icon className={`h-5 w-5 ${color}`} />
      <span className="text-sm font-medium tracking-wide">{name}</span>
      <span className={`text-xs tracking-widest uppercase ${color}`}>{emotion}</span>
    </div>
  );
}
