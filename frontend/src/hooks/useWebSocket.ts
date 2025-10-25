import { useEffect, useRef, useCallback, useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useChatStore, Message } from '@/store/chatStore'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

interface WebSocketMessage {
  type: string
  [key: string]: any
}

export const useWebSocket = () => {
  const { accessToken } = useAuthStore()
  const { addMessage, updateMessage, setStreaming, currentConversation } = useChatStore()
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const currentMessageRef = useRef<string>('')
  const currentMessageIdRef = useRef<string>('')

  const connect = useCallback(() => {
    if (!accessToken) {
      setError('No access token available')
      return
    }

    try {
      const ws = new WebSocket(`${WS_URL}/api/v1/ws/chat?token=${accessToken}`)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)

          switch (data.type) {
            case 'connection':
              console.log('Connection established:', data.message)
              break

            case 'conversation_created':
              console.log('Conversation created:', data.conversation_id)
              break

            case 'message_start':
              setStreaming(true)
              currentMessageRef.current = ''
              currentMessageIdRef.current = `temp-${Date.now()}`
              
              // Add empty assistant message
              addMessage({
                id: currentMessageIdRef.current,
                role: 'assistant',
                content: '',
                createdAt: new Date(),
                isStreaming: true,
              })
              break

            case 'message_chunk':
              currentMessageRef.current += data.content
              updateMessage(currentMessageIdRef.current, currentMessageRef.current)
              break

            case 'message_end':
              setStreaming(false)
              // Update with final message ID
              if (data.message_id) {
                updateMessage(currentMessageIdRef.current, currentMessageRef.current)
              }
              currentMessageRef.current = ''
              currentMessageIdRef.current = ''
              break

            case 'error':
              console.error('WebSocket error:', data.message)
              setError(data.message)
              break

            case 'pong':
              // Heartbeat response
              break

            default:
              console.log('Unknown message type:', data.type)
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...')
          connect()
        }, 3000)
      }
    } catch (err) {
      console.error('Error creating WebSocket:', err)
      setError('Failed to create WebSocket connection')
    }
  }, [accessToken, addMessage, updateMessage, setStreaming])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
  }, [])

  const sendMessage = useCallback(
    (message: string, conversationId?: string) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        setError('WebSocket is not connected')
        return
      }

      // Add user message to chat
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        createdAt: new Date(),
      }
      addMessage(userMessage)

      // Send message via WebSocket
      wsRef.current.send(
        JSON.stringify({
          type: 'chat',
          message,
          conversation_id: conversationId || currentConversation?.id,
        })
      )
    },
    [addMessage, currentConversation]
  )

  // Start heartbeat
  useEffect(() => {
    if (!isConnected || !wsRef.current) return

    const heartbeat = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000) // Every 30 seconds

    return () => clearInterval(heartbeat)
  }, [isConnected])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    isConnected,
    error,
    sendMessage,
    connect,
    disconnect,
  }
}

