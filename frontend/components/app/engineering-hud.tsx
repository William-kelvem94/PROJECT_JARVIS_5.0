'use client';

import React, { useEffect, useState } from 'react';
import {
  Battery,
  BrainCircuit,
  Cpu,
  Fingerprint,
  HardDrive,
  Shield,
  User,
  Zap,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { AppConfig } from '@/app-config';
import { cn } from '@/lib/shadcn/utils';

interface TelemetryData {
  type: string;
  cpu: number;
  ram: number;
  battery: number;
  gpu?: number;
  model: string;
  persona: string;
  // Percepção vinda do perception_manager
  face_emotion?: string;
  face_identity?: string;
  speaker_identity?: string;
  is_reasoning?: boolean;
}

export function EngineeringHUD({ appConfig }: { appConfig: AppConfig }) {
  // const room = useRoomContext();
  const [data, setData] = useState<TelemetryData | null>(null);

  // Conexão com a telemetria em tempo real do Backend
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${appConfig.jarvisApiUrl}/health`);
        const health = await response.json();

        setData(
          (prev) =>
            ({
              ...prev,
              type: 'telemetry_update',
              cpu: health.cpu,
              ram: health.ram,
              battery: prev?.battery || 99,
              model: 'Jarvis Native v5.3',
              persona: 'Engineer Core',
              face_identity: health.face_identity,
              face_emotion: health.face_emotion,
              is_reasoning: health.cpu > 50, // Inteligência visual: se CPU sobe, ele está 'pensando'
            }) as TelemetryData
        );
      } catch {
        console.warn('HUD: Falha ao conectar com telemetria local.');
      }
    };

    const interval = setInterval(fetchStatus, 5000); // Atualiza o HUD a cada 5 segundos
    fetchStatus();

    return () => clearInterval(interval);
  }, [appConfig.jarvisApiUrl]);

  if (!data) return null;

  const getEmotionEmoji = (emotion: string) => {
    const emotions: Record<string, string> = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      neutral: '😐',
      surprised: '😲',
      fearful: '😨',
    };
    return emotions[emotion.toLowerCase()] || '❓';
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 300, opacity: 0 }}
        className="cyber-glass fixed top-1/2 right-6 z-50 w-64 -translate-y-1/2 overflow-hidden rounded-2xl p-1"
      >
        <div className="flex flex-col gap-5 bg-white/5 p-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-2">
            <div className="flex items-center gap-2">
              <Shield className="jarvis-cyan-text size-4" />
              <span className="text-[10px] font-bold tracking-[0.2em] text-white/70 uppercase">
                OS Core 5.0
              </span>
            </div>
            <div className="size-2 animate-pulse rounded-full bg-green-500" />
          </div>

          {/* Hardware Stats */}
          <div className="space-y-4">
            <StatRow icon={<Cpu />} label="CPU" value={data.cpu} />
            <StatRow icon={<HardDrive />} label="RAM" value={data.ram} />
            {data.gpu !== undefined && (
              <StatRow
                icon={<Zap className="text-yellow-400" />}
                label="GPU"
                value={data.gpu}
                color="bg-yellow-400"
              />
            )}
            <StatRow
              icon={<Battery />}
              label="BAT"
              value={data.battery}
              color={data.battery < 20 ? 'bg-red-500' : 'bg-[#1da3b9]'}
            />
          </div>

          {/* Perception Module (The Mastery part) */}
          <div className="mt-2 space-y-3 border-t border-white/10 pt-4">
            <span className="text-[8px] font-bold tracking-[0.3em] text-white/30 uppercase">
              Intelligence Layer
            </span>

            {/* Face Identity */}
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-2 py-1">
              <div className="flex items-center gap-2">
                <User className="size-3 text-white/50" />
                <span className="text-[9px] text-white/70 uppercase">Identify</span>
              </div>
              <span className="jarvis-cyan-text font-mono text-[10px] font-bold tracking-tight uppercase">
                {data.face_identity || 'Unknown'}
              </span>
            </div>

            {/* Emotion */}
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-2 py-1">
              <div className="flex items-center gap-2">
                <Fingerprint className="size-3 text-white/50" />
                <span className="text-[9px] text-white/70 uppercase">Affect</span>
              </div>
              <span className="font-mono text-[10px] font-bold text-violet-400 uppercase">
                {data.face_emotion
                  ? `${getEmotionEmoji(data.face_emotion)} ${data.face_emotion}`
                  : 'Awaiting...'}
              </span>
            </div>

            {/* Neural State */}
            <div className="flex items-center justify-between rounded-lg border border-white/5 bg-white/5 px-2 py-1">
              <div className="flex items-center gap-2">
                <BrainCircuit
                  className={cn(
                    'size-3',
                    data.is_reasoning ? 'animate-pulse text-violet-400' : 'text-white/30'
                  )}
                />
                <span className="text-[9px] text-white/70 uppercase">Neural</span>
              </div>
              <span
                className={cn(
                  'rounded-sm px-2 text-[9px] font-bold',
                  data.is_reasoning ? 'bg-violet-500/20 text-violet-400' : 'text-white/20'
                )}
              >
                {data.is_reasoning ? 'THINKING' : 'IDLE'}
              </span>
            </div>
          </div>

          <div className="mt-1 flex flex-col gap-1 pt-3">
            <div className="flex items-center justify-between text-[8px] tracking-widest text-white/20 uppercase">
              <span>Core Engine</span>
              <span className="text-white/40">{data.model}</span>
            </div>
          </div>
        </div>

        {/* Decorative border */}
        <div className="absolute top-0 right-0 h-16 w-16 rounded-tr-2xl border-t-2 border-r-2 border-[#1da3b9]/20" />
        <div className="absolute bottom-0 left-0 h-12 w-12 rounded-bl-2xl border-b-2 border-l-2 border-[#1da3b9]/10" />
      </motion.div>
    </AnimatePresence>
  );
}

function StatRow({
  icon,
  label,
  value,
  color = 'bg-[#1da3b9]',
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color?: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-[10px]">
        <div className="flex items-center gap-2 text-white/40">
          {React.cloneElement(icon as React.ReactElement<{ className?: string }>, {
            className: 'size-3',
          })}
          <span className="font-mono tracking-tighter">{label}</span>
        </div>
        <span className="font-mono font-bold text-white/80">{value.toFixed(0)}%</span>
      </div>
      <div className="h-0.5 w-full overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          className={cn('h-full', color, 'shadow-[0_0_8px_currentColor]')}
        />
      </div>
    </div>
  );
}
