import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { Send, Loader2, Bot, User as UserIcon } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useChatStore } from '@/store/chatStore'
import { conversationApi } from '@/lib/api'
import { toast } from '@/components/ui/toaster'
import ReactMarkdown from 'react-markdown'

const ChatPage = () => {
  const { conversationId } = useParams()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { currentConversation, isStreaming, setCurrentConversation } = useChatStore()
  const { isConnected, sendMessage, error: wsError } = useWebSocket()

  // Load conversation if ID provided
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId)
    }
  }, [conversationId])

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentConversation?.messages])

  // Show WebSocket errors
  useEffect(() => {
    if (wsError) {
      toast({ message: wsError, type: 'error' })
    }
  }, [wsError])

  const loadConversation = async (id: string) => {
    try {
      const response = await conversationApi.get(id)
      setCurrentConversation(response.data)
    } catch (error) {
      toast({ message: 'Erro ao carregar conversa', type: 'error' })
    }
  }

  const handleSend = () => {
    if (!input.trim() || isStreaming) return

    sendMessage(input, conversationId)
    setInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Connection Status */}
      {!isConnected && (
        <div className="px-6 py-3 bg-yellow-600/20 border-b border-yellow-600/30 text-yellow-400 text-sm text-center">
          Conectando ao servidor...
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <AnimatePresence mode="popLayout">
          {currentConversation?.messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex gap-4 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}

              <div
                className={`max-w-[70%] rounded-2xl px-6 py-4 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'glass border border-dark-800'
                }`}
              >
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
                {message.isStreaming && (
                  <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Gerando...</span>
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <div className="w-10 h-10 rounded-full bg-dark-700 flex items-center justify-center flex-shrink-0">
                  <UserIcon className="w-5 h-5 text-gray-300" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Empty state */}
        {!currentConversation?.messages.length && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mx-auto animate-float">
                <Bot className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-200">
                Olá! Como posso ajudar?
              </h2>
              <p className="text-gray-400">
                Digite sua mensagem abaixo para começar uma conversa
              </p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 glass border-t border-dark-800">
        <div className="flex gap-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem..."
            className="input resize-none"
            rows={1}
            disabled={isStreaming || !isConnected}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming || !isConnected}
            className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isStreaming ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatPage

