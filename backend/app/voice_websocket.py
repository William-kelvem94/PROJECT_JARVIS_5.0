import asyncio
from asyncio import Lock
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from .voice.tts_engine import tts_engine

# Store background tasks to prevent garbage collection
_background_tasks: set[asyncio.Task] = set()

router = APIRouter()

# Referência global para o WebSocket ativo para permitir interrupções e gatilhos externos
_active_ws = None
_ws_lock = Lock()

@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    global _active_ws
    await websocket.accept()
    async with _ws_lock:
        _active_ws = websocket
    logger.success("🎙️ HUD Conectado (Apenas Telemetria)")

    # Cumprimento inicial pelo backend (Toca localmente, mas avisa o HUD para animar)
    await initial_greeting()

    try:
        while True:
            # Recebe pacotes do frontend (Apenas comandos JSON agora)
            message = await websocket.receive()
            raw_text = message.get("text")
            raw_bytes = message.get("bytes")
            
            if raw_text:
                try:
                    data = json.loads(raw_text)
                    if data.get("type") == "manual_trigger":
                        # Clicou no Orb - Força o backend a escutar
                        from .perception.voice_engine import force_listen
                        task = asyncio.create_task(force_listen())
                        _background_tasks.add(task)
                        task.add_done_callback(_background_tasks.discard)
                except json.JSONDecodeError:
                    pass
            elif raw_bytes:
                try:
                    import numpy as np
                    from .perception.voice_engine import _chunk_q

                    chunk_int16 = np.frombuffer(raw_bytes, dtype=np.int16)
                    if _chunk_q.qsize() < 100:
                        _chunk_q.put_nowait(chunk_int16)
                except Exception as e:
                    pass

    except WebSocketDisconnect:
        logger.info("🔌 HUD Desconectado")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
    finally:
        async with _ws_lock:
            if _active_ws == websocket:
                _active_ws = None

async def initial_greeting():
    """Saudação inicial ao conectar o HUD."""
    greeting = "Olá Chefe! HUD conectado e sistemas operacionais online."
    await broadcast_state("speaking", response=greeting)
    
    # Roda o TTS em background para não travar o loop do websocket
    task = asyncio.create_task(tts_engine.speak(greeting, play_local=True))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    
    # Simula o tempo da fala e volta pro idle
    await asyncio.sleep(4)
    await broadcast_state("idle")

# --- FUNÇÕES DE BROADCAST (TELEMETRIA VISUAL) ---

async def broadcast_state(status: str, transcript: str = "", response: str = ""):
    """
    Informa o Frontend (HUD) do estado atual do Backend.
    status: 'idle', 'listening', 'thinking', 'speaking'
    """
    async with _ws_lock:
        ws = _active_ws
    if ws:
        try:
            payload = {"type": "status_update", "status": status}
            if transcript: payload["transcript"] = transcript
            if response: payload["response"] = response
            await ws.send_json(payload)
        except Exception as e:
            logger.debug(f"Falha ao enviar telemetria: {e}")

async def broadcast_chunk(chunk: str):
    """Envia pedaços da resposta para o HUD exibir em tempo real."""
    async with _ws_lock:
        ws = _active_ws
    if ws:
        try:
            await ws.send_json({"type": "response_chunk", "text": chunk})
        except:
            pass

async def broadcast_audio_file(filepath: str):
    """Lê o arquivo de áudio gerado pelo TTS e envia os bytes (binário) para o WebSocket."""
    async with _ws_lock:
        ws = _active_ws
    if ws and filepath:
        try:
            import aiofiles
            async with aiofiles.open(filepath, mode="rb") as f:
                data = await f.read()
                await ws.send_bytes(data)
        except Exception as e:
            logger.debug(f"Falha ao enviar arquivo de áudio: {e}")
