import os
import json
import asyncio
import datetime
from loguru import logger
from ..local_memory import local_memory
from ..engineer_brain import brain

class DreamProcessor:
    """
    O 'Processador de Sonhos' do Jarvis.
    Analisa logs de conversas passadas para extrair aprendizados, 
    ajustar a personalidade e reforçar memórias importantes.
    """
    
    def __init__(self, logs_dir: str = "backend/data/logs"):
        self.logs_dir = logs_dir
        self.is_dreaming = False
    
    async def capture_experiences(self) -> list:
        """Lê os logs reais do sistema para análise."""
        experiences = []
        try:
            # Busca logs de atividade reais salvos pelo log_manager
            log_file = os.path.join(self.logs_dir, "activity.log")
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    # Pega as últimas 50 linhas de atividade
                    lines = f.readlines()
                    experiences = [line.strip() for line in lines[-50:]]
            
            # Adiciona logs de conversação se existirem
            chat_log = os.path.join(self.logs_dir, "chat_history.json")
            if os.path.exists(chat_log):
                with open(chat_log, "r", encoding="utf-8") as f:
                    chats = json.load(f)
                    experiences.extend([f"Conversa: {c['content']}" for c in chats[-10:]])
            
            return experiences
        except Exception as e:
            logger.error(f"[DreamProcessor] Erro ao capturar experiências reais: {e}")
            return []

    async def reflect(self, experiences: list):
        """Usa o Ollama local (ou OpenRouter se falhar) para refletir."""
        if not experiences:
            return
        
        logger.info(f"[DreamProcessor] Iniciando reflexão autônoma sobre {len(experiences)} eventos...")
        context = "\n".join(experiences)
        prompt = (
            "Como o subconsciente do JARVIS, analise as atividades e conversas acima. "
            "Identifique padrões de comportamento do usuário, erros recorrentes do sistema e preferências. "
            "Gere uma lista de 3 fatos importantes para eu lembrar e evoluir. "
            "Responda apenas com os fatos, de forma concisa."
        )
        
        try:
            # Tenta usar Ollama local primeiro para 'Sonhos' (mais privado e grátis)
            insights = await brain.reason_local(prompt, context)
            if not insights:
                # Fallback para OpenRouter se o usuário não tiver Ollama
                insights = await brain.reason(prompt, context)
            
            if insights:
                logger.success(f"[DreamProcessor] Reflexão concluída com sucesso.")
            return insights
        except Exception as e:
            logger.error(f"[DreamProcessor] Falha na reflexão: {e}")
            return None

    async def dream_loop(self):
        """Loop de processamento em idle."""
        while True:
            # Espera um longo tempo entre 'sonhos' ou checa atividade do sistema
            await asyncio.sleep(3600) # Checa a cada hora
            
            # Condição de exemplo: só sonha de madrugada ou quando o PC está idle
            now = datetime.datetime.now().hour
            if now >= 0 and now <= 5: # Janela de sonho: 00h às 05h
                experiences = await self.capture_experiences()
                insights = await self.reflect(experiences)
                if insights:
                    # Salva os aprendizados na memória local
                    local_memory.save_fact("Jarvis", f"Insight de Evolução: {insights}")

# Singleton
dream_processor = DreamProcessor()
