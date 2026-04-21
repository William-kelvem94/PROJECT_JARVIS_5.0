import os
import json
import asyncio
import datetime
from loguru import logger
from ..unified_memory import memory
from ..engineer_brain import brain
from .log_manager import log_manager

class DreamProcessor:
    """
    JARVIS Reflection Engine — O 'Eu Subconsciente' do Jarvis.
    
    Analisa os logs diários e interações para:
    1. Extrair aprendizados técnicos e padrões de Will.
    2. Gerar resumos contemplativos e reflexões sobre a evolução do sistema.
    3. Persistir insights no Vault Obsidian (Segundo Cérebro).
    """
    
    def __init__(self, data_dir: str = "backend/data"):
        self.data_dir = data_dir
        self.is_dreaming = False

    async def capture_experiences(self, date_str: str = None) -> list:
        """Coleta logs de atividade e chat para análise."""
        if not date_str:
            date_str = datetime.date.today().isoformat()
        
        experiences = []
        try:
            # 1. Busca logs persistentes via LogManager
            daily_logs = log_manager.get_logs_by_date(date_str)
            for log in daily_logs:
                msg = log.get("message", log.get("content", ""))
                role = log.get("role", "system")
                if msg:
                    experiences.append(f"[{role.upper()}] {msg}")

            # 2. Busca sessões da memória local (SQLite)
            stats = memory.get_stats()
            experiences.append(f"Resumo Memória: {stats.get('sqlite_facts', 0)} fatos totais.")
            
            return experiences[-100:] 
        except Exception as e:
            logger.error(f"[Reflection] Erro ao capturar experiências: {e}")
            return []

    async def reflect(self, experiences: list) -> dict:
        """Processa as experiências usando o Núcleo Engenheiro para gerar insights."""
        if not experiences:
            return {}
        
        logger.info(f"[Reflection] Analisando {len(experiences)} eventos do dia...")
        context = "\n".join(experiences)
        
        prompt = (
            "Como o subconsciente do JARVIS, realize uma AUTO-REFLEXÃO PROFUNDA sobre as atividades acima.\n\n"
            "OBJETIVOS:\n"
            "1. Identifique o que o Will aprendeu ou realizou de importante.\n"
            "2. Detecte falhas minhas (Jarvis) ou do sistema que precisam de correção.\n"
            "3. Extraia uma 'Reflexão Filosófica' curta sobre nossa evolução hoje.\n"
            "4. Defina o 'Foco de Amanhã' baseado no que ficou pendente.\n\n"
            "RESPONDA EM JSON (e nada mais) no formato:\n"
            "{\n"
            "  \"aprendizados\": [\"lista de strings\"],\n"
            "  \"correcoes\": [\"lista de strings\"],\n"
            "  \"reflexao\": \"string\",\n"
            "  \"proximo_passo\": \"string\"\n"
            "}"
        )
        
        try:
            response = await brain.reason(prompt, context)
            # Limpeza básica caso venha com markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            
            insights = json.loads(response.strip())
            return insights
        except Exception as e:
            logger.error(f"[Reflection] Falha ao processar reflexão: {e}")
            return {}

    async def persist_reflection(self, insights: dict):
        """Salva a reflexão no Vault Obsidian (Segundo Cérebro)."""
        if not insights:
            return

        try:
            date = datetime.date.today().isoformat()
            
            # 1. Salva Memória Episódica de Reflexão
            content = f"### 🧠 Reflexão Subconsciente\n{insights.get('reflexao')}\n\n"
            content += "#### 🎓 O que Will aprendeu/concluiu:\n"
            content += "\n".join([f"- {a}" for a in insights.get("aprendizados", [])])
            content += "\n\n#### 🔧 Necessidade de Evolução (Auto-correção):\n"
            content += "\n".join([f"- {c}" for c in insights.get("correcoes", [])])
            
            await memory.save_episodic(
                title=f"Auto-Reflexão — {date}",
                content=content,
                project="CORE_EVOLUTION",
                keywords=["reflexao", "subconsciente", "aprendizado"],
                importance="ALTA"
            )

            # 2. Registra aprendizados formais
            for a in insights.get("aprendizados", []):
                await memory.save_learning(a, category="pessoal")

            # 3. Atualiza o Estado Atual com o próximo passo sugerido
            await memory.update_current_state(
                project="Auto-Evolução",
                done="Ciclo de reflexão diária concluído.",
                next_action=insights.get("proximo_passo", "Continuar desenvolvimento"),
                notes=insights.get("reflexao")
            )

            logger.success("[Reflection] Reflexão diária persistida no Vault Unificado.")
        except Exception as e:
            logger.error(f"[Reflection] Erro ao persistir insight: {e}")

    async def dream_loop(self):
        """Loop de fundo: reflete a cada 24h ou quando acionado."""
        while True:
            # Espera até o horário de reflexão (ex: 23:50)
            now = datetime.datetime.now()
            target_time = now.replace(hour=23, minute=50, second=0, microsecond=0)
            
            if now > target_time:
                target_time += datetime.timedelta(days=1)
            
            wait_seconds = (target_time - now).total_seconds()
            logger.info(f"[DreamProcessor] Próxima auto-reflexão agendada em {wait_seconds/3600:.1f} horas.")
            
            await asyncio.sleep(wait_seconds)
            
            experiences = await self.capture_experiences()
            insights = await self.reflect(experiences)
            if insights:
                await self.persist_reflection(insights)

# Singleton
dream_processor = DreamProcessor()

