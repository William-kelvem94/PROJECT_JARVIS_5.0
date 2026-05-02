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
        audio_buffer = bytearray()
        
        while True:
            # Recebe qualquer mensagem do WebSocket
            message = await websocket.receive()
            
            raw_bytes = message.get("bytes")
            if raw_bytes:
                # É um pacote de áudio do microfone
                audio_buffer.extend(raw_bytes)
                
                # Trava de segurança (10s = ~320000 bytes)
                if len(audio_buffer) > 320000:
                    logger.warning("⚠️ Limite de 10s atingido. Forçando corte de áudio.")
                    message["text"] = '{"type": "commit_audio"}'
                    
            raw_text = message.get("text")
            if raw_text:
                # É um comando do frontend
                import json
                try:
                    data = json.loads(raw_text)
                    if data.get("type") == "commit_audio":
                        logger.info(f"🎙️ Comando de parada recebido! Buffer tem {len(audio_buffer)} bytes.")
                        
                        if len(audio_buffer) < 8000:
                            logger.warning("⚠️ Áudio muito curto descartado (menos de 0.5s)")
                            await websocket.send_json({"type": "response_chunk", "text": " "})
                            audio_buffer.clear()
                            continue
                            
                        transcription_data = bytes(audio_buffer)
                        audio_buffer.clear()
                        
                        # --- GRAVAR EM ARQUIVO PARA DEBUG ---
                        try:
                            import wave
                            with wave.open("debug_audio.wav", "wb") as wf:
                                wf.setnchannels(1)
                                wf.setsampwidth(2)
                                wf.setframerate(16000)
                                wf.writeframes(transcription_data)
                            logger.info("💾 Áudio salvo em debug_audio.wav para inspeção.")
                        except Exception as e:
                            logger.error(f"Erro ao salvar debug_audio.wav: {e}")
                        # -------------------------------------
                        
                        # Chama STT sem bloquear o event loop
                        loop = asyncio.get_event_loop()
                        from app.perception.voice_engine import transcribe_offline
                        audio_np = np.frombuffer(transcription_data, dtype=np.int16)
                        
                        logger.info("🧠 Mandando áudio para o Whisper...")
                        text = await loop.run_in_executor(None, transcribe_offline, audio_np)

                        if text:
                            logger.success(f"🗣️ Transcrição recebida: '{text}'")
                            
                            # Processamento de Resposta
                            full_response = ""
                            async for chunk in chat_stream("william", text):
                                full_response += chunk
                                await websocket.send_json({"type": "response_chunk", "text": chunk})

                            # Conversão para Fala (TTS)
                            audio_path = await tts_engine.speak(full_response)
                            if audio_path and os.path.exists(audio_path):
                                with open(audio_path, "rb") as f:
                                    await websocket.send_bytes(f.read())
                                try: os.unlink(audio_path)
                                except: pass
                        else:
                            logger.warning("🚫 Whisper retornou vazio. (Alucinação rejeitada ou áudio ruim)")
                            await websocket.send_json({"type": "response_chunk", "text": " "})
                            
                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        logger.info("🔌 Cliente WebSocket de voz desconectado")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket de voz: {e}")
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
