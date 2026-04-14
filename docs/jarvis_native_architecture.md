# Nova Arquitetura Nativa: Voz do Jarvis 5.0

Este documento descreve como a arquitetura do **Jarvis 5.0** foi reestruturada para operar de forma 100% offline, ágil e privada, abandonando as dependências de nuvem como LiveKit e Workers na nuvem.

## 1. Visão Geral (Do LiveKit para o Native WebSocket)

O modelo antigo dependia de uma "sala LiveKit" hospedada na nuvem. O navegador do usuário se conectava a essa sala, e um script Python independente (`agents_worker.py`) se conectava à mesma sala para capturar e enviar o áudio processado. 

No novo modelo **Jarvis Native (Offline)**, utilizamos uma arquitetura Cliente-Servidor simples e direta, de baixíssima latência:
1. O Frontend (Next.js) envia a sua voz em `bytes brutos` diretamente pela rede local.
2. O Backend (FastAPI em `backend/app/voice_websocket.py`) escuta essa conexão nativamente e coordena todas as inteligências de áudio, IA generativa e síntese vocal.

---

## 2. Fase 1: Limpeza do Terreno (Remoção do LiveKit)

### Componentes de UI Limpos:
Diversos componentes do Frontend travavam por tentar localizar a "Sessão da Nuvem" (`useRoomContext`). Todos os hooks do LiveKit foram neutralizados ou comentados em:
*   `active-console.tsx`: O console lateral. 
*   `engineering-hud.tsx`: O relógio/módulo de telemetria lateral. Adicionado "Mocks Virtuais" visuais temporários.
*   `vanta-engine.tsx`: O orbe holográfico central (reage visualmente com hooks autônomos sem precisar do LiveKit).
*   `chat-transcript.tsx`: A transcrição de texto.
*   `useDebug.ts`: Remoção do rastro de log do LiveKit exposto pelo navegador.

---

## 3. Fase 2: Construção do "Pipelines" Offline

A fase central, estabelecendo o fluxo real da voz ponta-a-ponta, 100% isolado.

### 🎤 O Ouvido (Frontend VAD)
No arquivo `frontend/hooks/useJarvisVoice.ts`, mudamos a forma de captura do áudio. 
Em vez de gravar empacotando *trilhas de vídeo comprimido* (arquivos `audio/webm` via `MediaRecorder`), ligamos a **Web Audio API** (`ScriptProcessorNode`) diretamente ao socket.

**Funcionalidade:**
- O microfone capta a voz pelo navegador do cliente.
- A configuração da amostragem do som é forçada em taxa constante de **16000 Hz**.
- Os trechos fracionados de décimos de segundos da voz (`Float32Array`) são convertidos "on-the-fly" para números inteiros puros (`Int16 PCM raw bytes`) e transportados instantaneamente pela rede via `WebSocket`.  

### 🧠 A Inteligência (Backend VAD)
No arquivo `backend/app/voice_websocket.py`, recebemos a voz crua a cada `0.2s`.

#### Sistema de Energia (VAD de Processamento Zero)
Como a FastAPI no backend lida com os bytes? 
Em vez de depender de pacotes assíncronos pesados, configuramos um analisador matemático nativo e hiperveloz (usa matriz do `NumPy`):
- O código tira uma amostragem do valor absoluto médio (RMS - _Root Mean Square_) da energia sonora.
- Limite (Threshold): **> 400**.
- **Se > 400:** O usuário está falando. O buffer acústico é acumulado rapidamente.
- **Se < 400 (Silêncio):** Inicia-se a contagem. Bateu **1.2 segundos** de tempo mudo, concluímos que o usuário encerrou a fala (VAD).

#### Delegados Off-Thread (STT e TTS)
Quando a "frase termina" e fechamos o buffer, criamos uma tarefa (`asyncio.create_task`) isolada e disparada via chamadas de Threads assíncronas do interpretador (evitando desligar a rede do WebSocket no momento da análise):
1.  Transcreve offline passando o Numpy Integer (*Fast_Whisper* nativo em `voice_engine`).
2.  Dispara os dados obtidos para os LLMs da rede que estão instanciados (*chat_pipeline*).
3.  Recebe as strings geradas de texto, retorna o log via JSON de mensagens, empacota os bytes MP3 em áudio final de alto requinte (`edge_tts` no momento, customizável).

O frontend, ao receber de volta pelo WebSocket, converte esses bytes decodificados (`audioContext.decodeAudioData`) e a voz natural sai direto nos alto-falantes – concluindo a latência da malha local offline perfeitamente.
