// Variável global fora do hook para garantir SINGLETON absoluto, mesmo com React StrictMode
let globalSocket: WebSocket | null = null;
let globalIsConnecting = false;

export function useJarvisVoice() {
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  
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

      if (!isConnectingRef.current) {
        // Componente desmontou durante o fallback do microfone
        stream.getTracks().forEach(t => t.stop());
        return;
      }
      
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      
      const wsUrl = process.env.NEXT_PUBLIC_VOICE_WEBSOCKET_URL || `ws://${window.location.hostname}:8000/ws/voice-stream`;
      const ws = new WebSocket(wsUrl);
      
      // Salva referência do socket precocemente
      wsRef.current = ws;
      
      ws.binaryType = 'arraybuffer';
      
      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        
        // Inicia a gravação em PCM nativo a 16kHz
        const source = audioContextRef.current!.createMediaStreamSource(stream);
        // Usamos uma Ref para o loop de áudio ter acesso imediato ao estado de fala (evita lag de state do React)
        const isSpeakingRef = { current: false };

        const processor = audioContextRef.current!.createScriptProcessor(4096, 1, 1);
        
        source.connect(processor);
        processor.connect(audioContextRef.current!.destination);
        
        processor.onaudioprocess = (e) => {
          // SE o Jarvis está falando (localmente ou sinalizado pelo servidor), NÃO mandamos áudio do mic
          if (ws.readyState === WebSocket.OPEN && !isSpeakingRef.current) {
            const inputData = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
              let s = Math.max(-1, Math.min(1, inputData[i]));
              pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            ws.send(pcm16.buffer);
          }
        };

        (wsRef as any).processor = processor;
        (wsRef as any).source = source;
        (wsRef as any).speakingRef = isSpeakingRef;
      };
      
      ws.onmessage = async (event) => {
        const speakingRef = (wsRef as any).speakingRef;

        if (event.data instanceof ArrayBuffer && audioContextRef.current) {
          setIsSpeaking(true);
          if (speakingRef) speakingRef.current = true;

          try {
            const audioBuffer = await audioContextRef.current.decodeAudioData(event.data);
            const source = audioContextRef.current.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContextRef.current.destination);
            source.onended = () => {
              setIsSpeaking(false);
              // Pequeno delay para o mic não abrir EXATAMENTE no fim do áudio (evita captar eco final)
              setTimeout(() => { if (speakingRef) speakingRef.current = false; }, 400);
            };
            source.start();
          } catch (e) {
            console.error('Error decoding audio', e);
            setIsSpeaking(false);
            if (speakingRef) speakingRef.current = false;
          }
        } else if (typeof event.data === 'string') {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
              setMessages(prev => [...prev, data]);
            } else if (data.type === 'jarvis_speaking') {
              // Servidor avisando que começou/terminou de processar algo que resultará em fala
              setIsSpeaking(data.state);
              if (speakingRef) speakingRef.current = data.state;
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
      isConnectingRef.current = false;
      setError(err.message || 'Falha ao acessar microfone.');
      setIsConnected(false);
    }
  }, []);

    globalIsConnecting = false;
    if (globalSocket) {
      globalSocket.close();
      globalSocket = null;
      if (wsRef.current) {
        if ((wsRef.current as any).processor) (wsRef.current as any).processor.disconnect();
        if ((wsRef.current as any).source) (wsRef.current as any).source.disconnect();
        wsRef.current = null;
      }
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
