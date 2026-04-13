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

@router.websocket("/ws/voice-stream")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("🎙️ Cliente WebSocket de Áudio conectado (Native Local Voice).")
    
    # Cada conexao possui seu próprio buffer de áudio (16000 Hz, Mono, Int16)
    audio_buffer = bytearray()
    
    try:
        while True:
            # Recebe chunks de áudio (Binários PCM)
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            # TODO: Fase 2 - Detectar fim de fala usando VAD do `voice_engine`.
            # Por enquanto acumulamos. A detecção do "fim da frase" vai disparar
            # a transcrição + chat_reply + TTS.
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.error(f"Erro no WebSocket de Áudio: {e}")
