export type MemoryItem = {
  id?: string;
  memory?: string;
  text?: string;
  content?: string;
  title?: string;
  metadata?: Record<string, unknown>;
};

export type TelemetryHistoryItem = {
  cpu?: number;
  memory?: number;
  ram?: number;
  status?: string;
  timestamp?: string;
};

export type VaultStats = {
  total_notes?: number;
  total_memories?: number;
  episodic?: number;
  semantic?: number;
  vault_path?: string;
  available?: boolean;
  [key: string]: unknown;
};

export type SaveStatus = {
  type: 'idle' | 'success' | 'error';
  message: string;
};

export type ProjectData = {
  memories: MemoryItem[];
  screenshots: string[];
  vaultStats: VaultStats | null;
  history: TelemetryHistoryItem[];
  isLoading: boolean;
  lastUpdated: Date | null;
};

export const roadmap = [
  { label: 'Backend FastAPI', state: 'online' },
  { label: 'WebSocket de voz', state: 'manual' },
  { label: 'Telemetria 8001', state: 'sincroniza' },
  { label: 'Vault Obsidian', state: 'indexado' },
  { label: 'Memória episódica', state: 'gravável' },
];
