// Shared TypeScript interfaces between frontend and backend

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}
