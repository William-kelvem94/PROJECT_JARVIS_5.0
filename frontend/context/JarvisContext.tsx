'use client';

import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';

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
  sendMessage: (text: string) => void;
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
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
        video: false,
      });
      setLocalStream(stream);

      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const wsUrl =
        process.env.NEXT_PUBLIC_WS_URL || `ws://${window.location.hostname}:8000/ws/voice-stream`;
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
        (window as any)._audioProcessor = processor; // Evita Garbage Collection
      };

      ws.onmessage = async (event) => {
        if (event.data instanceof ArrayBuffer && audioContextRef.current) {
          setIsSpeaking(true);
          setAgentState('speaking');
          try {
            const audioBuffer = await audioContextRef.current.decodeAudioData(event.data);
            const playSource = audioContextRef.current.createBufferSource();
            playSource.buffer = audioBuffer;
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
              setMessages((prev) => [
                ...prev,
                {
                  role: data.role,
                  content: data.text,
                  timestamp: new Date().toLocaleTimeString(),
                },
              ]);
            } else if (data.type === 'jarvis_speaking') {
              setAgentState(data.state ? 'speaking' : 'idle');
            }
          } catch (e) {}
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        setLocalStream(null);
      };

      ws.onerror = () => setError('Conexão perdida com o Jarvis.');
      wsRef.current = ws;
    } catch (err: any) {
      setError(err.message || 'Erro ao iniciar Jarvis.');
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) wsRef.current.close();
    if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
    if (localStream) localStream.getTracks().forEach((t) => t.stop());
    if (screenStream) screenStream.getTracks().forEach((t) => t.stop());
    setIsConnected(false);
    setLocalStream(null);
    setScreenStream(null);
  }, [localStream, screenStream]);

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

  const sendMessage = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'text_message', text }));
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content: text,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    }
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
