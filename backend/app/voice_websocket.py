import asyncio
import io
import wave
import numpy as np
import concurrent.futures
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import gc
import torch

from .perception import voice_engine
from .perception.voice_engine import identify_speaker, _get_oww
from .perception.perception_manager import perception_manager
from .chat_pipeline import chat_reply
import psutil
import torch

HAS_EDGE_TTS = False
try:
    import edge_tts # type: ignore
    HAS_EDGE_TTS = True
except ImportError:
    pass

router = APIRouter()

# ProcessPoolExecutor for heavy voice processing
_voice_executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)

# Buffer state for the active WebSocket connection
_active_voice_websocket = None
_global_processing_lock = asyncio.Lock()

async def generate_speech_bytes(text: str, voice: str = "pt-BR-AntonioNeural") -> bytes:
    """Gera o áudio a partir do texto usando edge-tts e retorna os bytes do MP3."""
    if not HAS_EDGE_TTS:
        logger.warning("edge-tts não está instalado. Falha ao gerar áudio.")
        return b""
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_stream = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream += chunk["data"]
        return audio_stream
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        return b""

async def process_and_reply(audio_int16: np.ndarray, websocket: WebSocket):
    """Processamento de áudio (STT -> LLM -> TTS)."""
    # Trava global para evitar múltiplos processamentos simultâneos
    if _global_processing_lock.locked():
        logger.warning("⚠️ Já existe um processo de voz ativo. Ignorando...")
        return

    async with _global_processing_lock:
        try:
            from .perception.voice_engine import transcribe_offline, identify_speaker
            
            # 1. Transcrição (STT)
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(_voice_executor, voice_engine.transcribe_offline, audio_int16)
            
            if not text:
                return

            # Tenta identificar o falante pela voz
            speaker_name, speaker_conf = await loop.run_in_executor(_voice_executor, identify_speaker, audio_int16)
            
            await _handle_thinking_and_reply(text, websocket, speaker_name, speaker_conf)
            
        except Exception as e:
            logger.error(f"Erro no process_and_reply: {e}")
            try: await websocket.send_json({"type": "jarvis_speaking", "state": False})
            except: pass

async def _handle_thinking_and_reply(text: str, websocket: WebSocket, speaker_name: str = None, speaker_conf: float = 0.0):
    """Núcleo da lógica de resposta (Comum para Voz e Texto)."""
    try:
        from .chat_pipeline import chat_stream
        
        # 1. Contexto Sensorial
        perception = perception_manager.get_snapshot()
        person = speaker_name or perception.get('face_identity') or "Usuário"
        emotion = perception.get('face_emotion', 'neutral')
        
        # 2. Filtro de Alucinação / Ruído (apenas se vier de voz, mas mantemos limpeza básica)
        clean_text = text.strip()
        if not clean_text or len(clean_text) < 1:
            return

        logger.success(f"📩 Processando para {person}: '{clean_text}' [{emotion}]")
        
        # Envia confirmação de recebimento para o UI
        try: await websocket.send_json({"type": "message", "role": "user", "text": clean_text})
        except: pass
        
        # 3. Brainstorming & Resposta
        enriched_prompt = f"Contexto Sensorial -> Falante: {person}. Emoção: {emotion}. Mensagem: {text}"
        
        logger.info("🤖 Jarvis está pensando...")
        try: await websocket.send_json({"type": "jarvis_speaking", "state": True})
        except: pass

        sentence_buffer = ""
        full_reply = ""
        is_first_chunk = True

        async for chunk in chat_stream("jarvis_user", enriched_prompt):
            sentence_buffer += chunk
            full_reply += chunk
            
            # Streaming TTS (por frase)
            should_trigger = any(p in chunk for p in (".", "!", "?", "\n"))
            if is_first_chunk and len(sentence_buffer) > 25:
                should_trigger = True
            
            if should_trigger:
                sentence = sentence_buffer.strip()
                if len(sentence) > 2:
                    is_first_chunk = False
                    audio_bytes = await generate_speech_bytes(sentence)
                    if audio_bytes:
                        try:
                            await websocket.send_bytes(audio_bytes)
                            await websocket.send_json({"type": "message_chunk", "role": "assistant", "text": sentence})
                        except: break
                    sentence_buffer = ""
        
        # Flush final
        if sentence_buffer.strip():
            audio_bytes = await generate_speech_bytes(sentence_buffer.strip())
            if audio_bytes:
                try: 
                    await websocket.send_bytes(audio_bytes)
                    await websocket.send_json({"type": "message_chunk", "role": "assistant", "text": sentence_buffer.strip()})
                except: pass

        # Sincronização final
        try:
            await websocket.send_json({"type": "message", "role": "assistant", "text": full_reply})
            await websocket.send_json({"type": "jarvis_speaking", "state": False})
        except: pass
        
        # GC
        if os.environ.get("JARVIS_ENABLE_GC", "true").lower() == "true":
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    except Exception as e:
        logger.error(f"Erro no _handle_thinking_and_reply: {e}")
        try: await websocket.send_json({"type": "jarvis_speaking", "state": False})
        except: pass

@router.websocket("/ws/voice-stream")
async def websocket_voice_endpoint(websocket: WebSocket):
    global _active_voice_websocket
    
    await websocket.accept()
    
    # Singleton: Se já existe uma conexão ATIVA e diferente, fecha a antiga
    if _active_voice_websocket and _active_voice_websocket != websocket:
        try:
            logger.info("♻️  Limpando conexão WebSocket anterior...")
            await _active_voice_websocket.close(code=1000)
            await asyncio.sleep(0.2) # Delay para evitar race conditions no cleanup
        except: pass
        
    _active_voice_websocket = websocket
    
    logger.info("🎙️ Cliente WebSocket de Áudio conectado (Native Local Voice PCM).")
    
    # Cumprimento inicial (Greeting)
    async def initial_greeting():
        greeting = "Olá William! Sistema JARVIS 5.0 online."
        try:
            audio_bytes = await generate_speech_bytes(greeting)
            if audio_bytes:
                await websocket.send_bytes(audio_bytes)
                await websocket.send_json({"type": "message", "role": "assistant", "text": greeting})
        except: pass

    asyncio.create_task(initial_greeting())
    
    # Modelo Wake Word
    oww = _get_oww()
    
    # Task de Telemetria (HUD)
    async def telemetry_loop():
        while _active_voice_websocket == websocket:
            try:
                percep = perception_manager.get_snapshot()
                telemetry = {
                    "type": "telemetry_update",
                    "cpu": psutil.cpu_percent(),
                    "ram": psutil.virtual_memory().percent,
                    "gpu": 0, # Placeholder se não tiver GPUtil
                    "face_emotion": percep.get("face_emotion"),
                    "face_identity": percep.get("face_identity"),
                    "is_reasoning": _global_processing_lock.locked(),
                    "model": "WILL-JARVIS 5.0"
                }
                await websocket.send_json(telemetry)
            except: break
            await asyncio.sleep(2.0)

    asyncio.create_task(telemetry_loop())
    audio_buffer = bytearray()
    
    is_speaking = False
    silence_frames = 0
    frames_per_sec = 16000
    
    try:
        while True:
            # Recebe a mensagem genérica do WebSocket (pode ser Bytes ou Texto JSON)
            message = await websocket.receive()
            
            # 1. Tratamento de Áudio Binário (PCM)
            if "bytes" in message:
                data = message["bytes"]
                
                # Se já estamos processando um áudio anterior ou o Jarvis está falando (lock ativo), ignoramos entrada
                if _global_processing_lock.locked():
                    audio_buffer = bytearray()
                    continue
                    
                # Proteção: Garante que os bytes sejam múltiplos de 2 (int16)
                if len(data) % 2 != 0:
                    data = data[:-1]
                    
                chunk_arr = np.frombuffer(data, dtype=np.int16)
                
                # Detecção de Wake Word (Hey Jarvis) no stream do browser
                if oww:
                    chunk_float = chunk_arr.astype(np.float32) / 32768.0
                    if len(chunk_float) >= 1280:
                       prediction = oww.predict(chunk_float)
                       for mw, score in prediction.items():
                           if score > 0.45:
                               logger.success(f"🎙️ Wake Word '{mw}' detectada!")
                               await websocket.send_json({"type": "wake_word_detected", "model": mw})
                
                # Detecção de energia para VAD (Voice Activity Detection)
                energy = np.abs(chunk_arr).mean()
                if energy > 250:
                    if not is_speaking:
                        is_speaking = True
                        logger.debug("🎙️ Capturando fala...")
                    silence_frames = 0
                    audio_buffer.extend(data)
                else:
                    if is_speaking:
                        silence_frames += len(chunk_arr)
                        audio_buffer.extend(data)
                        
                        # Silêncio detectado (0.8 segundos)
                        if silence_frames > (0.8 * frames_per_sec):
                            full_audio_raw = np.frombuffer(audio_buffer, dtype=np.int16)
                            step = 3 # 48k -> 16k
                            full_audio = full_audio_raw[::step].copy()
                            
                            audio_buffer = bytearray()
                            is_speaking = False
                            silence_frames = 0
                            
                            # Dispara processamento em background
                            asyncio.create_task(process_and_reply(full_audio, websocket))
            
            # 2. Tratamento de Comandos JSON (Texto)
            elif "text" in message:
                try:
                    import json
                    command_data = json.loads(message["text"])
                    
                    if command_data.get("type") == "text_message":
                        text_input = command_data.get("text")
                        if text_input:
                            logger.info(f"⌨️ Mensagem de Texto Recebida: {text_input}")
                            # Dispara o pensamento para o texto
                            asyncio.create_task(_handle_thinking_and_reply(text_input, websocket))
                    
                except Exception as e:
                    logger.error(f"Erro ao processar comando JSON: {e}")
            
            # 3. Tratamento de Desconexão
            elif message.get("type") == "websocket.disconnect":
                break
                        
    except WebSocketDisconnect:
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        logger.error(f"Erro no WebSocket de Áudio: {e}")
    finally:
        if _active_voice_websocket == websocket:
            _active_voice_websocket = None


