'use client';

import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';

type ExtendedWindow = Window & {
  webkitAudioContext?: typeof AudioContext;
  _audioProcessor?: ScriptProcessorNode;
};

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface JarvisContextType {
  isConnected: boolean;
  isSpeaking: boolean;
  isMicEnabled: boolean;
  isCameraEnabled: boolean;
  isScreenSharing: boolean;
  agentState: 'idle' | 'listening' | 'thinking' | 'speaking';
  messages: Message[];
  error: string | null;
  volume: number;
  localStream: MediaStream | null;
  screenStream: MediaStream | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendMessage: (text: string) => Promise<void>;
  toggleMic: () => void;
  toggleCamera: () => Promise<void>;
  toggleScreenShare: () => Promise<void>;
}

const JarvisContext = createContext<JarvisContextType | undefined>(undefined);

export function JarvisProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMicEnabled, setIsMicEnabled] = useState(true);
  const [isCameraEnabled, setIsCameraEnabled] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [agentState, setAgentState] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>(
    'idle'
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [volume, setVolume] = useState(0);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [screenStream, setScreenStream] = useState<MediaStream | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  // Loop de animação para o volume (Visualizadores)
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

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

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current.onaudioprocess = null;
      processorRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => undefined);
      audioContextRef.current = null;
    }
    if (localStream) localStream.getTracks().forEach((t) => t.stop());
    if (screenStream) screenStream.getTracks().forEach((t) => t.stop());
    setIsConnected(false);
    setLocalStream(null);
    setScreenStream(null);
  }, [localStream, screenStream]);

  const connect = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
        video: false,
      });
      setLocalStream(stream);

      const win = window as ExtendedWindow;
      const AudioContextCtor = window.AudioContext || win.webkitAudioContext;
      if (!AudioContextCtor) {
        throw new Error('Web Audio API não suportada neste navegador.');
      }
      audioContextRef.current = new AudioContextCtor();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const defaultScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl =
        process.env.NEXT_PUBLIC_WS_URL ||
        `${defaultScheme}://${window.location.hostname}:8000/ws/voice-stream`;
      const ws = new WebSocket(wsUrl);
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        setIsConnected(true);
        setAgentState('idle');
        setError(null);

        // Em vez de MediaRecorder, usamos ScriptProcessor para áudio BRUTO (PCM)
        const processor = audioContextRef.current!.createScriptProcessor(4096, 1, 1);
        source.connect(processor);
        processor.connect(audioContextRef.current!.destination);
        processorRef.current = processor;

        processor.onaudioprocess = (e) => {
          if (ws.readyState === WebSocket.OPEN) {
            const inputData = e.inputBuffer.getChannelData(0);
            const pcmData = new Int16Array(inputData.length);
            // Conversão Float32 -> Int16
            for (let i = 0; i < inputData.length; i++) {
              pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7fff;
            }
            ws.send(pcmData.buffer);
          }
        };
        // Envia configuração real do hardware (Bug #5)
        ws.send(
          JSON.stringify({
            type: 'config',
            sample_rate: audioContextRef.current?.sampleRate || 48000,
          })
        );

        (window as ExtendedWindow)._audioProcessor = processor; // Evita Garbage Collection
      };

      ws.onmessage = async (event) => {
        // 1. Áudio Binário (MP3 do Jarvis)
        if (
          (event.data instanceof ArrayBuffer || event.data instanceof Blob) &&
          audioContextRef.current
        ) {
          const binaryData =
            event.data instanceof Blob ? await event.data.arrayBuffer() : event.data;

          setIsSpeaking(true);
          setAgentState('speaking');

          try {
            if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
              // Web Audio API decode (suporta MP3)
              const audioBuffer = await audioContextRef.current.decodeAudioData(binaryData);
              const playSource = audioContextRef.current.createBufferSource();
              playSource.buffer = audioBuffer;
              playSource.connect(analyserRef.current!);
              playSource.connect(audioContextRef.current.destination);
              playSource.onended = () => {
                setIsSpeaking(false);
                setAgentState('idle');
              };
              playSource.start();
            }
          } catch (e) {
            console.error('Falha ao decodificar áudio do Jarvis:', e);
            // Fallback para Audio Element se o Web Audio falhar ou estiver fechado
            try {
              const blob = new Blob([binaryData], { type: 'audio/mp3' });
              const url = URL.createObjectURL(blob);
              const audio = new Audio(url);
              audio.onended = () => {
                setIsSpeaking(false);
                setAgentState('idle');
              };
              await audio.play();
            } catch {}
          }
        }
        // 2. Mensagens JSON (Texto, Telemetria, etc)
        else if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'message' || data.type === 'message_chunk') {
              // Se for chunk, anexamos à última mensagem se ela for do assistente
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                if (data.type === 'message_chunk' && last && last.role === 'assistant') {
                  return [
                    ...prev.slice(0, -1),
                    { ...last, content: last.content + ' ' + data.text },
                  ];
                }
                return [
                  ...prev,
                  {
                    role: data.role || 'assistant',
                    content: data.text,
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ];
              });
            } else if (data.type === 'jarvis_speaking') {
              setAgentState(data.state ? 'speaking' : 'idle');
            } else if (data.type === 'wake_word_detected') {
              console.log('🎙️ Wake word detectada via hardware!');
            }
          } catch {}
        }
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;
        setIsConnected(false);
        setLocalStream(null);
      };

      ws.onerror = () => setError('Conexão perdida com o Jarvis.');
      wsRef.current = ws;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Erro ao iniciar Jarvis.');
    }
  }, []); // Conecta sem recriar callback por estado externo

  // Cleanup automático ao destruir o componente
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const toggleMic = useCallback(() => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0];
      audioTrack.enabled = !audioTrack.enabled;
      setIsMicEnabled(audioTrack.enabled);
      logger_local('Microfone', audioTrack.enabled ? 'Ativado' : 'Mudo');
    }
  }, [localStream]);

  const toggleCamera = useCallback(async () => {
    try {
      if (isCameraEnabled) {
        localStream?.getVideoTracks().forEach((t) => {
          t.stop();
          localStream.removeTrack(t);
        });
        setIsCameraEnabled(false);
      } else {
        const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoTrack = videoStream.getVideoTracks()[0];
        localStream?.addTrack(videoTrack);
        setIsCameraEnabled(true);
      }
    } catch (e) {
      console.error('Erro ao acessar câmera:', e);
    }
  }, [isCameraEnabled, localStream]);

  const toggleScreenShare = useCallback(async () => {
    try {
      if (isScreenSharing) {
        screenStream?.getTracks().forEach((t) => t.stop());
        setScreenStream(null);
        setIsScreenSharing(false);
      } else {
        const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        setScreenStream(displayStream);
        setIsScreenSharing(true);
        displayStream.getVideoTracks()[0].onended = () => {
          setIsScreenSharing(false);
          setScreenStream(null);
        };
      }
    } catch (e) {
      console.error('Erro ao compartilhar tela:', e);
    }
  }, [isScreenSharing, screenStream]);

  const sendMessage = useCallback(async (text: string) => {
    const userMessage = {
      role: 'user' as const,
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'text_message', text }));
      return;
    }

    // Fallback HTTP para manter o chat funcional mesmo sem WS/áudio ativo.
    try {
      const apiBase = process.env.NEXT_PUBLIC_JARVIS_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, user_name: 'jarvis_user' }),
      });

      if (!res.ok) {
        throw new Error(`Falha HTTP ${res.status}`);
      }

      const data = await res.json();
      if (data?.reply) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: data.reply,
            timestamp: new Date().toLocaleTimeString(),
          },
        ]);
        setAgentState('idle');
        setError(null);
        return;
      }
    } catch (e) {
      console.error('Falha no fallback de texto (/chat):', e);
    }

    setError('Jarvis offline no momento. Verifique backend e conexão WebSocket.');
  }, []);

  function logger_local(label: string, state: string) {
    console.log(`[Jarvis UI] ${label}: ${state}`);
  }

  return (
    <JarvisContext.Provider
      value={{
        isConnected,
        isSpeaking,
        isMicEnabled,
        isCameraEnabled,
        isScreenSharing,
        agentState,
        messages,
        error,
        volume,
        localStream,
        screenStream,
        connect,
        disconnect,
        sendMessage,
        toggleMic,
        toggleCamera,
        toggleScreenShare,
      }}
    >
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
