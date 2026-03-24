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
  audioVisualizerType?: string;  // e.g. 'wave', 'bar', ...
  audioVisualizerColor?: string;
  audioVisualizerAuraColorShift?: number;
  audioVisualizerWaveLineWidth?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;

  // allow arbitrary extra fields (used by audio visualizer settings)
  [key: string]: any;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Jarvis',
  pageTitle: 'Jarvis - Assistente de Voz',
  pageDescription: 'Um assistente de voz avançado e inteligente.',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#002cf2',
  logoDark: '/lk-logo-dark.svg',
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

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,
};
