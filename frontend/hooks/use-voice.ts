'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export function useVoice() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  const cleanupWebSocket = useCallback(
    ({ closeSocket = true }: { closeSocket?: boolean } = {}) => {
      clearReconnectTimer();

      const ws = wsRef.current;
      if (!ws) return;

      ws.onopen = null;
      ws.onmessage = null;
      ws.onerror = null;
      ws.onclose = null;
      if (
        closeSocket &&
        ws.readyState !== WebSocket.CLOSED &&
        ws.readyState !== WebSocket.CLOSING
      ) {
        ws.close();
      }
      wsRef.current = null;
    },
    [clearReconnectTimer]
  );

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    cleanupWebSocket();

    const scheme =
      typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `${scheme}://${host}:8000/ws/voice`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      if (typeof event.data !== 'string') {
        return;
      }

      try {
        const data = JSON.parse(event.data);

        if (data.type === 'status_update') {
          setStatus(data.status ?? 'idle');
          if (data.status === 'listening') {
            setIsListening(true);
            setTranscript('Escutando...');
            setResponse('');
          } else if (data.status === 'idle') {
            setIsListening(false);
          }

          if (data.transcript) setTranscript(data.transcript);
          if (data.response) setResponse(data.response);
        } else if (data.type === 'response_chunk') {
          setResponse((prev) => prev + (data.text ?? ''));
        }
      } catch (e) {
        console.error('Erro ao processar mensagem WS JSON:', e);
      }
    };

    ws.onopen = () => {
      console.log('HUD sincronizado com o backend via WebSocket JSON');
      setStatus('idle');
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      console.log('HUD desconectado do backend');
      cleanupWebSocket({ closeSocket: false });
      setStatus('idle');
      setIsListening(false);
      // Reconnect after 3 seconds without accumulating timers.
      clearReconnectTimer();
      reconnectTimerRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.onerror = () => {
      setStatus('idle');
      setIsListening(false);
      if (ws.readyState !== WebSocket.CLOSED && ws.readyState !== WebSocket.CLOSING) {
        ws.close();
      }
    };
  }, [cleanupWebSocket, clearReconnectTimer]);

  const toggleListening = () => {
    // The backend controls capture; the click only asks it to start listening.
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      if (!isListening) {
        wsRef.current.send(JSON.stringify({ type: 'manual_trigger' }));
      }
    } else {
      connect();
    }
  };

  useEffect(() => {
    connect();
    return () => {
      mountedRef.current = false;
      cleanupWebSocket();
    };
  }, [cleanupWebSocket, connect]);

  return {
    isListening,
    transcript,
    response,
    status,
    toggleListening,
    connect,
  };
}
