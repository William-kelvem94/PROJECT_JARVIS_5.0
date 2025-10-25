import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: Date
  isStreaming?: boolean
}

export interface Conversation {
  id: string
  title: string
  model_name: string
  created_at: Date
  updated_at?: Date
  messages: Message[]
}

interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  isLoading: boolean
  isStreaming: boolean

  setConversations: (conversations: Conversation[]) => void
  setCurrentConversation: (conversation: Conversation | null) => void
  addMessage: (message: Message) => void
  updateMessage: (messageId: string, content: string) => void
  setLoading: (loading: boolean) => void
  setStreaming: (streaming: boolean) => void
  clearCurrentConversation: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversation: null,
  isLoading: false,
  isStreaming: false,

  setConversations: (conversations) => set({ conversations }),

  setCurrentConversation: (conversation) =>
    set({ currentConversation: conversation }),

  addMessage: (message) =>
    set((state) => {
      if (!state.currentConversation) return state

      return {
        currentConversation: {
          ...state.currentConversation,
          messages: [...state.currentConversation.messages, message],
        },
      }
    }),

  updateMessage: (messageId, content) =>
    set((state) => {
      if (!state.currentConversation) return state

      return {
        currentConversation: {
          ...state.currentConversation,
          messages: state.currentConversation.messages.map((msg) =>
            msg.id === messageId ? { ...msg, content } : msg
          ),
        },
      }
    }),

  setLoading: (loading) => set({ isLoading: loading }),
  setStreaming: (streaming) => set({ isStreaming: streaming }),
  clearCurrentConversation: () => set({ currentConversation: null }),
}))

