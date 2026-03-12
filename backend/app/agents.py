from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext, AutoSubscribe
from livekit.agents.voice import VoiceActivityVideoSampler
from livekit.plugins import noise_cancellation, google, silero
from .prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from .system_tools import SystemTools
from .mem0 import AsyncMemoryClient
from loguru import logger
import os
import json
import asyncio

load_dotenv(override=True)

# Injeta a chave do projeto de forma limpa
# O SDK google-genai prefere GOOGLE_API_KEY. Vamos unificar para evitar conflitos.
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if gemini_key:
    # Define GOOGLE_API_KEY e remove GEMINI_API_KEY para evitar warning de chave duplicada do SDK
    os.environ["GOOGLE_API_KEY"] = gemini_key
    os.environ.pop("GEMINI_API_KEY", None)
    logger.info("GOOGLE_API_KEY configurada.")
else:
    logger.critical("ERRO: Nenhuma chave de API (GEMINI ou GOOGLE) encontrada no .env!")

logger.info(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
logger.info(f"Gemini API Key configurada: {'Sim' if os.getenv('GOOGLE_API_KEY') else 'Não'}")



# Modelo gratuito com suporte a bidiGenerateContent (Gemini Live API)
GEMINI_LIVE_MODEL = "gemini-2.5-flash-native-audio-latest"

class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext = None):
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.realtime.RealtimeModel(
                model=GEMINI_LIVE_MODEL,
                voice="Charon",
                temperature=0.6,
            ),
            chat_ctx=chat_ctx
        )


async def entrypoint(ctx: agents.JobContext):
    
    # Prefixes/substrings that identify system-injected messages (never save as memories)
    _SYSTEM_MARKERS = [
        SESSION_INSTRUCTION.strip()[:60],
        "Apresente-se brevemente",
        "#Tarefa",
        "Forneça assistência usando as ferramentas",
    ]

    async def shutdown_hook():
        logger.info("Shutdown iniciado: salvando contexto do chat na memória...")
        chat_ctx = session.history
        messages_formatted = []
        logger.info(f"Mensagens do chat: {chat_ctx.items}")
        for item in chat_ctx.items:
            if not hasattr(item, 'content') or item.content is None:
                continue
            content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)
            content_stripped = content_str.strip()

            # Filter out empty, system prompts and memory injections
            if not content_stripped:
                continue
            if memory_str and memory_str in content_str:
                continue
            if any(marker in content_stripped for marker in _SYSTEM_MARKERS):
                continue
            # Skip very short responses (greetings, acknowledgements)
            if len(content_stripped) < 10:
                continue

            if item.role in ['user', 'assistant']:
                messages_formatted.append({
                    "role": item.role,
                    "content": content_stripped
                })

        logger.info(f"Mensagens reais da sessão: {len(messages_formatted)} mensagens filtradas.")
        try:
            await asyncio.wait_for(
                mem0.add(messages_formatted, user_id=user_id),
                timeout=8.0,
            )
            stats = mem0.get_local_stats(user_id)
            logger.info(f"Memória salva para {user_id}. Stats locais: {stats}")
        except asyncio.TimeoutError:
            logger.warning("Timeout ao salvar memória, prosseguindo com cleanup.")
        except Exception as e:
            logger.error(f"Falha ao salvar contexto na memória: {e}")

        # Desconectar sessões de forma segura
        try:
            # AgentSession não tem disconnect(), usa-se end() para encerramento limpo
            # Mas geralmente session.start() já gerencia o ciclo de vida.
            pass
        except Exception as e:
            logger.warning(f"Falha ao limpar sessão: {e}")
        # Stop perception engines gracefully
        try:
            from .perception import perception_manager
            perception_manager.stop()
        except Exception:
            pass

        try:
            await ctx.room.disconnect()
            logger.info("Room desconectada com sucesso.")
        except Exception as e:
            logger.warning(f"Falha ao desconectar room: {e}")

    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    
    # Extração dinâmica de identidade do usuário
    user_id = "Chefe" # Default genérico
    for participant in ctx.room.remote_participants.values():
        if participant.metadata:
            try:
                metadata = json.loads(participant.metadata)
                if "user_name" in metadata:
                    user_id = metadata["user_name"]
                    logger.success(f"Identidade do usuário detectada: {user_id}")
                    break
            except:
                pass
    
    # Initialize Memory Client
    mem0 = AsyncMemoryClient()
    # Load existing memories - try get_all first, fallback to search
    initial_ctx = ChatContext()
    memory_str = ''
    results = []
    
    try:
        # Try to get all memories for the user
        results = await mem0.get_all(user_id=user_id)
        logger.info(f"Retrieved {len(results) if results else 0} memories using get_all")
    except Exception as e:
        logger.warning(f"get_all failed: {e}. Trying search method...")
        try:
            # Fallback: use search with a broad query (empty query causes 400 error)
            response = await mem0.search("informações preferências contexto", filters={"user_id": user_id})
            results = response["results"] if isinstance(response, dict) and "results" in response else response
            logger.info(f"Retrieved {len(results) if results else 0} memories using search")
        except Exception as e2:
            logger.warning(f"Search also failed: {e2}. No memories loaded.")
            results = []

    if results:
        memories = [
            {
                "memory": result.get("memory") if isinstance(result, dict) else result.get("memory", ""),
                "updated_at": result.get("updated_at") if isinstance(result, dict) else result.get("updated_at", "")
            }
            for result in results
            if isinstance(result, dict) and result.get("memory")
        ]
        
        if memories:
            memory_str = json.dumps(memories, ensure_ascii=False)
            logger.info(f"Formatted memories: {memory_str}")
            initial_ctx.add_message(
                role="assistant",
                content=f"O nome do usuário é {user_id}. Aqui estão informações importantes sobre ele que você deve lembrar e usar nas conversas: {memory_str}."
            )
    else:
        logger.info(f"Nenhuma memória encontrada para {user_id}. Iniciando conversa limpa.")

    # Na versão 1.4.3 do livekit-agents, o MultimodalAgent não está disponível 
    # como um módulo de alto nível em livekit.agents.multimodal.
    # Usamos o AgentSession + RealtimeModel que é o padrão estável.

    async def telemetry_loop():
        import psutil
        logger.info("Iniciando loop de telemetria...")
        counter = 0
        while True:
            try:
                if ctx.room.connection_state == "connected":
                    cpu = psutil.cpu_percent()
                    ram = psutil.virtual_memory().percent
                    battery = psutil.sensors_battery()
                    batt_pct = battery.percent if battery else 100
                    
                    telemetry = {
                        "type": "telemetry_update",
                        "cpu": cpu,
                        "ram": ram,
                        "battery": batt_pct,
                        "model": "Gemini 2.0 Flash",
                        "persona": agent_persona
                    }

                    # Reduzimos a frequência do GPU stats para evitar picos de latência
                    if counter % 10 == 0: # A cada 100s para telemetria rica
                        try:
                            import GPUtil
                            gpus = GPUtil.getGPUs()
                            if gpus:
                                gpu = gpus[0]
                                telemetry["gpu"] = gpu.load * 100
                                telemetry["gpu_mem"] = gpu.memoryUtil * 100
                                telemetry["gpu_name"] = gpu.name
                                logger.info(f"[HARDWARE] Detectado: {gpu.name} | VRAM: {gpu.memoryTotal}MB")
                        except: 
                            pass
                    
                    counter += 1

                    await ctx.room.local_participant.publish_data(
                        json.dumps(telemetry),
                        topic="telemetry"
                    )
                    # Debug log apenas (menos verboso)
                    logger.debug(f"[PERF] CPU: {cpu}% | RAM: {ram}%")
                # Sleep adaptativo: 15s de intervalo para telemetria
                await asyncio.sleep(15)
            except Exception as e:
                logger.error(f"Erro no loop de telemetria: {e}")
                await asyncio.sleep(10)
    async def watchdog_loop():
        from .utils.workflow_engine import workflow_engine
        logger.info("Iniciando loop de Watchdogs...")
        while True:
            try:
                if ctx.room.connection_state == "connected":
                    alerts = await workflow_engine.check_watchdogs()
                    for alert in alerts:
                        packet = {
                            "type": "activity_log",
                            "title": alert["title"],
                            "detail": alert["detail"],
                            "log_type": "info",
                            "status": "success",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        await ctx.room.local_participant.publish_data(
                            json.dumps(packet),
                            topic="activity"
                        )
                        # Salva no log persistente também
                        from .utils.log_manager import log_manager
                        log_manager.save_log(packet)
            except Exception as e:
                logger.error(f"Erro no loop de watchdogs: {e}")
            # Sleep aumentado para 20s (ADA Optimization)
            await asyncio.sleep(20)

    # Start loops
    agent_persona = "jarvis" # Default
    asyncio.create_task(telemetry_loop())
    asyncio.create_task(watchdog_loop())

    # Start perception engines (face + gesture + voice) — non-blocking, fail-safe
    try:
        from .perception import perception_manager

        def _wake_word_handler():
            """Called from voice engine thread when wake word fires."""
            asyncio.run_coroutine_threadsafe(
                session.generate_reply(
                    user_input="(wake word detectado — o usuário quer atenção)"
                ),
                asyncio.get_event_loop(),
            )

        perception_manager.on_wake_word(_wake_word_handler)

        def _gesture_handler(gesture, side):
            """Invoked when a proactive gesture is detected."""
            logger.info(f"[Proactive] Reagindo ao gesto {gesture} ({side})...")
            # Injeta uma instrução silenciosa no Gemini para ele decidir o que fazer
            asyncio.run_coroutine_threadsafe(
                session.generate_reply(
                    user_input=f"(O usuário fez o gesto {gesture}. Execute a ação apropriada ou pergunte se ele precisa de algo.)"
                ),
                asyncio.get_event_loop(),
            )

        perception_manager.on_gesture(_gesture_handler)
        perception_manager.start(room=ctx.room)
        asyncio.create_task(perception_manager.publish_loop())
        logger.success("[Perception] 🧠 Face + Gesture + Voice engines online")
    except Exception as _perc_err:
        logger.warning(f"[Perception] Engine not started (non-fatal): {_perc_err}")

    # --- Dynamic System Instruction with Perception ---
    async def get_dynamic_instruction():
        try:
            from .perception import perception_manager
            snap = perception_manager.get_snapshot()
            status = (
                f"\n[SITUAÇÃO ATUAL]\n"
                f"Usuário detectado: {'Sim' if snap['face_present'] else 'Não'}\n"
                f"Identidade: {snap['face_identity'] or 'Desconhecido'}\n"
                f"Emoção dominante: {snap['face_emotion']}\n"
                f"Gesto detectado: {snap['hand_gesture'] or 'Nenhum'}\n"
            )
            return AGENT_INSTRUCTION + status
        except:
            return AGENT_INSTRUCTION

    agent = Assistant(chat_ctx=initial_ctx)
    
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model=GEMINI_LIVE_MODEL,
            voice="Charon",
            temperature=0.6,
            instructions=await get_dynamic_instruction()
        ),
        vad=silero.VAD.load(),
        video_sampler=VoiceActivityVideoSampler(speaking_fps=2.0, silent_fps=0.5), # Aumentado para melhor percepção visual
        tools=[
            *agents.llm.find_function_tools(SystemTools(room=ctx.room)),
            google.tools.GoogleSearch()
        ],
    )

    logger.info("Configurando a sessão do Agente com Gemini Realtime...")
    
    # Event listeners na SESSION, não no agent (v1.4.3)
    @session.on("user_state_changed")
    def on_user_state_changed(ev):
        if ev.new_state == "speaking":
             logger.info("🎤 Usuário começou a falar...")
        elif ev.new_state == "listening":
             logger.info("👂 Aguardando resposta do Gemini...")

    @session.on("agent_state_changed")
    def on_agent_state_changed(ev):
        if ev.new_state == "speaking":
            logger.success("🤖 Gemini começou a responder.")
        elif ev.new_state == "thinking":
            logger.info("🧠 Gemini está processando...")

    @session.on("error")
    def on_error(ev):
        logger.error(f"🚨 Erro na sessão: {ev.error}")

    try:
        # Habilitamos explicitamente a captura de vídeo (screen share/camera)
        room_options = agents.voice.room_io.RoomOptions(
            video_input=True, # IMPORTANTE: permite ao agente ver vídeo
            audio_input=True,
            audio_output=True,
            text_output=True
        )
        
        # Iniciamos a sessão passando o agente, room e as opções de vídeo
        await session.start(agent=agent, room=ctx.room, room_options=room_options)
        logger.info("✔️ Sessão do Agente iniciada e conectada na Room com Visão Habilitada.")
    except Exception as e:
        logger.error(f"Falha ao iniciar o Agente na sala: {e}")
        raise e

    # Use a shutdown callback to capture the context at the end
    ctx.add_shutdown_callback(lambda: asyncio.create_task(shutdown_hook()))

    await session.generate_reply(
        user_input=f"Apresente-se brevemente. {SESSION_INSTRUCTION}"
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )

