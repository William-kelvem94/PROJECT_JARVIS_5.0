'use client';
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';

interface OrbCoreProps {
  status: 'idle' | 'listening' | 'thinking' | 'speaking';
}

export default function OrbCore({ status }: OrbCoreProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const canvasW = canvas.width;
    const canvasH = canvas.height;
    
    let particles: Particle[] = [];
    let animationFrame: number;

    class Particle {
      x: number; y: number; size: number; speed: number; angle: number;
      constructor() {
        this.x = centerX;
        this.y = centerY;
        this.size = Math.random() * 4 + 1;
        this.speed = Math.random() * 2 + 0.5;
        this.angle = Math.random() * Math.PI * 2;
      }
      update() {
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;
        this.size *= 0.98;
      }
      draw(context: CanvasRenderingContext2D) {
        context.save();
        context.globalAlpha = this.size / 5;
        context.fillStyle = status === 'speaking' ? '#ffff00' : 
                        status === 'listening' ? '#00ff88' :
                        status === 'thinking' ? '#ff00aa' : '#00f0ff';
        context.fillRect(this.x, this.y, this.size, this.size);
        context.restore();
      }
    }

    const animate = () => {
      if (!ctx) return;
      ctx.clearRect(0, 0, canvasW, canvasH);
      
      const glowColor = status === 'speaking' ? '#ffff00' : 
                        status === 'listening' ? '#00ff88' :
                        status === 'thinking' ? '#ff00aa' : '#00f0ff';

      // Glow central
      const gradient = ctx.createRadialGradient(centerX, centerY, 20, centerX, centerY, 120);
      gradient.addColorStop(0, glowColor + '88');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvasW, canvasH);

      // Particulas
      if (Math.random() < 0.6) particles.push(new Particle());
      particles = particles.filter(p => p.size > 0.3);
      particles.forEach(p => { 
        p.update(); 
        p.draw(ctx); 
      });

      // Anel Giratorio
      ctx.strokeStyle = glowColor + '33';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(centerX, centerY, 80 + Math.sin(Date.now()/500) * 5, 0, Math.PI * 2);
      ctx.stroke();

      animationFrame = requestAnimationFrame(animate);
    };

    animate();

    return () => cancelAnimationFrame(animationFrame);
  }, [status]);

  const colors = {
    idle: '#00f0ff',
    listening: '#00ff88',
    thinking: '#ff00aa',
    speaking: '#ffff00',
  };

  return (
    <motion.div
      className="relative w-80 h-80 flex items-center justify-center"
      animate={{ 
          scale: status === 'speaking' ? 1.2 : status === 'listening' ? 1.1 : 1,
          rotate: status === 'thinking' ? 360 : 0
      }}
      transition={{ 
          scale: { duration: 0.4 },
          rotate: { duration: 10, repeat: Infinity, ease: 'linear' }
      }}
    >
      <canvas ref={canvasRef} width={320} height={320} className="absolute" />
      <div 
        className="w-56 h-56 rounded-full flex items-center justify-center text-8xl font-bold relative z-10 backdrop-blur-sm border border-white/10"
        style={{ 
            background: `radial-gradient(circle, ${colors[status]}44 20%, transparent 70%)`,
            boxShadow: `0 0 80px ${colors[status]}44`
        }}
      >
        <span className="text-white drop-shadow-[0_0_20px_rgba(255,255,255,0.8)]">J</span>
      </div>
    </motion.div>
  );
}
