import { useState, useRef, useCallback, useEffect } from 'react';

// Variável global fora do hook para garantir SINGLETON absoluto, mesmo com React StrictMode
let globalSocket: WebSocket | null = null;
let globalIsConnecting = false;

export function useJarvisVoice() {
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const [isMuted, setIsMuted] = useState(false);
  const isMutedRef = useRef(false);

  // Sincroniza ref para acesso dentro do closure do onaudioprocess
  useEffect(() => {
    isMutedRef.current = isMuted;
  }, [isMuted]);
  
  const audioQueueRef = useRef<ArrayBuffer[]>([]);
  const isPlayingRef = useRef(false);

  const playNext = useCallback(async () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0 || !audioContextRef.current) return;
    
    isPlayingRef.current = true;
    const data = audioQueueRef.current.shift()!;
    
    try {
      const audioBuffer = await audioContextRef.current.decodeAudioData(data);
      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      
      source.onended = () => {
        isPlayingRef.current = false;
        playNext(); // Toca o próximo da fila
      };
      
      source.start();
      setIsSpeaking(true);
    } catch (e) {
      console.error('Erro ao tocar áudio da fila:', e);
      isPlayingRef.current = false;
      playNext();
    }
  }, []);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  
  const connect = useCallback(async () => {
    if (globalSocket || globalIsConnecting) {
      console.log("🚫 [Jarvis] Conexão já existente ou em progresso. Ignorando duplicata.");
      return;
    }
    globalIsConnecting = true;
    
    try {
      // Solicita acesso ao microfone
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Salva referência da stream precocemente para o disconnect
      mediaRecorderRef.current = { stream } as any;

      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      
      const wsUrl = process.env.NEXT_PUBLIC_VOICE_WEBSOCKET_URL || `ws://${window.location.hostname}:8000/ws/voice-stream`;
      const ws = new WebSocket(wsUrl);
      
      globalSocket = ws;
      wsRef.current = ws;
      ws.binaryType = 'arraybuffer';
      
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        globalIsConnecting = false;
        
        const source = audioContextRef.current!.createMediaStreamSource(stream);
        const jarvisSpeakingSharedRef = { current: false };
        const processor = audioContextRef.current!.createScriptProcessor(4096, 1, 1);
        
        source.connect(processor);
        processor.connect(audioContextRef.current!.destination);
        
        processor.onaudioprocess = (e) => {
          // Se estiver mutado ou o Jarvis estiver falando (ou tocando áudio), não envia o áudio capturado
          if (ws.readyState === WebSocket.OPEN && !jarvisSpeakingSharedRef.current && !isMutedRef.current && !isPlayingRef.current) {
            const inputData = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
              let s = Math.max(-1, Math.min(1, inputData[i]));
              pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            ws.send(pcm16.buffer);
          }
        };

        (wsRef.current as any).processor = processor;
        (wsRef.current as any).source = source;
        (wsRef.current as any).speakingRef = jarvisSpeakingSharedRef;
      };
      
      ws.onmessage = async (event) => {
        const speakingRef = (wsRef.current as any)?.speakingRef;

        if (event.data instanceof ArrayBuffer && audioContextRef.current) {
            // Em vez de tocar direto, coloca na fila
            audioQueueRef.current.push(event.data);
            playNext();
        } else if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
              setMessages(prev => [...prev, data]);
            } else if (data.type === 'jarvis_speaking') {
              setIsSpeaking(data.state);
              if (speakingRef) speakingRef.current = data.state;
            }
          } catch(e) {}
        }
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        setIsSpeaking(false);
        globalSocket = null;
        globalIsConnecting = false;
      };
      
      ws.onerror = (e) => {
        setError("Erro na conexão com Jarvis Voice Server.");
        setIsConnected(false);
        globalIsConnecting = false;
        globalSocket = null;
      };

    } catch (err: any) {
      globalIsConnecting = false;
      setError(err.message || 'Falha ao acessar microfone.');
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    globalIsConnecting = false;
    if (globalSocket) {
      globalSocket.close();
      globalSocket = null;
    }
    if (wsRef.current) {
      if ((wsRef.current as any).processor) (wsRef.current as any).processor.disconnect();
      if ((wsRef.current as any).source) (wsRef.current as any).source.disconnect();
      wsRef.current = null;
    }
    if (mediaRecorderRef.current && (mediaRecorderRef.current as any).stream) {
      (mediaRecorderRef.current as any).stream.getTracks().forEach((t: any) => t.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    setIsConnected(false);
    setIsSpeaking(false);
  }, []);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  return {
    isConnected,
    isSpeaking,
    isMuted,
    setIsMuted,
    messages,
    error,
    connect,
    disconnect
  };
}
