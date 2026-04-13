import asyncio
import io
import wave
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

# Importa as engines nativas que já existem no projeto
from .perception import voice_engine
from .chat_pipeline import chat_reply

router = APIRouter()

# Buffer state for the active WebSocket connection
active_connections = set()

# Optional: Initialize text-to-speech
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

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

# Trava global para evitar múltiplos processamentos simultâneos na mesma conexão (evita duplicar fala)
class ResponseLock:
    def __init__(self):
        self.locked = False
    
    def lock(self):
        if self.locked: return False
        self.locked = True
        return True
    
    def unlock(self):
        self.locked = False

# Mapeia travas por websocket
connection_locks = {}

async def process_and_reply(audio_int16: np.ndarray, websocket: WebSocket):
    # Verifica se já estamos processando algo para este socket
    lock = connection_locks.get(websocket)
    if lock and not lock.lock():
        return # Já existe um processamento em curso, ignora o novo disparo redundante

    try:
        from .perception.voice_engine import transcribe_offline
        
        # 1. Transcrição (STT)
        text = await asyncio.to_thread(transcribe_offline, audio_int16)
        
        if not text or len(text.strip()) < 2:
            logger.info("❌ Transcrição irrelevante ou ruído.")
            if lock: lock.unlock()
            return
            
        logger.success(f"🗣️ Transcrição STT (Usuário): '{text}'")
        
        try:
            await websocket.send_json({"type": "message", "role": "user", "text": text})
        except: pass
            
        # 2. Resposta da Inteligência (LLM/Pipeline)
        reply_text = ""
        try:
            from .chat_pipeline import chat_reply
            reply_text = await chat_reply("jarvis_user", text)
        except Exception as e:
            logger.error(f"Erro no chat_reply: {e}")
            reply_text = "Desculpe, meu núcleo de raciocínio encontrou um erro."
            
        logger.success(f"🤖 Resposta Jarvis: '{reply_text}'")
        
        try:
            await websocket.send_json({"type": "message", "role": "assistant", "text": reply_text})
        except: pass
            
        # 3. Síntese de Voz (TTS)
        audio_bytes = await generate_speech_bytes(reply_text)
        if audio_bytes:
            try:
                # Avisa o frontend que o Jarvis VAI falar (para o frontend silenciar o MIC se quiser)
                await websocket.send_json({"type": "jarvis_speaking", "state": True})
                await websocket.send_bytes(audio_bytes)
                logger.info("🔊 Áudio enviado ao cliente para reprodução.")
                # Aguarda um tempo estimado de fala para não "se ouvir" imediatamente
                await asyncio.sleep(len(reply_text) * 0.08 + 1.0)
                await websocket.send_json({"type": "jarvis_speaking", "state": False})
            except Exception as e:
                logger.error(f"Erro ao enviar bytes de áudio: {e}")
    finally:
        if lock:
            lock.unlock()

@router.websocket("/ws/voice-stream")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    connection_locks[websocket] = ResponseLock()
    
    logger.info("🎙️ Cliente WebSocket de Áudio conectado (Native Local Voice PCM).")
    audio_buffer = bytearray()
    
    is_speaking = False
    silence_frames = 0
    frames_per_sec = 16000
    
    try:
        while True:
            data = await websocket.receive_bytes()
            chunk_arr = np.frombuffer(data, dtype=np.int16)
            
            # Detecção de energia
            energy = np.abs(chunk_arr).mean()
            
            # Se o Jarvis está falando, ignoramos a entrada para evitar LOOP de "ele se ouvir"
            lock = connection_locks.get(websocket)
            if lock and lock.locked:
                # Enquanto ele processa ou fala, limpamos o buffer e ignoramos entrada
                audio_buffer = bytearray()
                continue

            if energy > 500: # Threshold um pouco mais alto para evitar ruído de fundo
                is_speaking = True
                silence_frames = 0
                audio_buffer.extend(data)
            else:
                if is_speaking:
                    silence_frames += len(chunk_arr)
                    audio_buffer.extend(data)
                    
                    if silence_frames > (1.1 * frames_per_sec):
                        logger.info("🗣️ Fim de fala detectado!")
                        full_audio = np.frombuffer(audio_buffer, dtype=np.int16).copy()
                        
                        # Reseta IMEDIATAMENTE antes de disparar a Task para evitar que novos 
                        # chunks entrem no buffer durante o início do processamento
                        audio_buffer = bytearray()
                        is_speaking = False
                        silence_frames = 0
                        
                        asyncio.create_task(process_and_reply(full_audio, websocket))
                        
    except WebSocketDisconnect:
        if websocket in active_connections: active_connections.remove(websocket)
        if websocket in connection_locks: del connection_locks[websocket]
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        if websocket in active_connections: active_connections.remove(websocket)
        logger.error(f"Erro no WebSocket de Áudio: {e}")

