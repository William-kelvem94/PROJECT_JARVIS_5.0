'use client';
import { useState, useCallback, useRef, useEffect } from 'react';

export function useVoice() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket('ws://localhost:8000/ws/voice');
    wsRef.current = ws;
    
    ws.onmessage = async (event) => {
      if (event.data instanceof Blob) {
        setStatus('speaking');
        const arrayBuffer = await event.data.arrayBuffer();
        playAudio(arrayBuffer);
      } else {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'response_chunk') {
            setResponse(prev => prev + data.text);
            setStatus('thinking');
          }
        } catch (e) {
          console.error("Erro ao processar mensagem WS:", e);
        }
      }
    };

    ws.onopen = () => {
      console.log('🎙️ WebSocket de voz conectado');
      setStatus('idle');
    };
    
    ws.onclose = () => {
        console.log('🔌 WebSocket de voz desconectado');
        setStatus('idle');
        // Tenta reconectar após 3 segundos
        setTimeout(connect, 3000);
    };
  }, []);

  const playAudio = async (arrayBuffer: ArrayBuffer) => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    const ctx = audioContextRef.current;
    if (ctx.state === 'suspended') await ctx.resume();
    
    const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
    const source = ctx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(ctx.destination);
    source.onended = () => {
        // Só volta para idle se não estiver escutando novamente
        setStatus(prev => prev === 'speaking' ? 'idle' : prev);
    };
    source.start();
  };

  const startListening = async () => {
    try {
      if (wsRef.current?.readyState !== WebSocket.OPEN) connect();
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      }
      const ctx = audioContextRef.current;
      if (ctx.state === 'suspended') await ctx.resume();

      const source = ctx.createMediaStreamSource(stream);
      // Processor para capturar chunks de áudio (formato PCM 16-bit esperado pelo backend)
      const processor = ctx.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      source.connect(processor);
      processor.connect(ctx.destination);

      processor.onaudioprocess = (e) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          // Converte Float32 para Int16
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
          }
          wsRef.current.send(pcmData.buffer);
        }
      };

      setIsListening(true);
      setStatus('listening');
      setResponse('');
      setTranscript('Escutando...');
    } catch (err) {
      console.error("Erro ao acessar microfone:", err);
      setStatus('idle');
    }
  };

  const stopListening = () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (processorRef.current) {
        processorRef.current.disconnect();
      }
      setIsListening(false);
      setStatus('idle');
  };

  useEffect(() => {
    connect();
    return () => {
        wsRef.current?.close();
        stopListening();
    };
  }, [connect]);

  return { 
    isListening, 
    transcript, 
    response, 
    status, 
    startListening, 
    stopListening,
    connect 
  };
}
