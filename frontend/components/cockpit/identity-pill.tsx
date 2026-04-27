'use client';

import { Smile, Zap, Meh, Frown, User } from 'lucide-react';

const emotionMap: Record<string, { icon: React.ElementType; color: string }> = {
  feliz:    { icon: Smile, color: 'text-yellow-400' },
  surpreso: { icon: Zap,   color: 'text-jarvis-cyan' },
  neutro:   { icon: Meh,   color: 'text-white/60' },
  triste:   { icon: Frown, color: 'text-blue-400' },
  raiva:    { icon: Frown, color: 'text-red-400' },
};

interface IdentityPillProps {
  name: string;
  emotion: string;
}

export function IdentityPill({ name, emotion }: IdentityPillProps) {
  const key = emotion.toLowerCase();
  const { icon: Icon, color } = emotionMap[key] ?? { icon: User, color: 'text-white/60' };

  return (
    <div className="flex items-center gap-3 px-5 py-2 rounded-full border border-jarvis-cyan/30 bg-white/5 backdrop-blur-sm">
      <Icon className={`w-5 h-5 ${color}`} />
      <span className="text-sm font-medium tracking-wide">{name}</span>
      <span className="text-xs text-white/40 uppercase tracking-widest">{emotion}</span>
    </div>
  );
}
