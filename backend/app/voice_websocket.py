import asyncio
import numpy as np
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.perception.perception_manager import perception_manager
from app.chat_pipeline import chat_stream
from app.voice.tts_engine import tts_engine
from app.voice.barge_in import barge_in
from app.config import settings

router = APIRouter()

_active_ws = None

@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    global _active_ws
    await websocket.accept()
    _active_ws = websocket

    logger.success("🎙️ WebSocket de voz conectado")

    # Cumprimento inicial automático
    await initial_greeting(websocket)

    try:
        while True:
            # Recebe áudio binário do microfone (frontend)
            data = await websocket.receive_bytes() 
            
            # 1. Transcrição (STT)
            text = await process_audio(data)

            if text:
                logger.info(f"Transcrição recebida: {text}")
                
                # 2. Processamento de Resposta (LLM Streaming)
                full_response = ""
                async for chunk in chat_stream("william", text):
                    full_response += chunk
                    await websocket.send_json({"type": "response_chunk", "text": chunk})

                # 3. Conversão para Fala (TTS)
                audio_path = await tts_engine.speak(full_response)
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, "rb") as f:
                        # Envia o áudio completo como bytes após o texto
                        await websocket.send_bytes(f.read())
                    
                    # Cleanup síncrono do arquivo enviado
                    try: os.unlink(audio_path)
                    except: pass

    except WebSocketDisconnect:
        logger.info("Cliente WebSocket de voz desconectado")
    except Exception as e:
        logger.error(f"Erro no WebSocket de voz: {e}")
    finally:
        _active_ws = None

async def initial_greeting(websocket: WebSocket):
    """Cumprimento inteligente no startup."""
    snapshot = perception_manager.get_snapshot()
    # Tenta usar o nome detectado pela visão, fallback para William
    name = snapshot.get("face_identity") or "William"
    
    from app.persona import persona
    greeting = await persona.get_dynamic_greeting(name)
    
    audio_path = await tts_engine.speak(greeting)
    if audio_path and os.path.exists(audio_path):
        try:
            with open(audio_path, "rb") as f:
                await websocket.send_bytes(f.read())
            await websocket.send_json({"type": "response_chunk", "text": greeting})
            os.unlink(audio_path)
        except Exception as e:
            logger.error(f"Erro ao enviar saudação inicial: {e}")

async def process_audio(audio_data: bytes):
    """STT via voice_engine offline."""
    from app.perception.voice_engine import transcribe_offline
    # Converte bytes para numpy array int16 se necessário
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    return transcribe_offline(audio_np)
