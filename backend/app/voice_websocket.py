import asyncio
import numpy as np
import os
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from .perception.perception_manager import perception_manager
from .chat_pipeline import chat_stream
from .voice.tts_engine import tts_engine
from .config import settings

router = APIRouter()

# Referência global para o WebSocket ativo para permitir interrupções e gatilhos externos
_active_ws = None

@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    global _active_ws
    await websocket.accept()
    _active_ws = websocket
    logger.success("🎙️ WebSocket conectado - Múltiplos modos ativos (Hey Jarvis / PTT)")

    # Cumprimento inicial inteligente
    await initial_greeting(websocket)

    audio_buffer = bytearray()

    try:
        while True:
            # Recebe pacotes do frontend (bytes para áudio, texto para comandos)
            message = await websocket.receive()
            
            # 1. Processamento de Áudio (Bytes)
            raw_bytes = message.get("bytes")
            if raw_bytes:
                audio_buffer.extend(raw_bytes)
                
                # Trava de segurança (10s = ~320000 bytes em 16kHz 16-bit mono)
                if len(audio_buffer) > 320000:
                    logger.warning("⚠️ Limite de áudio atingido. Processando automaticamente.")
                    await process_and_respond(websocket, bytes(audio_buffer))
                    audio_buffer.clear()

            # 2. Processamento de Comandos (Texto/JSON)
            raw_text = message.get("text")
            if raw_text:
                try:
                    data = json.loads(raw_text)
                    if data.get("type") == "commit_audio":
                        if len(audio_buffer) > 4000: # Mínimo 0.25s
                            audio_to_process = bytes(audio_buffer)
                            audio_buffer.clear()
                            await process_and_respond(websocket, audio_to_process)
                        else:
                            audio_buffer.clear()
                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket de voz desconectado")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
    finally:
        _active_ws = None

async def process_and_respond(websocket: WebSocket, audio_data: bytes):
    """Encaminha o áudio para STT -> LLM -> TTS."""
    from .perception.voice_engine import transcribe_offline
    
    # Transcrição Offline (Whisper)
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    text = await asyncio.get_event_loop().run_in_executor(None, transcribe_offline, audio_np)
    
    if text and text.strip():
        logger.info(f"👤 Usuário disse: {text}")
        
        full_reply = ""
        # Resposta em Streaming para o Frontend (Texto)
        async for chunk in chat_stream("william", text):
            full_reply += chunk
            await websocket.send_json({"type": "response_chunk", "text": chunk})

        # Conversão para Fala (TTS)
        audio_path = await tts_engine.speak(full_reply)
        if audio_path and os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                await websocket.send_bytes(f.read())
            try: os.unlink(audio_path)
            except: pass
    else:
        # Se for ruído ou vazio, avisa o frontend para voltar ao estado idle
        await websocket.send_json({"type": "response_chunk", "text": " "})

async def initial_greeting(websocket: WebSocket):
    """Saudação inicial ao conectar."""
    greeting = "Olá William! JARVIS 5.0 online. Estou ouvindo pelo sistema ou pode clicar no orb."
    audio_path = await tts_engine.speak(greeting)
    if audio_path and os.path.exists(audio_path):
        with open(audio_path, "rb") as f:
            await websocket.send_bytes(f.read())
        await websocket.send_json({"type": "response_chunk", "text": greeting})
        try: os.unlink(audio_path)
        except: pass

# Gatilho externo (ex: Wake Word detectado via Microfone local)
async def external_trigger():
    if _active_ws:
        try:
            # Envia sinal para o frontend começar a gravar ou brilhar
            await _active_ws.send_json({"type": "wake_word_triggered"})
            logger.info("📡 Gatilho externo enviado para o Frontend")
        except:
            pass
