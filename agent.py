import logging
import psutil
import subprocess
import os
from typing import Annotated
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import llm, voice, WorkerOptions
from livekit.plugins import google, noise_cancellation
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION

load_dotenv()

# Logger Stark
logger = logging.getLogger("jarvis-agent")
logger.setLevel(logging.INFO)

class JarvisMemory:
    def __init__(self, user_name="WilliamPereira"):
        self.user_name = user_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from mem0 import MemoryClient
                self._client = MemoryClient()
            except ImportError:
                logger.error("Biblioteca mem0ai não encontrada.")
                return None
        return self._client

    def buscar(self, query: str):
        if not self.client:
            return []
        try:
            response = self.client.search(query, filters={"user_id": self.user_name})
            results = response["results"] if isinstance(response, dict) and "results" in response else response
            return [item.get("memory") for item in results if isinstance(item, dict) and "memory" in item]
        except Exception as e:
            logger.error(f"Erro ao buscar memória: {e}")
            return []

class JarvisTools:
    """
    Protocolos de Elite: Ferramentas de Interação de Nível Stark.
    Dedicado ao Mestre WilliamPereira.
    """
    def __init__(self, user_name="WilliamPereira"):
        self.memory = JarvisMemory(user_name)
    
    @llm.function_tool
    def get_system_status(self) -> str:
        """Retorna o status atual dos recursos do computador (CPU, RAM, Bateria)."""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        batt_str = f"{battery.percent}%" if battery else "N/A"
        return f"CPU: {cpu}%, RAM: {ram}%, Bateria: {batt_str}. Sistemas nominais, Senhor William."

    @llm.function_tool
    def read_project_file(self, file_path: Annotated[str, "Caminho do arquivo."]) -> str:
        """Lê o conteúdo de um arquivo específico do projeto."""
        try:
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Erro ao ler: {str(e)}"

    @llm.function_tool
    def write_project_file(self, 
                           file_path: Annotated[str, "Caminho do arquivo."], 
                           content: Annotated[str, "Conteúdo a ser escrito."]) -> str:
        """Cria ou modifica um arquivo no sistema (Auto-desenvolvimento)."""
        try:
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Arquivo {file_path} foi atualizado/criado com sucesso, Senhor William."
        except Exception as e:
            return f"Erro na escrita: {str(e)}"

    @llm.function_tool
    def execute_terminal_command(self, command: Annotated[str, "O comando shell para rodar."]) -> str:
        """Executa um comando no terminal do Windows (Instalações, scripts, etc)."""
        try:
            logger.warning(f"EXECUTANDO COMANDO: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return f"Saída do Mestre William:\n{result.stdout}\n{result.stderr}"
        except Exception as e:
            return f"Falha na execução: {str(e)}"

    @llm.function_tool
    def search_long_term_memory(self, query: Annotated[str, "O que você quer lembrar?"]) -> str:
        """Busca memórias de longo prazo sobre o Mestre WilliamPereira."""
        memories = self.memory.buscar(query)
        if memories:
            return f"Dados encontrados para o Senhor William: {', '.join(memories)}"
        return "Nenhuma memória específica encontrada sobre isso para o William."

async def entrypoint(ctx: agents.JobContext):
    logger.info(f"Conectando à sala: {ctx.room.name}")
    await ctx.connect()

    fnc_ctx = JarvisTools(user_name="WilliamPereira")
    tools = llm.find_function_tools(fnc_ctx)

    agent = voice.Agent(
        instructions=AGENT_INSTRUCTION,
        llm=google.beta.realtime.RealtimeModel(
            voice="Puck",
            temperature=0.8,
            instructions=AGENT_INSTRUCTION
        ),
        tools=tools
    )
    
    logger.info("Iniciando JARVIS 5.0 para WilliamPereira...")
    
    session = voice.AgentSession()
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=voice.RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Saudação inicial
    greeting = fnc_ctx.search_long_term_memory("Como devo saudar o William hoje?")
    await session.generate_reply(instructions=f"{SESSION_INSTRUCTION}\nContexto de memória: {greeting}")

if __name__ == "__main__":
    agents.cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
