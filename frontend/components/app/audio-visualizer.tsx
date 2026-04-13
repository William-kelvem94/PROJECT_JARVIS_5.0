import { type MotionProps, motion } from 'motion/react';
import { useJarvis } from '@/context/JarvisContext';
import { AppConfig } from '@/app-config';
import dynamic from 'next/dynamic';
import { cn } from '@/lib/shadcn/utils';

// Lazy imports — cada visualizador só carrega se for o tipo configurado
const AgentAudioVisualizerAura = dynamic(
  () => import('@/components/agents-ui/agent-audio-visualizer-aura').then(m => ({ default: m.AgentAudioVisualizerAura })),
  { ssr: false }
);
const AgentAudioVisualizerBar = dynamic(
  () => import('@/components/agents-ui/agent-audio-visualizer-bar').then(m => ({ default: m.AgentAudioVisualizerBar })),
  { ssr: false }
);
const AgentAudioVisualizerGrid = dynamic(
  () => import('@/components/agents-ui/agent-audio-visualizer-grid').then(m => ({ default: m.AgentAudioVisualizerGrid })),
  { ssr: false }
);
const AgentAudioVisualizerRadial = dynamic(
  () => import('@/components/agents-ui/agent-audio-visualizer-radial').then(m => ({ default: m.AgentAudioVisualizerRadial })),
  { ssr: false }
);
const AgentAudioVisualizerWave = dynamic(
  () => import('@/components/agents-ui/agent-audio-visualizer-wave').then(m => ({ default: m.AgentAudioVisualizerWave })),
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
        <motion.div className={cn('size-[300px] md:size-[450px]', className)} {...props}>
          <AgentAudioVisualizerAura
            state={agentState as any}
            volume={normalizedVolume}
            color={audioVisualizerColor}
            colorShift={audioVisualizerAuraColorShift}
            className="w-full h-full"
          />
        </motion.div>
      );
    }
    case 'wave': {
      const { audioVisualizerColor, audioVisualizerWaveLineWidth = 3 } = appConfig;
      return (
        <motion.div className={className} {...props}>
          <AgentAudioVisualizerWave
            state={agentState as any}
            volume={normalizedVolume}
            color={audioVisualizerColor}
            lineWidth={isChatOpen ? audioVisualizerWaveLineWidth * 2 : audioVisualizerWaveLineWidth}
            className="size-[300px] md:size-[450px]"
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
            state={agentState as any}
            volume={normalizedVolume}
            rowCount={audioVisualizerGridRowCount}
            columnCount={audioVisualizerGridColumnCount}
            radius={Math.round(
              Math.min(audioVisualizerGridRowCount, audioVisualizerGridColumnCount) / 4
            )}
            className={cn('size-[350px] gap-0 p-8 md:size-[450px]')}
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
            state={agentState as any}
            volume={normalizedVolume}
            radius={audioVisualizerRadialRadius}
            barCount={audioVisualizerRadialBarCount}
            className="size-[450px]"
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
            size === 'xl' && 'size-[450px]',
            size === 'lg' && 'size-[450px]',
            size === 'md' && 'size-[350px] md:size-[450px]',
            size === 'sm' && 'size-[300px] md:size-[450px]',
            size === 'icon' && 'size-[300px] md:size-[450px]',
            className
          )}
          {...props}
        >
          <AgentAudioVisualizerBar
            size={size}
            state={agentState as any}
            volume={normalizedVolume}
            barCount={audioVisualizerBarCount}
            className="w-full h-full gap-2"
          />
        </motion.div>
      );
    }
  }
}
