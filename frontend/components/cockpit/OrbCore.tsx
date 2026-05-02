'use client';
import { motion } from 'motion/react';

type Status = 'idle' | 'listening' | 'thinking' | 'speaking';

export default function OrbCore({ status = 'idle' }: { status: Status }) {
  const colors = {
    idle: '#00f2ff',      // Ciano
    listening: '#00ff88', // Verde
    thinking: '#7000ff',  // Roxo
    speaking: '#ffcc00',  // Amarelo/Dourado
  };

  const activeColor = colors[status];

  return (
    <div className="relative w-48 h-48 flex items-center justify-center">
      {/* O Glow Fundo */}
      <motion.div 
        className="absolute w-full h-full rounded-full blur-2xl opacity-40"
        style={{ backgroundColor: activeColor }}
        animate={{ scale: status === 'speaking' ? [1, 1.2, 1] : 1 }}
        transition={{ duration: 0.5, repeat: Infinity }}
      />

      {/* O Núcleo Sólido */}
      <motion.div 
        className="w-24 h-24 rounded-full border-[1px] flex items-center justify-center relative z-10 bg-black/50 backdrop-blur-sm"
        style={{ 
            borderColor: activeColor,
            boxShadow: `0 0 20px ${activeColor}55, inset 0 0 15px ${activeColor}55`
        }}
        animate={{ 
            scale: status === 'speaking' ? [1, 1.1, 1] : 1,
            rotate: status === 'thinking' ? 360 : 0
        }}
        transition={{ 
            scale: { duration: 0.2, repeat: Infinity },
            rotate: { duration: 3, repeat: Infinity, ease: 'linear' }
        }}
      >
        <span 
            className="text-4xl font-bold font-sans tracking-tighter"
            style={{ 
                color: activeColor, 
                textShadow: `0 0 10px ${activeColor}` 
            }}
        >
          J
        </span>
      </motion.div>
    </div>
  );
}
