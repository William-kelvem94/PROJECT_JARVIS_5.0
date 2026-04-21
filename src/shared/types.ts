// Shared TypeScript interfaces - JARVIS 5.0 Core Types
// Usado por frontend/backend via LiveKit Data Channels

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface PerceptionSnapshot {
  type: 'perception_update';
  face_present: boolean;
  face_count: number;
  face_emotion: string;
  face_emotion_score: number;
  face_identity?: string;
  face_identity_confidence: number;
  hand_gesture?: string;
  hand_side?: string;
  head_gesture?: string;
  pointing_direction?: string;
  pointing_xy?: [number, number];
  wake_word_triggered: boolean;
  speaker_identity?: string;
  offline_transcript?: string;
  active_levels: string[];
  timestamp: string;
}

export interface MemoryFact {
  memory: string;
  category: 'preference' | 'event' | 'task' | 'code' | 'fact' | 'personality';
  updated_at: string;
}

export interface ToolResult {
  tool: string;
  args: Record<string, any>;
  result: string;
}

export interface TelemetryData {
  type: 'telemetry_update';
  cpu: number;
  ram: number;
  battery: number;
  gpu?: number;
  gpu_mem?: number;
  gpu_name?: string;
  model: string;
  persona: string;
}

export interface ActivityLog {
  type: 'activity_log';
  title: string;
  detail: string;
  log_type: 'info' | 'error' | 'cmd' | 'edit' | 'git';
  status: 'success' | 'error';
  timestamp: string;
}
