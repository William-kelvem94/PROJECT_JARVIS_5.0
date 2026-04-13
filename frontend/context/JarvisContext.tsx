'use client';

import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface JarvisContextType {
  isConnected: boolean;
  isSpeaking: boolean;
  agentState: 'idle' | 'listening' | 'thinking' | 'speaking';
  messages: Message[];
  error: string | null;
  volume: number; // 0 a 100 para visualizadores
  connect: () => Promise<void>;
  disconnect: () => void;
  sendMessage: (text: string) => void;
}

const JarvisContext = createContext<JarvisContextType | undefined>(undefined);

export function JarvisProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [agentState, setAgentState] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [volume, setVolume] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  // Loop de animação para o volume (Visualizadores)
  useEffect(() => {
    let animationId: number;
    const updateVolume = () => {
      if (analyserRef.current && isConnected) {
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((prev, cur) => prev + cur, 0) / dataArray.length;
        setVolume(average);
      }
      animationId = requestAnimationFrame(updateVolume);
    };
    updateVolume();
    return () => cancelAnimationFrame(animationId);
  }, [isConnected]);

  const connect = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // Setup Analyser para as Orbes
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const wsUrl = process.env.NEXT_PUBLIC_VOICE_WEBSOCKET_URL || `ws://${window.location.hostname}:8000/ws/voice-stream`;
      const ws = new WebSocket(wsUrl);
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        setIsConnected(true);
        setAgentState('idle');
        setError(null);
        
        const recorder = new MediaRecorder(stream);
        mediaRecorderRef.current = recorder;
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            ws.send(e.data);
          }
        };
        recorder.start(250);
      };

      ws.onmessage = async (event) => {
        if (event.data instanceof ArrayBuffer && audioContextRef.current) {
          setIsSpeaking(true);
          setAgentState('speaking');
          try {
            const audioBuffer = await audioContextRef.current.decodeAudioData(event.data);
            const playSource = audioContextRef.current.createBufferSource();
            playSource.buffer = audioBuffer;
            
            // Conecta a saída do Jarvis no analisador também para a orbe pulsar com a fala dele!
            playSource.connect(analyserRef.current!);
            playSource.connect(audioContextRef.current.destination);
            
            playSource.onended = () => {
                setIsSpeaking(false);
                setAgentState('idle');
            };
            playSource.start();
          } catch (e) {
            console.error('Error decoding audio', e);
          }
        } else if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
              setMessages(prev => [...prev, {
                role: data.role,
                content: data.text,
                timestamp: new Date().toLocaleTimeString()
              }]);
            } else if (data.type === 'jarvis_speaking') {
                setAgentState(data.state ? 'speaking' : 'idle');
            }
          } catch(e) {}
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setAgentState('idle');
      };

      ws.onerror = () => setError("Conexão perdida com o Jarvis.");
      wsRef.current = ws;

    } catch (err: any) {
      setError(err.message || "Erro ao iniciar Jarvis.");
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) wsRef.current.close();
    if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'text_message', text }));
        setMessages(prev => [...prev, {
            role: 'user',
            content: text,
            timestamp: new Date().toLocaleTimeString()
        }]);
    }
  }, []);

  return (
    <JarvisContext.Provider value={{
      isConnected,
      isSpeaking,
      agentState,
      messages,
      error,
      volume,
      connect,
      disconnect,
      sendMessage
    }}>
      {children}
    </JarvisContext.Provider>
  );
}

export function useJarvis() {
  const context = useContext(JarvisContext);
  if (context === undefined) {
    throw new Error('useJarvis must be used within a JarvisProvider');
  }
  return context;
}
