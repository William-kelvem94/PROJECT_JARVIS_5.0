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
        this.size = Math.random() * 5 + 2;
        this.speed = Math.random() * 3 + 1;
        this.angle = Math.random() * Math.PI * 2;
        this.life = 80;
      }
      update() {
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;
        this.life--;
        this.size *= 0.97;
      }
      draw() {
        ctx.save();
        ctx.globalAlpha = this.life / 80;
        ctx.fillStyle = status === 'speaking' ? '#ffff00' : '#00f0ff';
        ctx.shadowBlur = 20;
        ctx.shadowColor = status === 'speaking' ? '#ffff00' : '#00f0ff';
        ctx.fillRect(this.x, this.y, this.size, this.size);
        ctx.restore();
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Glow central forte
      const grad = ctx.createRadialGradient(
        canvas.width/2, canvas.height/2, 30,
        canvas.width/2, canvas.height/2, 140
      );
      grad.addColorStop(0, status === 'speaking' ? '#ffff0088' : '#00f0ff88');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Partículas
      if (Math.random() < 0.8) particles.push(new Particle());
      particles = particles.filter(p => p.life > 0);
      particles.forEach(p => { p.update(); p.draw(); });

      frame = requestAnimationFrame(animate);
    };

    animate();

    return () => cancelAnimationFrame(frame);
  }, [status]);

  const colors = {
    idle: '#00f0ff',
    listening: '#00ff88',
    thinking: '#ff00ff',
    speaking: '#ffff00',
  };

  return (
    <motion.div
      className="relative w-96 h-96 flex items-center justify-center"
      animate={{ scale: status === 'speaking' ? 1.15 : 1 }}
      transition={{ duration: 0.6, repeatType: 'reverse' }}
    >
      <canvas ref={canvasRef} width={400} height={400} className="absolute" />
      <div 
        className="w-64 h-64 rounded-full flex items-center justify-center text-9xl font-bold relative z-10 neon-text"
        style={{
          background: `radial-gradient(circle, ${colors[status]} 10%, transparent 70%)`,
          boxShadow: `0 0 80px 30px ${colors[status]}`,
        }}
      >
        J
      </div>
    </motion.div>
  );
}
