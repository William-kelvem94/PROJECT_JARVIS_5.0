'use client';
import { useState, useCallback, useRef, useEffect } from 'react';

export function useVoice() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');

  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const scheme = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `${scheme}://${host}:8000/ws/voice`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'status_update') {
            setStatus(data.status);
            if (data.status === 'listening') {
                setIsListening(true);
                setTranscript('Escutando...');
                setResponse('');
            } else if (data.status === 'idle') {
                setIsListening(false);
            }

            if (data.transcript) setTranscript(data.transcript);
            if (data.response) setResponse(data.response);
        }
        else if (data.type === 'response_chunk') {
            setResponse(prev => prev + data.text);
        }
      } catch (e) {
        console.error("Erro ao processar mensagem WS:", e);
      }
    };

    ws.onopen = () => {
      console.log('🎙️ HUD Sincronizado com o Backend');
      setStatus('idle');
    };

    ws.onclose = () => {
        console.log('🔌 HUD Desconectado do Backend');
        setStatus('idle');
        setIsListening(false);
        // Tenta reconectar após 3 segundos
        setTimeout(connect, 3000);
    };
  }, []);

  const toggleListening = () => {
      // Como o backend controla o áudio agora, o clique apenas força o backend a escutar
      if (wsRef.current?.readyState === WebSocket.OPEN) {
          if (!isListening) {
              wsRef.current.send(JSON.stringify({ type: "manual_trigger" }));
              // O status vai mudar pra 'listening' assim que o backend confirmar
          }
      } else {
          connect();
      }
  };

  useEffect(() => {
    connect();
    return () => {
        wsRef.current?.close();
    };
  }, [connect]);

  return {
    isListening,
    transcript,
    response,
    status,
    toggleListening,
    connect
  };
}
