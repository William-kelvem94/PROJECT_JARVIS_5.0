"""
JARVIS 5.0 - AI Agent (Orquestrador Modular)
==============================================
CORREÇÃO P2: God Object Refactoring - Versão Modular

Este é o ORQUESTRADOR PRINCIPAL que coordena:
  - PerceptionEngine: Coleta entradas (visão, áudio, memória)
  - DecisionEngine: Toma decisões via LLMs
  - ActionHandler: Executa ações físicas/virtuais

NOTA: Este arquivo substitui o ai_agent.py monolítico (1126 linhas)
      pela arquitetura modular (~300 linhas).

USAGE:
  from src.core.intelligence.ai_agent_modular import AIAgentModular
  agent = AIAgentModular()
  response = await agent.process_command("abrir notepad")
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTS DOS 3 MOTORES (P2 - Arquitetura Modular)
# ============================================================================
try:
    from src.core.intelligence.perception_engine import get_perception_engine
    PERCEPTION_AVAILABLE = True
except ImportError as e:
    logger.error(f"❌ CRÍTICO: PerceptionEngine não disponível: {e}")
    get_perception_engine = None
    PERCEPTION_AVAILABLE = False

try:
    from src.core.intelligence.decision_engine import get_decision_engine
    DECISION_AVAILABLE = True
except ImportError as e:
    logger.error(f"❌ CRÍTICO: DecisionEngine não disponível: {e}")
    get_decision_engine = None
    DECISION_AVAILABLE = False

try:
    from src.core.intelligence.action_handler import get_action_handler
    ACTION_HANDLER_AVAILABLE = True
except ImportError as e:
    logger.error(f"❌ CRÍTICO: ActionHandler não disponível: {e}")
    get_action_handler = None
    ACTION_HANDLER_AVAILABLE = False

try:
    from src.utils.config import config
    CONFIG_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Config não disponível")
    config = None
    CONFIG_AVAILABLE = False


class AIAgentModular:
    """
    Agente de IA Modular - Coordena os 3 motores
    
    DESIGN PATTERN: Facade Pattern
      - Simplifica interface complexa de 3 subsistemas
      - Gerencia ciclo ReAct (Reasoning + Acting)
      - Mantém histórico de conversação
    
    USAGE:
      agent = AIAgentModular()
      
      # Modo síncrono (para backward compatibility)
      response = agent.process_command_sync("olá jarvis")
      
      # Modo assíncrono (P1 AsyncIO - recomendado)
      response = await agent.process_command("abrir notepad")
    """
    
    def __init__(self, provider: str = 'gemini'):
        """
        Inicializa AIAgent modular
        
        Args:
            provider: 'gemini', 'ollama', ou 'local'
        """
        logger.info("="*60)
        logger.info("🚀 JARVIS 5.0 - AI Agent Modular (P2)")
        logger.info("="*60)
        
        # Verificar dependências críticas
        if not PERCEPTION_AVAILABLE or not DECISION_AVAILABLE or not ACTION_HANDLER_AVAILABLE:
            raise ImportError(
                "❌ CRÍTICO: Engines não disponíveis. "
                "Verifique PerceptionEngine, DecisionEngine e ActionHandler."
            )
        
        # Inicializar os 3 motores
        self.perception = get_perception_engine()
        self.decision = get_decision_engine(provider)
        self.action_handler = get_action_handler()
        
        # Configurações
        if CONFIG_AVAILABLE:
            self.max_react_turns = config.get_ai_config('ai_agent.max_react_turns', 5)
            self.screenshot_timeout = config.get_ai_config('ai_agent.screenshot_timeout', 5.0)
        else:
            self.max_react_turns = 5
            self.screenshot_timeout = 5.0
        
        # Estado
        self.chat_history: List[Dict[str, str]] = []
        self.provider = provider
        
        logger.info(f"✅ AIAgentModular inicializado (provider={provider})")
        logger.info(f"  • PerceptionEngine: OK")
        logger.info(f"  • DecisionEngine: OK")
        logger.info(f"  • ActionHandler: OK")
        logger.info(f"  • Max ReAct turns: {self.max_react_turns}")
    
    
    async def process_command(
        self,
        user_command: str,
        enable_vision: bool = True,
        privacy_level: Optional[str] = None,
        latency_req: Optional[str] = None
    ) -> str:
        """
        Processa comando do usuário de forma assíncrona
        
        Args:
            user_command: Comando em linguagem natural
            enable_vision: Se True, captura screenshot
            privacy_level: "LOW", "MEDIUM", "HIGH"
            latency_req: "ULTRA_LOW", "LOW", "MEDIUM", "FLEXIBLE"
        
        Returns:
            Resposta final em linguagem natural
        
        FLOW:
          1. PERCEPTION: Coleta contexto (visão + áudio + memória)
          2. DECISION: LLM decide o que fazer
          3. ACTION: Executa ações retornadas
          4. REACT: Se executou ações, volta para DECISION (loop)
          5. FINAL: Resposta final quando não há mais ações
        """
        logger.info("="*60)
        logger.info(f"🎙️ USER: {user_command}")
        logger.info("="*60)
        
        # Loop ReAct (Reasoning + Acting)
        current_turn = 0
        enriched_command = user_command
        
        while current_turn < self.max_react_turns:
            logger.info(f"🔄 ReAct Turn {current_turn+1}/{self.max_react_turns}")
            
            # ================================================================
            # PHASE 1: PERCEPTION - Coletar contexto perceptual
            # ================================================================
            try:
                context = await self.perception.gather_context(
                    user_command=enriched_command,
                    enable_vision=enable_vision
                )
                logger.info(f"✅ Context gathered: vision={bool(context['screenshot_path'])}")
            except Exception as e:
                logger.error(f"❌ Erro no Perception: {e}")
                context = {
                    "screenshot_path": None,
                    "user_face": "Unknown",
                    "user_emotion": "neutral",
                    "memory_context": "",
                    "ui_elements": [],
                    "ocr_text": ""
                }
            
            # ================================================================
            # PHASE 2: DECISION - LLM decide ações
            # ================================================================
            try:
                decision = await self.decision.decide(
                    user_command=enriched_command,
                    context=context,
                    privacy_level=privacy_level,
                    latency_req=latency_req
                )
                logger.info(f"✅ Decision: {len(decision['actions'])} ações planejadas")
            except Exception as e:
                logger.error(f"❌ Erro no Decision: {e}")
                return "Desculpe, ocorreu um erro ao processar sua solicitação."
            
            # ================================================================
            # PHASE 3: ACTION - Executar ações
            # ================================================================
            if decision['actions']:
                try:
                    results = await self.action_handler.execute_actions(
                        actions=decision['actions'],
                        context=context
                    )
                    
                    success_count = sum(1 for r in results if r['status'] == 'success')
                    logger.info(f"✅ Actions: {success_count}/{len(results)} executadas com sucesso")
                    
                    # ================================================================
                    # PHASE 4: REACT - Enriquecer comando com resultados
                    # ================================================================
                    # Adicionar resultados ao contexto para próximo turno
                    feedback = self._build_feedback(results)
                    enriched_command = f"{user_command}\n\n[SISTEMA] Ações executadas:\n{feedback}"
                    
                    # Continuar loop ReAct
                    current_turn += 1
                    continue
                
                except Exception as e:
                    logger.error(f"❌ Erro no ActionHandler: {e}")
                    return "Desculpe, ocorreu um erro ao executar as ações."
            
            # ================================================================
            # PHASE 5: FINAL ANSWER - Sem ações, resposta final
            # ================================================================
            final_answer = decision['final_answer']
            
            # Salvar no histórico
            self.chat_history.append({
                "user": user_command,
                "assistant": final_answer,
                "provider": decision['provider']
            })
            
            logger.info("="*60)
            logger.info(f"🤖 JARVIS: {final_answer[:100]}...")
            logger.info("="*60)
            
            return final_answer
        
        # Max turns atingido
        logger.warning(f"⚠️ Max ReAct turns ({self.max_react_turns}) atingido")
        return "Desculpe, atingi o limite de iterações. Tente reformular sua solicitação."
    
    
    def _build_feedback(self, results: List[Dict[str, Any]]) -> str:
        """Constrói feedback das ações para próximo turno"""
        feedback_lines = []
        
        for r in results:
            status_emoji = "✅" if r['status'] == 'success' else "❌"
            action_name = r.get('action', 'unknown')
            
            if r['status'] == 'success':
                result_preview = r.get('result', '')[:200]
                feedback_lines.append(f"{status_emoji} {action_name}: {result_preview}")
            else:
                error = r.get('error', 'Erro desconhecido')
                feedback_lines.append(f"{status_emoji} {action_name}: {error}")
        
        return "\n".join(feedback_lines)
    
    
    def process_command_sync(self, user_command: str, **kwargs) -> str:
        """
        Versão síncrona (backward compatibility)
        
        Args:
            user_command: Comando do usuário
            **kwargs: Argumentos adicionais para process_command
        
        Returns:
            Resposta final
        """
        # Rodar async em event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Criar novo loop se não existir
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_command(user_command, **kwargs))
    
    
    def get_chat_history(self, last_n: int = 10) -> List[Dict[str, str]]:
        """Retorna histórico de conversação"""
        return self.chat_history[-last_n:]
    
    
    def clear_history(self):
        """Limpa histórico de conversação"""
        self.chat_history.clear()
        logger.info("🗑️ Chat history cleared")


# ============================================================================
# SINGLETON GETTER (para compatibilidade com código legado)
# ============================================================================
_ai_agent_modular_instance = None

def get_ai_agent(provider: str = 'gemini') -> AIAgentModular:
    """Retorna instância singleton do AIAgentModular"""
    global _ai_agent_modular_instance
    if _ai_agent_modular_instance is None:
        _ai_agent_modular_instance = AIAgentModular(provider)
    return _ai_agent_modular_instance


# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================
# Permitir importar como "AIAgent" (código legado)
AIAgent = AIAgentModular
