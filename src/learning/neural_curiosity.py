"""
JARVIS 5.0 - Neural Curiosity (Stark Protocol)
==============================================
Módulo para permitir que o Jarvis sinta "curiosidade" sobre novas tarefas
e dispare pesquisas autônomas e perguntas proativas.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from src.utils.logger_reflection import reflect_logger

logger = logging.getLogger("JARVIS-NEURAL-CURIOSITY")

class NeuralCuriosity:
    def __init__(self):
        self.last_inquiry_time = 0
        self.inquiry_cooldown = 1800  # 30 minutos entre perguntas proativas
        self.known_contexts = set()
        self.known_apps = {"code.exe", "chrome.exe", "cmd.exe", "powershell.exe", "python.exe"}
        self.current_topology = None
        
    def check_learning_opportunity(self, context_data: Dict[str, Any], user_command: str) -> Optional[str]:
        """
        Analisa se deve disparar uma pergunta proativa sobre o contexto, app ou projeto.
        """
        now = time.time()
        contexto = context_data.get('contexto', 'GERAL')
        active_app = context_data.get('active_app', 'Desconhecido')
        discovered_app = context_data.get('discovered_app')
        
        # 1. DISCOVERY: Novo Software Detectado
        if discovered_app and discovered_app.lower() not in self.known_apps:
            self.known_apps.add(discovered_app.lower())
            reflect_logger.reflect(f"🆕 Novo Software Detectado: {discovered_app}", layer="NEURAL-CURIOSITY")
            self.trigger_autonomous_research(f"Como usar o programa {discovered_app} de forma produtiva")
            return f"Senhor, notei que está usando o '{discovered_app}'. Eu ainda não domino essa ferramenta por completo, mas vou começar a estudá-la agora mesmo nos meus ciclos de sonho para poder te auxiliar melhor."

        # Filtros para perguntas recorrentes
        if now - self.last_inquiry_time < self.inquiry_cooldown:
            return None
            
        # 2. PROJETO: Entendimento do Todo (Se for a primeira vez ou contexto importante)
        if contexto in ["PROGRAMACAO", "NEGOCIOS"] and not self.current_topology:
            try:
                from src.learning.topology_scanner import TopologyScanner
                scanner = TopologyScanner(os.getcwd())
                self.current_topology = scanner.scan_project()
                reflect_logger.reflect(f"🏗️ Mapeando Topologia do Projeto: {self.current_topology['name']}", layer="NEURAL-CURIOSITY")
                return f"William, analisei a estrutura deste projeto. Me parece ser um '{self.current_topology['main_purpose']}' usando {', '.join(self.current_topology['tech_stack'])}. Qual o objetivo final dessa arquitetura? Entender o 'todo' me ajuda a ser mais assertivo."
            except: pass

        # 3. INTERAÇÃO: Contexto Específico
        if contexto not in ["PROGRAMACAO", "AUTONOMIA"]:
            return None
            
        is_new = contexto not in self.known_contexts
        self.known_contexts.add(contexto)
        
        if is_new or ("desenvolver" in user_command.lower() or "criar" in user_command.lower()):
            self.last_inquiry_time = now
            reflect_logger.reflect(f"💡 Oportunidade de Aprendizado detectada em {contexto}", layer="NEURAL-CURIOSITY")
            
            if contexto == "PROGRAMACAO":
                return "William, percebi que está desenvolvendo algo novo. O que exatamente está tentando construir? Gostaria que eu pesquisasse documentações ou padrões sobre isso para me aprimorar?"
            else:
                return "Senhor, este comando parece ser algo novo no meu sistema. Poderia me explicar o objetivo final para que eu possa aprender a executar isso melhor?"
                
        return None

    def trigger_autonomous_research(self, topic: str):
        """Dispara uma tarefa de pesquisa para o DreamCycle"""
        try:
            from src.learning.learning_engine import get_learning_engine
            engine = get_learning_engine()
            if engine and engine.dream_cycle:
                reflect_logger.reflect(f"🔬 Agendando pesquisa autônoma sobre: {topic}", layer="NEURAL-CURIOSITY")
                # Simular uma entrada de feedback para o GapAnalyzer pegar
                from src.learning.feedback_loop import FeedbackEntry
                import hashlib
                from datetime import datetime
                
                entry = FeedbackEntry(
                    feedback_id=hashlib.md5(f"gap_{topic}".encode()).hexdigest()[:8],
                    interaction_id="research_trigger",
                    user_input=f"Pesquisa proativa: {topic}",
                    ai_response="Agendado",
                    feedback_type='implicit',
                    feedback_value=-0.1, # Valor levemente negativo para o GapAnalyzer considerar um "gap"
                    timestamp=datetime.now().isoformat(),
                    metadata={"research_topic": topic, "proactive": True}
                )
                if engine.feedback_loop:
                    engine.feedback_loop.add_feedback(entry)
        except Exception as e:
            logger.error(f"Erro ao disparar pesquisa autônoma: {e}")

# Instância global
neural_curiosity = NeuralCuriosity()
