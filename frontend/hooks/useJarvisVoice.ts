import { useState, useRef, useCallback, useEffect } from 'react';

export function useJarvisVoice() {
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const connect = useCallback(async () => {
    try {
      // Solicita acesso ao microfone
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      
      const wsUrl = process.env.NEXT_PUBLIC_VOICE_WEBSOCKET_URL || `ws://${window.location.hostname}:8000/ws/voice-stream`;
      const ws = new WebSocket(wsUrl);
      
      ws.binaryType = 'arraybuffer';
      
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        
        // Inicia a gravação em PCM PCM nativo a 16kHz
        const source = audioContextRef.current!.createMediaStreamSource(stream);
        const processor = audioContextRef.current!.createScriptProcessor(4096, 1, 1);
        
        source.connect(processor);
        processor.connect(audioContextRef.current!.destination); // Necessário para o evento onaudioprocess disparar no Chrome
        
        processor.onaudioprocess = (e) => {
          if (ws.readyState === WebSocket.OPEN) {
            const inputData = e.inputBuffer.getChannelData(0); // Float32Array PCM
            const pcm16 = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
              let s = Math.max(-1, Math.min(1, inputData[i]));
              pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            ws.send(pcm16.buffer);
          }
        };

        // Salvar referência para desconectar depois
        (wsRef as any).processor = processor;
        (wsRef as any).source = source;
        mediaRecorderRef.current = { stream } as any; // mock pra parar tracks depois
      };
      
      ws.onmessage = async (event) => {
        // Recebe bytes PCM de volta do Python e toca!
        if (event.data instanceof ArrayBuffer && audioContextRef.current) {
          setIsSpeaking(true);
          try {
            const audioBuffer = await audioContextRef.current.decodeAudioData(event.data);
            const source = audioContextRef.current.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContextRef.current.destination);
            source.onended = () => setIsSpeaking(false);
            source.start();
          } catch (e) {
            console.error('Error decoding audio from server', e);
            setIsSpeaking(false);
          }
        } else if (typeof event.data === 'string') {
          // Eventos ou JSON de texto/mensagens
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
              setMessages(prev => [...prev, data]);
            }
          } catch(e) {}
        }
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        setIsSpeaking(false);
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stop();
        }
      };
      
      ws.onerror = (e) => {
        setError("Erro na conexão com Jarvis Voice Server.");
        setIsConnected(false);
      };
      
      wsRef.current = ws;

    } catch (err: any) {
      setError(err.message || 'Falha ao acessar microfone.');
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      if ((wsRef as any).processor) {
        (wsRef as any).processor.disconnect();
      }
      if ((wsRef as any).source) {
        (wsRef as any).source.disconnect();
      }
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
    messages,
    error,
    connect,
    disconnect
  };
}
