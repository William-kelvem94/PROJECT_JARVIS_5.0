'use client';

<<<<<<< HEAD
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
=======
import { Smile, Zap, Meh, Frown, User } from 'lucide-react';

const emotionMap: Record<string, { icon: React.ElementType; color: string }> = {
  feliz:    { icon: Smile, color: 'text-yellow-400' },
  surpreso: { icon: Zap,   color: 'text-jarvis-cyan' },
  neutro:   { icon: Meh,   color: 'text-white/60' },
  triste:   { icon: Frown, color: 'text-blue-400' },
  raiva:    { icon: Frown, color: 'text-red-400' },
>>>>>>> main
};

interface IdentityPillProps {
  name: string;
  emotion: string;
}

export function IdentityPill({ name, emotion }: IdentityPillProps) {
<<<<<<< HEAD
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
=======
  const key = emotion.toLowerCase();
  const { icon: Icon, color } = emotionMap[key] ?? { icon: User, color: 'text-white/60' };

  return (
    <div className="flex items-center gap-3 px-5 py-2 rounded-full border border-jarvis-cyan/30 bg-white/5 backdrop-blur-sm">
      <Icon className={`w-5 h-5 ${color}`} />
      <span className="text-sm font-medium tracking-wide">{name}</span>
      <span className={`text-xs uppercase tracking-widest ${color}`}>{emotion}</span>
>>>>>>> main
    </div>
  );
}
