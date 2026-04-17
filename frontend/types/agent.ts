export type AgentState =
  | 'connecting'
  | 'initializing'
  | 'listening'
  | 'thinking'
  | 'speaking'
  | 'idle'
  | 'failed'
  | 'disconnected'
  | 'pre-connect-buffering';
