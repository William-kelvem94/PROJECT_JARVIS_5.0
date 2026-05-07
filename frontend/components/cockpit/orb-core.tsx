'use client';
import { motion } from 'motion/react';

type Status = 'idle' | 'listening' | 'thinking' | 'speaking';

export default function OrbCore({ status = 'idle' }: { status: Status }) {
  const colors = {
    idle: '#00f2ff',      // Ciano
    listening: '#ffffff', // Branco Brilhante
    thinking: '#7000ff',  // Roxo
    speaking: '#ffcc00',  // Amarelo/Dourado
  };

  const activeColor = colors[status];

  // Configurações de animação baseadas no estado cognitivo
  const animations = {
    idle: {
      core: { scale: [1, 1.05, 1], opacity: [0.8, 1, 0.8] },
      glow: { scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] },
      rotate: 0
    },
    listening: {
      core: { scale: [1, 1.1, 1], x: [-1, 1, -1] },
      glow: { scale: [1.2, 1.4, 1.2], opacity: [0.5, 0.8, 0.5] },
      rotate: 0
    },
    thinking: {
      core: { scale: [1, 0.9, 1] },
      glow: { scale: [1.1, 1.3, 1.1], opacity: [0.4, 0.7, 0.4] },
      rotate: 360
    },
    speaking: {
      core: { scale: [1, 1.2, 1] },
      glow: { scale: [1, 1.5, 1], opacity: [0.4, 0.9, 0.4] },
      rotate: 0
    },
  };

  const currentAnim = animations[status];

  return (
    <div className="relative w-64 h-64 flex items-center justify-center">
      {/* Aura de Energia (Glow) */}
      <motion.div
        className="absolute w-full h-full rounded-full blur-3xl opacity-40"
        style={{ backgroundColor: activeColor }}
        animate={currentAnim.glow}
        transition={{ duration: status === 'speaking' ? 0.3 : 2, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Anéis de Profundidade (Z-Axis) */}
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full border-[1px] opacity-20"
          style={{
            width: `${100 + i * 20}%`,
            height: `${100 + i * 20}%`,
            borderColor: activeColor
          }}
          animate={{ rotate: i % 2 === 0 ? 360 : -360 }}
          transition={{ duration: 10 + i * 5, repeat: Infinity, ease: 'linear' }}
        />
      ))}

      {/* O Núcleo Sólido */}
      <motion.div
        className="w-28 h-28 rounded-full border-[2px] flex items-center justify-center relative z-10 bg-black/60 backdrop-blur-md"
        style={{
            borderColor: activeColor,
            boxShadow: `0 0 30px ${activeColor}44, inset 0 0 20px ${activeColor}44`
        }}
        animate={{
            scale: currentAnim.core.scale,
            x: 'x' in currentAnim.core ? currentAnim.core.x : 0,
            rotate: currentAnim.rotate
        }}
        transition={{
            scale: { duration: status === 'speaking' ? 0.2 : 2, repeat: Infinity, ease: "easeInOut" },
            x: { duration: 0.1, repeat: Infinity },
            rotate: { duration: status === 'thinking' ? 2 : 20, repeat: Infinity, ease: 'linear' }
        }}
      >
        <span
            className="text-5xl font-bold font-sans tracking-tighter"
            style={{
                color: activeColor,
                textShadow: `0 0 15px ${activeColor}`
            }}
        >
          J
        </span>
      </motion.div>
    </div>
  );
}
