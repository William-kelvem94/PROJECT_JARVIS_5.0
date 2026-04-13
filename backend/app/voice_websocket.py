import asyncio
import io
import wave
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

# Importa as engines nativas que já existem no projeto
from .perception import voice_engine
from .chat_pipeline import chat_reply

HAS_EDGE_TTS = False
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    pass

router = APIRouter()

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
    # Trava global para evitar múltiplos processamentos simultâneos no sistema inteiro
    if _global_processing_lock.locked():
        logger.warning("⚠️ Já existe um processo de voz ativo. Ignorando...")
        return

    async with _global_processing_lock:
        try:
            from .perception.voice_engine import transcribe_offline
            from .chat_pipeline import chat_stream
            
            # 1. Transcrição (STT) - Síncrona (Off-thread)
            text = await asyncio.to_thread(transcribe_offline, audio_int16)
            
            if not text or len(text.strip()) < 2:
                logger.info("❌ Transcrição irrelevante ou ruído.")
                return
                
            logger.success(f"🗣️ Transcrição STT (Usuário): '{text}'")
            try: await websocket.send_json({"type": "message", "role": "user", "text": text})
            except: pass
                
            # 2. Resposta via Streaming
            logger.info("🤖 Iniciando resposta em streaming...")
            sentence_buffer = ""
            full_reply = ""
            
            # Avisa o frontend que o Jarvis começou a falar
            try: await websocket.send_json({"type": "jarvis_speaking", "state": True})
            except: pass

            is_first_chunk = True
            async for chunk in chat_stream("jarvis_user", text):
                sentence_buffer += chunk
                full_reply += chunk
                
                # Se detectarmos fim de frase ou se for o primeiro chunk e for longo o suficiente
                should_trigger = any(p in chunk for p in (".", "!", "?", "\n", ":"))
                if is_first_chunk and len(sentence_buffer) > 25:
                    should_trigger = True
                
                if should_trigger:
                    sentence = sentence_buffer.strip()
                    if len(sentence) > 3:
                        is_first_chunk = False
                        logger.debug(f"🔊 Streaming TTS: {sentence}")
                        audio_bytes = await generate_speech_bytes(sentence)
                        if audio_bytes:
                            try:
                                await websocket.send_bytes(audio_bytes)
                                await websocket.send_json({"type": "message_chunk", "role": "assistant", "text": sentence})
                            except: break
                        sentence_buffer = ""
            
            # Flush final (se sobrou algo no buffer)
            if sentence_buffer.strip():
                audio_bytes = await generate_speech_bytes(sentence_buffer.strip())
                if audio_bytes:
                    try: 
                        await websocket.send_bytes(audio_bytes)
                        await websocket.send_json({"type": "message_chunk", "role": "assistant", "text": sentence_buffer.strip()})
                    except: pass

            logger.success(f"🤖 Resposta completa: '{full_reply}'")
            
            # 3. Finalização
            try:
                # Envia a mensagem completa consolidada para o histórico do UI
                await websocket.send_json({"type": "message", "role": "assistant", "text": full_reply})
                await websocket.send_json({"type": "jarvis_speaking", "state": False})
            except: pass
            
        except Exception as e:
            logger.error(f"Erro crítico no process_and_reply: {e}")
            try: await websocket.send_json({"type": "jarvis_speaking", "state": False})
            except: pass

@router.websocket("/ws/voice-stream")
async def websocket_voice_endpoint(websocket: WebSocket):
    global _active_voice_websocket
    
    await websocket.accept()
    
    # Singleton: Se já existe uma conexão, fecha a antiga para evitar fantasmas
    if _active_voice_websocket:
        try:
            logger.info("♻️ Substituindo conexão WebSocket de voz antiga por uma nova.")
            await _active_voice_websocket.close(code=1000)
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
    audio_buffer = bytearray()
    
    is_speaking = False
    silence_frames = 0
    frames_per_sec = 16000
    
    try:
        while True:
            data = await websocket.receive_bytes()
            
            # Se já estamos processando um áudio anterior ou o Jarvis está falando (lock ativo), ignoramos entrada
            if _global_processing_lock.locked():
                audio_buffer = bytearray()
                continue
                
            chunk_arr = np.frombuffer(data, dtype=np.int16)
            
            # Detecção de energia simplificada
            energy = np.abs(chunk_arr).mean()
            
            if energy > 450: # Threshold ajustado 
                if not is_speaking:
                    is_speaking = True
                    logger.debug("🎙️ Capturando fala...")
                silence_frames = 0
                audio_buffer.extend(data)
            else:
                if is_speaking:
                    silence_frames += len(chunk_arr)
                    audio_buffer.extend(data)
                    
                    # Silêncio detectado (0.8 segundos de margem para resposta mais rápida)
                    if silence_frames > (0.8 * frames_per_sec):
                        logger.info("🗣️ Fim de fala detectado!")
                        full_audio = np.frombuffer(audio_buffer, dtype=np.int16).copy()
                        
                        audio_buffer = bytearray()
                        is_speaking = False
                        silence_frames = 0
                        
                        # Dispara processamento
                        asyncio.create_task(process_and_reply(full_audio, websocket))
                        
    except WebSocketDisconnect:
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        logger.error(f"Erro no WebSocket de Áudio: {e}")
    finally:
        if _active_voice_websocket == websocket:
            _active_voice_websocket = None


