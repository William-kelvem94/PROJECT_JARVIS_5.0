export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // agent dispatch configuration
  agentName?: string;
  jarvisApiUrl?: string;
  audioVisualizerType?: string; // e.g. 'wave', 'bar', ...
  audioVisualizerColor?: string;
  audioVisualizerAuraColorShift?: number;
  audioVisualizerWaveLineWidth?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerBarCount?: number;

  // optional toggle for vanta background (setting false will disable)
  enableVanta?: boolean;
  // allow arbitrary extra fields (used by audio visualizer settings)
  [key: string]: unknown;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Jarvis',
  pageTitle: 'Jarvis - Assistente de Voz',
  pageDescription: 'Um assistente de voz avançado e inteligente.',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/jarvis-logo.svg',
  accent: '#002cf2',
  logoDark: '/jarvis-logo-dark.svg',
  accentDark: '#1fd5f9',
  startButtonText: 'Iniciar Chamada',

  // agent dispatch configuration
  agentName: process.env.AGENT_NAME ?? undefined,
  jarvisApiUrl: process.env.NEXT_PUBLIC_JARVIS_API_URL ?? undefined,
  audioVisualizerType: process.env.NEXT_PUBLIC_AUDIO_VISUALIZER ?? 'wave',
  audioVisualizerColor: process.env.NEXT_PUBLIC_AUDIO_VISUALIZER_COLOR ?? '#1fd5f9',
  audioVisualizerAuraColorShift: Number(process.env.NEXT_PUBLIC_AUDIO_AURA_SHIFT ?? '0'),
  audioVisualizerWaveLineWidth: Number(process.env.NEXT_PUBLIC_AUDIO_WAVE_WIDTH ?? '3'),
  audioVisualizerGridRowCount: Number(process.env.NEXT_PUBLIC_AUDIO_GRID_ROWS ?? '9'),
  audioVisualizerGridColumnCount: Number(process.env.NEXT_PUBLIC_AUDIO_GRID_COLUMNS ?? '9'),
  audioVisualizerRadialBarCount: Number(process.env.NEXT_PUBLIC_AUDIO_RADIAL_BARS ?? '25'),
  audioVisualizerRadialRadius: Number(process.env.NEXT_PUBLIC_AUDIO_RADIAL_RADIUS ?? '12'),
  audioVisualizerBarCount: Number(process.env.NEXT_PUBLIC_AUDIO_BAR_COUNT ?? '5'),

  enableVanta: process.env.NEXT_PUBLIC_ENABLE_VANTA !== 'false',
};
