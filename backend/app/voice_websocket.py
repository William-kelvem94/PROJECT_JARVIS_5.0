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
    # Trava global para evitar múltiplos processamentos simultâneos no sistema inteiro
    if _global_processing_lock.locked():
        logger.warning("⚠️ Já existe um processo de voz ativo. Ignorando...")
        return

    async with _global_processing_lock:
        try:
            from .perception.voice_engine import transcribe_offline
            from .chat_pipeline import chat_stream
            
            # 1. Transcrição (STT) - Síncrona (Off-thread)
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(_voice_executor, voice_engine.transcribe_offline, audio_int16)
            
            if text is None:
                logger.debug("🔇 Nenhuma fala detectada no áudio.")
                return

            # 1.1 Injeta Percepção no Contexto
            perception = perception_manager.get_snapshot()
            
            # Tenta identificar o falante pelo áudio atual (Biometria Vocal)
            speaker_name, speaker_conf = await loop.run_in_executor(_voice_executor, identify_speaker, audio_int16)
            person = speaker_name or perception.get('face_identity') or "Usuário"
            emotion = perception.get('face_emotion', 'neutral')
            
            # Enriquece a mensagem com o que o Jarvis "vê" e "ouve"
            enriched_text = f"Contexto Sensorial -> Falante: {person} (Confiança: {speaker_conf}). Emoção: {emotion}. Mensagem: {text}"
            
            # Ignora se for vazio ou se for uma alucinação comum do Whisper em silêncio
            hallucinations = ["e o que eu vou fazer?", "e o que eu vou fazer..", "obrigado por assistir"]
            clean_text = text.strip().lower()

            if not clean_text or any(h in clean_text for h in hallucinations):
                logger.debug(f"🔇 Silêncio/Ruído ignorado: {text}")
                return
            
            if len(clean_text) < 1: # Aceita qualquer coisa com pelo menos 1 letra
                logger.info("❌ Transcrição muito curta.")
                return
                
            logger.success(f"🗣️ Reconhecido: {person} | '{text}' [{emotion}]")
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
            async for chunk in chat_stream("jarvis_user", enriched_text):
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
            
            # Memory management
            if os.environ.get("JARVIS_ENABLE_GC", "true").lower() == "true":
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
        except Exception as e:
            logger.error(f"Erro crítico no process_and_reply: {e}")
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
            data = await websocket.receive_bytes()
            
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
                # O browser envia em 44.1k ou 48k. O OpenWakeWord quer 16k.
                # Fazemos um subsampling simples (pega 1 a cada 3 amostras aprox)
                # pcm_16k = chunk_arr[::3] 
                chunk_float = chunk_arr.astype(np.float32) / 32768.0
                
                # Só processa se o chunk for do tamanho esperado pelo oww (ou múltiplo)
                if len(chunk_float) >= 1280:
                   prediction = oww.predict(chunk_float)
                   for model, score in prediction.items():
                       if score > 0.45:
                           logger.success(f"🎙️ Wake Word '{model}' detectada via Browser!")
                           await websocket.send_json({"type": "wake_word_detected", "model": model})
            
            # Detecção de energia simplificada - Limiar reduzido para captar sussurros
            energy = np.abs(chunk_arr).mean()
            
            if energy > 250: # Reduzido de 450 para 250 (mais sensível)
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
                        # Resampling Profissional: Determina a taxa de entrada real e converte para 16kHz
                        # A maioria dos browsers envia a 48000Hz.
                        full_audio_raw = np.frombuffer(audio_buffer, dtype=np.int16)
                        
                        # Amostras por segundo recebidas (aproximação baseada no tamanho do buffer acumulado)
                        # Se recebemos X bytes em Y segundos, a taxa é X/2/Y
                        # No WebSocket, processamos em tempo real, então confiamos no step calculado.
                        step = 3 # Padrão para 48kHz -> 16kHz
                        if len(full_audio_raw) < (0.5 * frames_per_sec): # Áudio muito curto
                             step = 1
                        
                        # Garante que o step seja flutuante para precisão se necessário, 
                        # mas para voz int16 o slice [::step] é performático e suficiente
                        full_audio = full_audio_raw[::step].copy()
                        
                        audio_buffer = bytearray()
                        is_speaking = False
                        silence_frames = 0
                        
                        # Dispara processamento em background
                        asyncio.create_task(process_and_reply(full_audio, websocket))
                        
    except WebSocketDisconnect:
        logger.info("🔌 Cliente WebSocket desconectado.")
    except Exception as e:
        logger.error(f"Erro no WebSocket de Áudio: {e}")
    finally:
        if _active_voice_websocket == websocket:
            _active_voice_websocket = None


