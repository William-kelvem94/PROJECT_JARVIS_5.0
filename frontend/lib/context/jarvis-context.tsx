'use client';

import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { jarvisApi } from '@/lib/jarvis-endpoints';

type ExtendedWindow = Window & {
  webkitAudioContext?: typeof AudioContext;
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
  const [isMicEnabled, setIsMicEnabled] = useState(false);
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
  const localStreamRef = useRef<MediaStream | null>(null);
  const screenStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const setLocalMediaStream = useCallback((stream: MediaStream | null) => {
    localStreamRef.current = stream;
    setLocalStream(stream);
    setIsMicEnabled(Boolean(stream?.getAudioTracks().some((track) => track.enabled)));
    setIsCameraEnabled(Boolean(stream?.getVideoTracks().length));
  }, []);

  const setScreenMediaStream = useCallback((stream: MediaStream | null) => {
    screenStreamRef.current = stream;
    setScreenStream(stream);
    setIsScreenSharing(Boolean(stream));
  }, []);

  const stopStream = useCallback((stream: MediaStream | null) => {
    stream?.getTracks().forEach((track) => {
      track.onended = null;
      track.stop();
    });
  }, []);

  const cleanupSession = useCallback(
    ({ closeSocket = true }: { closeSocket?: boolean } = {}) => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      const ws = wsRef.current;
      if (ws) {
        ws.onopen = null;
        ws.onclose = null;
        ws.onmessage = null;
        ws.onerror = null;
        if (
          closeSocket &&
          ws.readyState !== WebSocket.CLOSED &&
          ws.readyState !== WebSocket.CLOSING
        ) {
          ws.close();
        }
        wsRef.current = null;
      }

      if (processorRef.current) {
        processorRef.current.onaudioprocess = null;
        processorRef.current.disconnect();
        processorRef.current = null;
      }

      audioSourceRef.current?.disconnect();
      audioSourceRef.current = null;
      analyserRef.current?.disconnect();
      analyserRef.current = null;

      const audioContext = audioContextRef.current;
      audioContextRef.current = null;
      if (audioContext && audioContext.state !== 'closed') {
        audioContext.close().catch(() => undefined);
      }

      stopStream(localStreamRef.current);
      stopStream(screenStreamRef.current);
      setLocalMediaStream(null);
      setScreenMediaStream(null);
      setIsConnected(false);
      setIsSpeaking(false);
      setAgentState('idle');
      setVolume(0);
    },
    [setLocalMediaStream, setScreenMediaStream, stopStream]
  );

  const disconnect = useCallback(() => {
    cleanupSession();
  }, [cleanupSession]);

  const handleConnectionClosed = useCallback(
    (message?: string) => {
      if (!mountedRef.current) return;
      cleanupSession({ closeSocket: false });
      if (message) {
        setError(message);
      }
    },
    [cleanupSession]
  );

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

  const connect = useCallback(async () => {
    cleanupSession();

    let stream: MediaStream | null = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
        video: false,
      });
      setLocalMediaStream(stream);

      const win = window as ExtendedWindow;
      const AudioContextCtor = window.AudioContext || win.webkitAudioContext;
      if (!AudioContextCtor) {
        throw new Error('Web Audio API nao suportada neste navegador.');
      }

      const audioContext = new AudioContextCtor();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      audioSourceRef.current = source;
      analyserRef.current = analyser;

      const defaultScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
      const wsUrl =
        process.env.NEXT_PUBLIC_WS_URL ||
        `${defaultScheme}://${window.location.hostname}:8000/ws/voice`;
      const ws = new WebSocket(wsUrl);
      ws.binaryType = 'arraybuffer';
      wsRef.current = ws;

      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processor.onaudioprocess = (e) => {
        if (ws.readyState === WebSocket.OPEN && localStreamRef.current?.getAudioTracks()[0]?.enabled) {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcm[i] = inputData[i] * 32767;
          }
          ws.send(pcm.buffer);
        }
      };

      const dummyGainNode = audioContext.createGain();
      dummyGainNode.gain.value = 0;
      source.connect(processor);
      processor.connect(dummyGainNode);
      dummyGainNode.connect(audioContext.destination);
      processorRef.current = processor;

      ws.onopen = () => {
        setIsConnected(true);
        setAgentState('idle');
        setError(null);
      };

      ws.onmessage = async (event) => {
        // JSON is the active protocol for control/text. Binary is kept isolated for
        // compatibility with existing audio responses.
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
              const audioBuffer = await audioContextRef.current.decodeAudioData(binaryData);
              const playSource = audioContextRef.current.createBufferSource();
              playSource.buffer = audioBuffer;
              if (analyserRef.current) {
                playSource.connect(analyserRef.current);
              }
              playSource.connect(audioContextRef.current.destination);
              playSource.onended = () => {
                setIsSpeaking(false);
                setAgentState('idle');
              };
              playSource.start();
            }
          } catch (e) {
            console.error('Falha ao decodificar áudio do Jarvis:', e);
            try {
              const blob = new Blob([binaryData], { type: 'audio/mp3' });
              const url = URL.createObjectURL(blob);
              const audio = new Audio(url);
              audio.onended = () => {
                URL.revokeObjectURL(url);
                setIsSpeaking(false);
                setAgentState('idle');
              };
              await audio.play();
            } catch {}
          }
        } else if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {
              setAgentState(data.status ?? 'idle');
              setIsSpeaking(data.status === 'speaking');
              if (data.response) {
                setMessages((prev) => [
                  ...prev,
                  {
                    role: 'assistant',
                    content: data.response,
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ]);
              }
              if (data.transcript) {
                setMessages((prev) => [
                  ...prev,
                  {
                    role: 'user',
                    content: data.transcript,
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ]);
              }
            } else if (data.type === 'response_chunk') {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                if (last && last.role === 'assistant') {
                  return [
                    ...prev.slice(0, -1),
                    { ...last, content: `${last.content}${data.text ?? ''}` },
                  ];
                }
                return [
                  ...prev,
                  {
                    role: 'assistant',
                    content: data.text ?? '',
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ];
              });
            } else if (data.type === 'message' || data.type === 'message_chunk') {
              setMessages((prev) => {
                const last = prev[prev.length - 1];
                if (data.type === 'message_chunk' && last && last.role === 'assistant') {
                  return [
                    ...prev.slice(0, -1),
                    { ...last, content: `${last.content} ${data.text ?? ''}` },
                  ];
                }
                return [
                  ...prev,
                  {
                    role: data.role || 'assistant',
                    content: data.text ?? '',
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ];
              });
            } else if (data.type === 'jarvis_speaking') {
              setAgentState(data.state ? 'speaking' : 'idle');
              setIsSpeaking(Boolean(data.state));
            }
          } catch {}
        }
      };

      ws.onclose = () => {
        handleConnectionClosed();
      };

      ws.onerror = () => {
        if (!mountedRef.current) return;
        cleanupSession();
        setError('Conexão perdida com o Jarvis.');
      };
    } catch (err: unknown) {
      if (stream && localStreamRef.current !== stream) {
        stopStream(stream);
      }
      cleanupSession();
      setError(err instanceof Error ? err.message : 'Erro ao iniciar Jarvis.');
    }
  }, [cleanupSession, handleConnectionClosed, setLocalMediaStream, stopStream, setIsConnected, setAgentState, setError, setMessages, setVolume]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const toggleMic = useCallback(() => {
    const audioTrack = localStreamRef.current?.getAudioTracks()[0];
    if (!audioTrack) {
      setIsMicEnabled(false);
      return;
    }

    audioTrack.enabled = !audioTrack.enabled;
    setIsMicEnabled(audioTrack.enabled);
    loggerLocal('Microfone', audioTrack.enabled ? 'Ativado' : 'Mudo');
  }, []);

  const toggleCamera = useCallback(async () => {
    try {
      const stream = localStreamRef.current;
      if (isCameraEnabled) {
        stream?.getVideoTracks().forEach((track) => {
          track.stop();
          stream.removeTrack(track);
        });
        setLocalMediaStream(stream);
        return;
      }

      if (!stream) {
        setError('Conecte o Jarvis antes de ativar a câmera.');
        setIsCameraEnabled(false);
        return;
      }

      const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (localStreamRef.current !== stream) {
        stopStream(videoStream);
        return;
      }

      const videoTrack = videoStream.getVideoTracks()[0];
      if (!videoTrack) {
        stopStream(videoStream);
        return;
      }

      stream.addTrack(videoTrack);
      setLocalMediaStream(stream);
      setError(null);
    } catch (e) {
      console.error('Erro ao acessar câmera:', e);
      setIsCameraEnabled(false);
    }
  }, [isCameraEnabled, setLocalMediaStream, stopStream]);

  const toggleScreenShare = useCallback(async () => {
    try {
      if (isScreenSharing) {
        stopStream(screenStreamRef.current);
        setScreenMediaStream(null);
        return;
      }

      const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      setScreenMediaStream(displayStream);
      const [displayTrack] = displayStream.getVideoTracks();
      if (displayTrack) {
        displayTrack.onended = () => {
          setScreenMediaStream(null);
        };
      }
    } catch (e) {
      console.error('Erro ao compartilhar tela:', e);
    }
  }, [isScreenSharing, setScreenMediaStream, stopStream]);

  const sendMessage = useCallback(async (text: string) => {
    const userMessage = {
      role: 'user' as const,
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const res = await fetch(jarvisApi('/chat'), {
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

  function loggerLocal(label: string, state: string) {
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
