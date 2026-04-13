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

async def process_and_reply(audio_int16: np.ndarray, websocket: WebSocket):
    from .perception.voice_engine import transcribe_offline
    
    # 1. Transcrição (STT) - Roda em thread pool para nao travar o loop assíncrono
    text = await asyncio.to_thread(transcribe_offline, audio_int16)
    
    if not text:
        logger.info("❌ Transcrição vazia ou ruído ignorado.")
        return
        
    logger.success(f"🗣️ Transcrição STT (Usuário): '{text}'")
    
    try:
        await websocket.send_json({"type": "message", "role": "user", "text": text})
    except Exception:
        pass
        
    # 2. Resposta da Inteligência (LLM/Pipeline)
    # Por segurança, mockamos resposta caso o pipeline esteja instável
    reply_text = ""
    try:
        # A API "chat_reply" pode ser síncrona ou assíncrona dependendo de como foi feita no projeto
        # Se ela contiver chamadas de rede bloqueantes, to_thread é seguro.
        reply_text = await asyncio.to_thread(chat_reply, text)
    except Exception as e:
        logger.error(f"Erro no chat_reply: {e}")
        reply_text = "Desculpe, meu núcleo de raciocínio encontrou um erro."
        
    logger.success(f"🤖 Resposta Jarvis: '{reply_text}'")
    
    try:
        await websocket.send_json({"type": "message", "role": "assistant", "text": reply_text})
    except Exception:
        pass
        
    # 3. Síntese de Voz (TTS)
    audio_bytes = await generate_speech_bytes(reply_text)
    if audio_bytes:
        try:
            # O Frontend tenta tocar diretamente os bytes que enviarmos (mp3/wav) usando o decodeAudioData
            await websocket.send_bytes(audio_bytes)
            logger.info("🔊 Áudio enviado ao cliente para reprodução.")
        except Exception as e:
            logger.error(f"Erro ao enviar bytes de áudio: {e}")

@router.websocket("/ws/voice-stream")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("🎙️ Cliente WebSocket de Áudio conectado (Native Local Voice PCM).")
    
    # Cada conexao possui seu próprio buffer de áudio (16000 Hz, Mono, Int16)
    audio_buffer = bytearray()
    
    is_speaking = False
    silence_frames = 0
    frames_per_sec = 16000
    
    try:
        while True:
            # Recebe chunks de áudio (Binários PCM Raw - 16 bit Int)
            data = await websocket.receive_bytes()
            
            # Converter bytes para array int16 do numpy
            chunk_arr = np.frombuffer(data, dtype=np.int16)
            
            # Calcular energia acústica do chunk (Valor Absoluto Médio)
            energy = np.abs(chunk_arr).mean()
            
            # Definindo um limite (threshold) dinâmico mas base de ~300 para ativar
            if energy > 400:
                is_speaking = True
                silence_frames = 0
                audio_buffer.extend(data)
            else:
                if is_speaking:
                    silence_frames += len(chunk_arr)
                    audio_buffer.extend(data)
                    
                    # Se tivemos ~1.2 segundos de silêncio, a fala terminou
                    if silence_frames > (1.2 * frames_per_sec):
                        logger.info("🗣️ Fim de fala detectado! Processando áudio capturado...")
                        
                        # Extrai o áudio para Numpy e manda processar em Task separada
                        full_audio = np.frombuffer(audio_buffer, dtype=np.int16).copy()
                        asyncio.create_task(process_and_reply(full_audio, websocket))
                        
                        # Reseta para escutar o próximo comando
                        audio_buffer = bytearray()
                        is_speaking = False
                        silence_frames = 0
                        
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.error(f"Erro no WebSocket de Áudio: {e}")
