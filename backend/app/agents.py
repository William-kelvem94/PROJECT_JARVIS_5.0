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

load_dotenv()

# Map Gemini key to what the plugin expects if needed
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

logger.info(f"LiveKit URL: {os.getenv('LIVEKIT_URL')}")
logger.info(f"Gemini API Key configurada: {'Sim' if os.getenv('GOOGLE_API_KEY') else 'Não'}")



class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext = None):
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.realtime.RealtimeModel(
                voice="Charon",
                temperature=0.6,
            ),
            chat_ctx=chat_ctx,
            tools=[SystemTools()] # Adicionando ferramentas de sistema
        )


async def entrypoint(ctx: agents.JobContext):
    
    async def shutdown_hook():
        logger.info("Shutdown iniciado: salvando contexto do chat na memória...")
        chat_ctx = session.history
        messages_formatted = []
        logger.info(f"Mensagens do chat: {chat_ctx.items}")
        for item in chat_ctx.items:
            if not hasattr(item, 'content') or item.content is None:
                continue
            content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)
            if memory_str and memory_str in content_str:
                continue
            if item.role in ['user', 'assistant']:
                messages_formatted.append({
                    "role": item.role,
                    "content": content_str.strip()
                })
        logger.info(f"Mensagens formatadas para memória: {messages_formatted}")
        try:
            await asyncio.wait_for(
                mem0.add(messages_formatted, user_id="PedroLucas"),
                timeout=5.0,
            )
            logger.info("Contexto do chat salvo na memória.")
        except asyncio.TimeoutError:
            logger.warning("Timeout ao salvar memória, prosseguindo com cleanup.")
        except Exception as e:
            logger.error(f"Falha ao salvar contexto na memória: {e}")

        # Desconectar sessões
        try:
            await session.disconnect()
            logger.info("Sessão desconectada com sucesso.")
        except Exception as e:
            logger.warning(f"Falha ao desconectar sessão: {e}")
        try:
            await ctx.room.disconnect()
            logger.info("Room desconectada com sucesso.")
        except Exception as e:
            logger.warning(f"Falha ao desconectar room: {e}")

    # Initialize Memory Client
    mem0 = AsyncMemoryClient()
    user_id = "PedroLucas"

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
        logger.info("No memories found for this user. Starting fresh conversation.")

    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

    # Na versão 1.4.3 do livekit-agents, o MultimodalAgent não está disponível 
    # como um módulo de alto nível em livekit.agents.multimodal.
    # Usamos o AgentSession + RealtimeModel que é o padrão estável.

    agent = Assistant(chat_ctx=initial_ctx)
    
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            voice="Charon",
            temperature=0.6,
        ),
        vad=silero.VAD.load(),
        # Video sampler allows Gemini to "see" the screen/camera frames
        video_sampler=VoiceActivityVideoSampler(speaking_fps=1.0, silent_fps=0.5),
        tools=[SystemTools()], # Garante que as ferramentas estão disponíveis na sessão
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

