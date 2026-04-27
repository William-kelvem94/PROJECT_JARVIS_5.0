'use client';

import React, { useEffect, useState } from 'react';
import {
  BatteryHigh,
  Brain,
  Cpu,
  Fingerprint,
  HardDrive,
  ShieldCheck,
  UserFocus,
  Lightning,
  Pulse,
} from '@phosphor-icons/react';
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
  face_emotion?: string;
  face_identity?: string;
  speaker_identity?: string;
  is_reasoning?: boolean;
}

export function EngineeringHUD({ appConfig }: { appConfig: AppConfig }) {
  const [data, setData] = useState<TelemetryData | null>(null);

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
              is_reasoning: health.cpu > 50,
            }) as TelemetryData
        );
      } catch {
        // Fallback para demonstração se o backend estiver offline
        setData((prev) => prev || {
          type: 'telemetry_update',
          cpu: 12,
          ram: 45,
          battery: 99,
          model: 'Jarvis Offline Mode',
          persona: 'Emergency Core',
          face_identity: 'Unauthorized',
          face_emotion: 'Neutral',
          is_reasoning: false
        });
      }
    };

    const interval = setInterval(fetchStatus, 5000);
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
        className="cyber-glass fixed top-1/2 right-6 z-50 w-72 -translate-y-1/2 rounded-2xl p-0.5"
      >
        <div className="flex flex-col gap-6 bg-black/40 backdrop-blur-xl p-5">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <ShieldCheck weight="duotone" className="text-jarvis-cyan size-5" />
                <motion.div 
                  animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="absolute inset-0 rounded-full bg-jarvis-cyan/30"
                />
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] font-bold tracking-[0.2em] text-white/90 uppercase font-mono">
                  OS Core 5.0
                </span>
                <span className="text-[7px] tracking-[0.1em] text-jarvis-cyan/50 font-mono uppercase">
                  Secure Link Active
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Pulse className="size-3 text-jarvis-cyan animate-pulse" />
              <div className="size-1.5 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e]" />
            </div>
          </div>

          {/* Hardware Stats */}
          <div className="space-y-5">
            <StatRow icon={<Cpu weight="duotone" />} label="Processador" value={data.cpu} />
            <StatRow icon={<HardDrive weight="duotone" />} label="Memória" value={data.ram} />
            <StatRow
              icon={<BatteryHigh weight="duotone" />}
              label="Energia"
              value={data.battery}
              color={data.battery < 20 ? 'bg-red-500' : 'bg-jarvis-cyan'}
            />
          </div>

          {/* Perception Module */}
          <div className="mt-2 space-y-3 border-t border-white/5 pt-5">
            <div className="flex items-center justify-between">
              <span className="text-[8px] font-bold tracking-[0.3em] text-white/30 uppercase font-mono">
                Neural Perception
              </span>
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              >
                <Brain weight="thin" className="size-3 text-white/20" />
              </motion.div>
            </div>

            <div className="grid gap-2">
              <HudInfoBox 
                icon={<UserFocus weight="duotone" />} 
                label="Identidade" 
                value={data.face_identity || 'Aguardando...'} 
                active={!!data.face_identity}
              />
              <HudInfoBox 
                icon={<Fingerprint weight="duotone" />} 
                label="Afetividade" 
                value={data.face_emotion ? `${getEmotionEmoji(data.face_emotion)} ${data.face_emotion}` : 'Estável'} 
                active={!!data.face_emotion}
                color="text-jarvis-violet"
              />
              <HudInfoBox 
                icon={<Lightning weight="duotone" />} 
                label="Estado" 
                value={data.is_reasoning ? 'PENSANDO' : 'OCIOSO'} 
                active={data.is_reasoning}
                color="text-amber-400"
                pulse={data.is_reasoning}
              />
            </div>
          </div>

          {/* Footer Info */}
          <div className="mt-2 flex flex-col gap-1 border-t border-white/5 pt-4">
            <div className="flex items-center justify-between font-mono text-[7px] tracking-widest text-white/20 uppercase">
              <span>Engine Status</span>
              <span className="text-jarvis-cyan/40">Synchronized</span>
            </div>
            <div className="flex items-center justify-between font-mono text-[7px] tracking-widest text-white/20 uppercase">
              <span>Model Vers</span>
              <span className="text-white/40">{data.model}</span>
            </div>
          </div>
        </div>

        {/* Decorative HUD Elements */}
        <div className="absolute -top-1 -right-1 size-8 border-t-2 border-r-2 border-jarvis-cyan/30 rounded-tr-xl" />
        <div className="absolute -bottom-1 -left-1 size-8 border-b-2 border-l-2 border-jarvis-cyan/20 rounded-bl-xl" />
      </motion.div>
    </AnimatePresence>
  );
}

function HudInfoBox({ icon, label, value, active, color = "text-jarvis-cyan", pulse }: { 
  icon: React.ReactNode, 
  label: string, 
  value: string, 
  active?: boolean,
  color?: string,
  pulse?: boolean
}) {
  return (
    <div className={cn(
      "flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.03] px-3 py-2 transition-all",
      active ? "border-white/10 bg-white/[0.05]" : "opacity-50"
    )}>
      <div className="flex items-center gap-2.5">
        <div className={cn("size-4 transition-colors", active ? "text-white/70" : "text-white/20")}>
          {icon}
        </div>
        <span className="text-[9px] text-white/40 uppercase font-mono tracking-tight">{label}</span>
      </div>
      <span className={cn(
        "font-mono text-[10px] font-bold tracking-tight uppercase",
        active ? color : "text-white/20",
        pulse && "animate-pulse"
      )}>
        {value}
      </span>
    </div>
  );
}

function StatRow({
  icon,
  label,
  value,
  color = 'bg-jarvis-cyan',
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color?: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-[10px]">
        <div className="flex items-center gap-2 text-white/50">
          <div className="size-3.5 text-jarvis-cyan/70">
            {icon}
          </div>
          <span className="font-mono tracking-wider uppercase text-[9px]">{label}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="font-mono font-bold text-white/90">{value.toFixed(0)}</span>
          <span className="text-[8px] text-white/30">%</span>
        </div>
      </div>
      <div className="relative h-1 w-full overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={cn('h-full', color, 'shadow-[0_0_10px_currentColor]')}
        />
        {/* Glow effect on the bar */}
        <motion.div 
          animate={{ x: ['-100%', '200%'] }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          className="absolute inset-y-0 w-1/2 bg-linear-to-r from-transparent via-white/20 to-transparent"
        />
      </div>
    </div>
  );
}
