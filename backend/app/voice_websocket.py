import asyncio
import io
import os
import wave
import numpy as np
import concurrent.futures
import gc
import torch
import psutil
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from .perception import voice_engine
from .perception.voice_engine import identify_speaker, _get_oww
from .perception.perception_manager import perception_manager
from .chat_pipeline import chat_reply

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
        
        # 2. Filtro de Alucinação / Ruído
        clean_text = text.strip()
        if not clean_text or len(clean_text) < 1:
            return

        # Ajuste de voz para Francisca (mais natural que Antonio)
        voz_jarvis = "pt-BR-FranciscaNeural"

        logger.success(f"📩 Processando para {person}: '{clean_text}' [{emotion}]")
        
        # Envia confirmação de recebimento para o UI
        try: await websocket.send_json({"type": "message", "role": "user", "text": clean_text})
        except: pass
        
        # 3. Brainstorming & Resposta
        enriched_prompt = f"Contexto Sensorial -> Usuário: {person}. Emoção: {emotion}. Mensagem: {text}"
        
        logger.info(f"🤖 Jarvis pensando resposta para {person}...")
        try: await websocket.send_json({"type": "jarvis_speaking", "state": True})
        except: pass

        sentence_buffer = ""
        full_reply = ""
        is_first_chunk = True

        async for chunk in chat_stream("jarvis_user", enriched_prompt):
            sentence_buffer += chunk
            full_reply += chunk
            
            # Streaming TTS (Melhorado: Dispara com pausas naturais)
            should_trigger = any(p in chunk for p in (".", "!", "?", "\n", ";"))
            if is_first_chunk and len(sentence_buffer) > 30:
                should_trigger = True
            
            if should_trigger:
                sentence = sentence_buffer.strip()
                if len(sentence) > 2:
                    is_first_chunk = False
                    audio_bytes = await generate_speech_bytes(sentence, voice=voz_jarvis)
                    if audio_bytes:
                        try:
                            await websocket.send_bytes(audio_bytes)
                            await websocket.send_json({"type": "message_chunk", "role": "assistant", "text": sentence})
                        except: break
                    sentence_buffer = ""
        
        # Flush final
        if sentence_buffer.strip():
            audio_bytes = await generate_speech_bytes(sentence_buffer.strip(), voice=voz_jarvis)
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
            await asyncio.sleep(0.2)
        except: pass
        
    _active_voice_websocket = websocket
    
    logger.info("🎙️ Cliente WebSocket de Áudio conectado.")
    
    # Handshake inicial: solicita configuração do cliente (Bug #5)
    await websocket.send_json({"type": "config_request", "fields": ["sample_rate"]})
    
    # Variável persistente por conexão (Bug #5)
    sample_rate_client = 48000 

    # Cumprimento inicial (Greeting)
    async def initial_greeting():
        percep = perception_manager.get_snapshot()
        user_name = percep.get("face_identity") or "Chefe"
        greeting = f"Olá {user_name}! Sistema JARVIS 5.0 online."
        try:
            audio_bytes = await generate_speech_bytes(greeting, voice="pt-BR-AntonioNeural")
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
                    "gpu": 0,
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
            message = await websocket.receive()
            
            # 1. Áudio Binário (PCM)
            if "bytes" in message:
                data = message["bytes"]
                if _global_processing_lock.locked():
                    continue
                    
                if len(data) % 2 != 0: data = data[:-1]
                chunk_arr = np.frombuffer(data, dtype=np.int16)
                
                # VAD simples
                energy = np.abs(chunk_arr).mean()
                if energy > 250:
                    is_speaking = True
                    silence_frames = 0
                    audio_buffer.extend(data)
                else:
                    if is_speaking:
                        silence_frames += len(chunk_arr)
                        audio_buffer.extend(data)
                        
                        # Silêncio detectado (0.8s)
                        if silence_frames > (0.8 * frames_per_sec):
                            full_audio_raw = np.frombuffer(audio_buffer, dtype=np.int16)
                            
                            # Resampling dinâmico baseado no valor do cliente (Bug #5)
                            # Pelo menos eliminamos o hardcode fixo.
                            in_rate = max(8000, min(96000, sample_rate_client))
                            step = max(1, round(in_rate / 16000))
                            full_audio = full_audio_raw[::step].copy()
                            
                            audio_buffer = bytearray()
                            is_speaking = False
                            silence_frames = 0
                            asyncio.create_task(process_and_reply(full_audio, websocket))
            
            # 2. Comandos JSON
            elif "text" in message:
                try:
                    import json
                    command_data = json.loads(message["text"])
                    
                    # Processa configuração real do cliente (Bug #5)
                    if command_data.get("type") == "config":
                        received_rate = command_data.get("sample_rate", 48000)
                        if 8000 <= received_rate <= 96000:
                            sample_rate_client = received_rate
                            logger.info(f"⚙️ Sample rate ajustada para {sample_rate_client}Hz")
                        continue

                    if command_data.get("type") == "text_message":
                        text_input = command_data.get("text")
                        if text_input:
                            asyncio.create_task(_handle_thinking_and_reply(text_input, websocket))
                except: pass
            
            elif message.get("type") == "websocket.disconnect":
                break
                        
    except WebSocketDisconnect:
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        logger.error(f"Erro no WebSocket de Áudio: {e}")
    finally:
        if _active_voice_websocket == websocket:
            _active_voice_websocket = None


