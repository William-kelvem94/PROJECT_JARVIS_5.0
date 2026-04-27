'use client';

import { Smile, Meh, Frown, User, Zap } from 'lucide-react';

type EmotionKey = 'feliz' | 'surpreso' | 'neutro' | 'triste' | 'raiva';

const emotionIcons: Record<EmotionKey, React.ElementType> = {
  feliz: Smile,
  surpreso: Zap,
  neutro: Meh,
  triste: Frown,
  raiva: Frown,
};

const emotionColors: Record<EmotionKey, string> = {
  feliz: 'text-yellow-300',
  surpreso: 'text-purple-300',
  neutro: 'text-cyan-400',
  triste: 'text-blue-300',
  raiva: 'text-red-400',
};

interface IdentityPillProps {
  name: string;
  emotion: string;
}

export function IdentityPill({ name, emotion }: IdentityPillProps) {
  const key = emotion.toLowerCase() as EmotionKey;
  const Icon = emotionIcons[key] ?? User;
  const colorClass = emotionColors[key] ?? 'text-cyan-400';

  return (
    <div className="flex items-center gap-2 bg-white/5 backdrop-blur-sm px-4 py-2 rounded-full border border-white/10">
      <div className="bg-white/10 p-1.5 rounded-full">
        <User className="w-4 h-4 text-white/80" />
      </div>
      <span className="text-sm font-medium text-white">{name}</span>
      <Icon className={`w-4 h-4 ${colorClass}`} />
    </div>
  );
}
