'use client';
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';

type Status = 'idle' | 'listening' | 'thinking' | 'speaking';

export default function OrbCore({ status = 'idle' }: { status: Status }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let particles: any[] = [];
    let frame = 0;

    class Particle {
      x: number; y: number; size: number; speed: number; angle: number; life: number;
      constructor() {
        this.x = canvas.width / 2;
        this.y = canvas.height / 2;
        this.size = Math.random() * 4 + 1;
        this.speed = status === 'thinking' ? Math.random() * 5 + 2 : Math.random() * 2 + 0.5;
        this.angle = Math.random() * Math.PI * 2;
        this.life = 100;
      }
      update() {
        const rad = status === 'listening' ? 1.05 : 1;
        this.x += Math.cos(this.angle) * this.speed * rad;
        this.y += Math.sin(this.angle) * this.speed * rad;
        this.life -= 1;
        this.size *= 0.98;
      }
      draw() {
        ctx.save();
        ctx.globalAlpha = this.life / 100;
        ctx.fillStyle = status === 'speaking' ? '#00f2ff' : status === 'listening' ? '#00ff88' : '#00f2ff';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Camada de "Calor" Central
      const grad = ctx.createRadialGradient(
        canvas.width/2, canvas.height/2, 10,
        canvas.width/2, canvas.height/2, 120
      );
      grad.addColorStop(0, 'rgba(0, 242, 255, 0.4)');
      grad.addColorStop(0.5, 'rgba(0, 242, 255, 0.05)');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Gerar partículas baseado no status
      const spawnRate = status === 'idle' ? 0.2 : 0.8;
      if (Math.random() < spawnRate) particles.push(new Particle());
      
      particles = particles.filter(p => p.life > 0);
      particles.forEach(p => { p.update(); p.draw(); });

      frame = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(frame);
  }, [status]);

  return (
    <motion.div
      className="relative w-[300px] h-[300px] flex items-center justify-center light-projection"
      animate={{ 
        scale: status === 'speaking' ? [1, 1.1, 1] : 1,
        rotate: status === 'thinking' ? 360 : 0
      }}
      transition={{ 
        scale: { duration: 0.4, repeat: Infinity },
        rotate: { duration: 10, repeat: Infinity, ease: 'linear' }
      }}
    >
      <canvas ref={canvasRef} width={400} height={400} className="absolute pointer-events-none" />
      
      {/* O Núcleo Geométrico (Arc Reactor Style) */}
      <div className="relative z-10 w-32 h-32 flex items-center justify-center">
        {/* Anéis Internos */}
        <div className="absolute inset-0 border-4 border-cyan-400/30 rounded-full animate-pulse" />
        <div className="absolute inset-2 border-2 border-dashed border-cyan-400/50 rounded-full animate-spin-slow" />
        
        {/* Triângulos de Foco */}
        {[0, 120, 240].map((angle) => (
          <div 
            key={angle}
            className="absolute w-1 h-6 bg-cyan-400 shadow-[0_0_10px_#00f2ff]"
            style={{ transform: `rotate(${angle}deg) translateY(-40px)` }}
          />
        ))}

        <span className="text-4xl font-black text-cyan-400 drop-shadow-[0_0_15px_rgba(0,242,255,1)]">
          J
        </span>
      </div>
    </motion.div>
  );
}
