import type { ComponentProps } from 'react';
import dynamic from 'next/dynamic';
import { type MotionProps, motion } from 'motion/react';
import { AppConfig } from '@/app-config';
import type { AgentAudioVisualizerAuraProps } from '@/components/agents-ui/agent-audio-visualizer-aura';
import type { AgentAudioVisualizerBarProps } from '@/components/agents-ui/agent-audio-visualizer-bar';
import type { AgentAudioVisualizerGridProps } from '@/components/agents-ui/agent-audio-visualizer-grid';
import type { AgentAudioVisualizerRadialProps } from '@/components/agents-ui/agent-audio-visualizer-radial';
import type { AgentAudioVisualizerWaveProps } from '@/components/agents-ui/agent-audio-visualizer-wave';
import { useJarvis } from '@/context/JarvisContext';
import { cn } from '@/lib/shadcn/utils';

// Lazy imports — cada visualizador só carrega se for o tipo configurado
const AgentAudioVisualizerAura = dynamic<AgentAudioVisualizerAuraProps & ComponentProps<'div'>>(
  () =>
    import('@/components/agents-ui/agent-audio-visualizer-aura').then((m) => ({
      default: m.AgentAudioVisualizerAura,
    })),
  { ssr: false }
);
const AgentAudioVisualizerBar = dynamic<AgentAudioVisualizerBarProps & ComponentProps<'div'>>(
  () =>
    import('@/components/agents-ui/agent-audio-visualizer-bar').then((m) => ({
      default: m.AgentAudioVisualizerBar,
    })),
  { ssr: false }
);
const AgentAudioVisualizerGrid = dynamic<AgentAudioVisualizerGridProps & ComponentProps<'div'>>(
  () =>
    import('@/components/agents-ui/agent-audio-visualizer-grid').then((m) => ({
      default: m.AgentAudioVisualizerGrid,
    })),
  { ssr: false }
);
const AgentAudioVisualizerRadial = dynamic<AgentAudioVisualizerRadialProps & ComponentProps<'div'>>(
  () =>
    import('@/components/agents-ui/agent-audio-visualizer-radial').then((m) => ({
      default: m.AgentAudioVisualizerRadial,
    })),
  { ssr: false }
);
const AgentAudioVisualizerWave = dynamic<AgentAudioVisualizerWaveProps & ComponentProps<'div'>>(
  () =>
    import('@/components/agents-ui/agent-audio-visualizer-wave').then((m) => ({
      default: m.AgentAudioVisualizerWave,
    })),
  { ssr: false }
);

interface AudioVisualizerProps extends MotionProps {
  appConfig: AppConfig;
  isChatOpen: boolean;
  className?: string;
}

export function AudioVisualizer({
  appConfig,
  isChatOpen,
  className,
  ...props
}: AudioVisualizerProps) {
  const { audioVisualizerType } = appConfig;
  const { agentState, volume } = useJarvis();

  // Mapeamento de volume: O Analyser retorna 0-255, normalizamos para 0-1
  const normalizedVolume = volume / 255;

  switch (audioVisualizerType) {
    case 'aura': {
      const { audioVisualizerColor, audioVisualizerAuraColorShift } = appConfig;
      return (
        <motion.div className={cn('size-75 md:size-112.5', className)} {...props}>
          <AgentAudioVisualizerAura
            state={agentState}
            volume={normalizedVolume}
            color={audioVisualizerColor}
            colorShift={audioVisualizerAuraColorShift}
            className="h-full w-full"
          />
        </motion.div>
      );
    }
    case 'wave': {
      const { audioVisualizerColor, audioVisualizerWaveLineWidth = 3 } = appConfig;
      return (
        <motion.div className={className} {...props}>
          <AgentAudioVisualizerWave
            state={agentState}
            volume={normalizedVolume}
            color={audioVisualizerColor}
            lineWidth={isChatOpen ? audioVisualizerWaveLineWidth * 2 : audioVisualizerWaveLineWidth}
            className="size-75 md:size-112.5"
          />
        </motion.div>
      );
    }
    case 'grid': {
      const { audioVisualizerGridRowCount = 9, audioVisualizerGridColumnCount = 9 } = appConfig;
      const totalCount = audioVisualizerGridRowCount * audioVisualizerGridColumnCount;

      let size: 'icon' | 'sm' | 'md' | 'lg' | 'xl' = 'sm';
      if (totalCount <= 100) {
        size = 'xl';
      } else if (totalCount <= 200) {
        size = 'lg';
      } else if (totalCount <= 300) {
        size = 'md';
      }

      return (
        <motion.div className={className} {...props}>
          <AgentAudioVisualizerGrid
            size={size}
            state={agentState}
            volume={normalizedVolume}
            rowCount={audioVisualizerGridRowCount}
            columnCount={audioVisualizerGridColumnCount}
            radius={Math.round(
              Math.min(audioVisualizerGridRowCount, audioVisualizerGridColumnCount) / 4
            )}
            className={cn('size-87.5 gap-0 p-8 md:size-112.5')}
          />
        </motion.div>
      );
    }
    case 'radial': {
      const { audioVisualizerRadialBarCount = 25, audioVisualizerRadialRadius = 12 } = appConfig;
      return (
        <motion.div className={className} {...props}>
          <AgentAudioVisualizerRadial
            size="xl"
            state={agentState}
            volume={normalizedVolume}
            radius={audioVisualizerRadialRadius}
            barCount={audioVisualizerRadialBarCount}
            className="size-112.5"
          />
        </motion.div>
      );
    }
    default: {
      const { audioVisualizerBarCount = 5 } = appConfig;

      let size: 'icon' | 'sm' | 'md' | 'lg' | 'xl' = 'icon';

      if (audioVisualizerBarCount <= 5) {
        size = 'xl';
      } else if (audioVisualizerBarCount <= 10) {
        size = 'lg';
      } else if (audioVisualizerBarCount <= 15) {
        size = 'md';
      } else if (audioVisualizerBarCount <= 30) {
        size = 'sm';
      }

      return (
        <motion.div
          className={cn(
            size === 'xl' && 'size-112.5',
            size === 'lg' && 'size-112.5',
            size === 'md' && 'size-87.5 md:size-112.5',
            size === 'sm' && 'size-75 md:size-112.5',
            size === 'icon' && 'size-75 md:size-112.5',
            className
          )}
          {...props}
        >
          <AgentAudioVisualizerBar
            size={size}
            state={agentState}
            volume={normalizedVolume}
            barCount={audioVisualizerBarCount}
            className="h-full w-full gap-2"
          />
        </motion.div>
      );
    }
  }
}
