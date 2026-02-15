"""
JARVIS 5.0 - AI Agent (Orquestrador Modular)
==============================================
CORREÃ‡ÃƒO P2: God Object Refactoring - VersÃ£o Modular

Este Ã© o ORQUESTRADOR PRINCIPAL que coordena:
  - PerceptionEngine: Coleta entradas (visÃ£o, Ã¡udio, memÃ³ria)
  - DecisionEngine: Toma decisÃµes via LLMs
  - ActionHandler: Executa aÃ§Ãµes fÃ­sicas/virtuais

NOTA: Este arquivo substitui o ai_agent.py monolÃ­tico (1126 linhas)
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
    logger.error(f"âŒ CRÃTICO: PerceptionEngine nÃ£o disponÃ­vel: {e}")
    get_perception_engine = None
    PERCEPTION_AVAILABLE = False

try:
    from src.core.intelligence.decision_engine import get_decision_engine
    DECISION_AVAILABLE = True
except ImportError as e:
    logger.error(f"âŒ CRÃTICO: DecisionEngine nÃ£o disponÃ­vel: {e}")
    get_decision_engine = None
    DECISION_AVAILABLE = False

try:
    from src.core.intelligence.action_handler import get_action_handler
    ACTION_HANDLER_AVAILABLE = True
except ImportError as e:
    logger.error(f"âŒ CRÃTICO: ActionHandler nÃ£o disponÃ­vel: {e}")
    get_action_handler = None
    ACTION_HANDLER_AVAILABLE = False

try:
    from src.learning.semantic_feedback import process_interaction_feedback
    SEMANTIC_FEEDBACK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ Semantic Feedback nÃ£o disponÃ­vel: {e}")
    process_interaction_feedback = None
    SEMANTIC_FEEDBACK_AVAILABLE = False


class AIAgentModular:
    """
    Agente de IA Modular - Coordena os 3 motores
    
    DESIGN PATTERN: Facade Pattern
      - Simplifica interface complexa de 3 subsistemas
      - Gerencia ciclo ReAct (Reasoning + Acting)
      - MantÃ©m histÃ³rico de conversaÃ§Ã£o
    
    USAGE:
      agent = AIAgentModular()
      
      # Modo sÃ­ncrono (para backward compatibility)
      response = agent.process_command_sync("olÃ¡ jarvis")
      
      # Modo assÃ­ncrono (P1 AsyncIO - recomendado)
      response = await agent.process_command("abrir notepad")
    """
    
    def __init__(self, provider: str = 'gemini'):
        """
        Inicializa AIAgent modular
        
        Args:
            provider: 'gemini', 'ollama', ou 'local'
        """
        logger.info("="*60)
        logger.info("ðŸš€ JARVIS 5.0 - AI Agent Modular (P2)")
        logger.info("="*60)
        
        # Verificar dependÃªncias crÃ­ticas
        if not PERCEPTION_AVAILABLE or not DECISION_AVAILABLE or not ACTION_HANDLER_AVAILABLE:
            raise ImportError(
                "âŒ CRÃTICO: Engines nÃ£o disponÃ­veis. "
                "Verifique PerceptionEngine, DecisionEngine e ActionHandler."
            )
        
        # Inicializar os 3 motores
        self.perception = get_perception_engine()
        self.decision = get_decision_engine(provider)
        self.action_handler = get_action_handler()
        
        # ConfiguraÃ§Ãµes
        if CONFIG_AVAILABLE:
            self.max_react_turns = config.get_ai_config('ai_agent.max_react_turns', 5)
            self.screenshot_timeout = config.get_ai_config('ai_agent.screenshot_timeout', 5.0)
        else:
            self.max_react_turns = 5
            self.screenshot_timeout = 5.0
        
        # Estado
        self.chat_history: List[Dict[str, str]] = []
        self.provider = provider
        
        logger.info(f"âœ… AIAgentModular inicializado (provider={provider})")
        logger.info(f"  â€¢ PerceptionEngine: OK")
        logger.info(f"  â€¢ DecisionEngine: OK")
        logger.info(f"  â€¢ ActionHandler: OK")
        logger.info(f"  â€¢ Max ReAct turns: {self.max_react_turns}")
    
    
    async def process_command(
        self,
        user_command: str,
        enable_vision: bool = True,
        privacy_level: Optional[str] = None,
        latency_req: Optional[str] = None
    ) -> str:
        """
        Processa comando do usuÃ¡rio de forma assÃ­ncrona
        
        Args:
            user_command: Comando em linguagem natural
            enable_vision: Se True, captura screenshot
            privacy_level: "LOW", "MEDIUM", "HIGH"
            latency_req: "ULTRA_LOW", "LOW", "MEDIUM", "FLEXIBLE"
        
        Returns:
            Resposta final em linguagem natural
        
        FLOW:
          1. PERCEPTION: Coleta contexto (visÃ£o + Ã¡udio + memÃ³ria)
          2. DECISION: LLM decide o que fazer
          3. ACTION: Executa aÃ§Ãµes retornadas
          4. REACT: Se executou aÃ§Ãµes, volta para DECISION (loop)
          5. FINAL: Resposta final quando nÃ£o hÃ¡ mais aÃ§Ãµes
        """
        logger.info("="*60)
        logger.info(f"ðŸŽ™ï¸ USER: {user_command}")
        logger.info("="*60)
        
        # Loop ReAct (Reasoning + Acting)
        current_turn = 0
        enriched_command = user_command
        
        while current_turn < self.max_react_turns:
            logger.info(f"ðŸ”„ ReAct Turn {current_turn+1}/{self.max_react_turns}")
            
            # ================================================================
            # PHASE 1: PERCEPTION - Coletar contexto perceptual
            # ================================================================
            try:
                context = await self.perception.gather_context(
                    user_command=enriched_command,
                    enable_vision=enable_vision
                )
                logger.info(f"âœ… Context gathered: vision={bool(context['screenshot_path'])}")
            except Exception as e:
                logger.error(f"âŒ Erro no Perception: {e}")
                context = {
                    "screenshot_path": None,
                    "user_face": "Unknown",
                    "user_emotion": "neutral",
                    "memory_context": "",
                    "ui_elements": [],
                    "ocr_text": ""
                }
            
            # ================================================================
            # PHASE 2: DECISION - LLM decide aÃ§Ãµes
            # ================================================================
            try:
                decision = await self.decision.decide(
                    user_command=enriched_command,
                    context=context,
                    privacy_level=privacy_level,
                    latency_req=latency_req
                )
                logger.info(f"âœ… Decision: {len(decision['actions'])} aÃ§Ãµes planejadas")
            except Exception as e:
                logger.error(f"âŒ Erro no Decision: {e}")
                return "Desculpe, ocorreu um erro ao processar sua solicitaÃ§Ã£o."
            
            # ================================================================
            # PHASE 3: ACTION - Executar aÃ§Ãµes
            # ================================================================
            if decision['actions']:
                try:
                    results = await self.action_handler.execute_actions(
                        actions=decision['actions'],
                        context=context
                    )
                    
                    success_count = sum(1 for r in results if r['status'] == 'success')
                    logger.info(f"âœ… Actions: {success_count}/{len(results)} executadas com sucesso")
                    
                    # ================================================================
                    # PHASE 4: REACT - Enriquecer comando com resultados
                    # ================================================================
                    # Adicionar resultados ao contexto para prÃ³ximo turno
                    feedback = self._build_feedback(results)
                    enriched_command = f"{user_command}\n\n[SISTEMA] AÃ§Ãµes executadas:\n{feedback}"
                    
                    # Continuar loop ReAct
                    current_turn += 1
                    continue
                
                except Exception as e:
                    logger.error(f"âŒ Erro no ActionHandler: {e}")
                    return "Desculpe, ocorreu um erro ao executar as aÃ§Ãµes."
            
            # ================================================================
            # PHASE 5: FINAL ANSWER - Sem aÃ§Ãµes, resposta final
            # ================================================================
            final_answer = decision['final_answer']
            
            # Salvar no histÃ³rico
            self.chat_history.append({
                "user": user_command,
                "assistant": final_answer,
                "provider": decision['provider']
            })
            
            # ================================================================
            # PHASE 6: SEMANTIC FEEDBACK - Auto-CorreÃ§Ã£o Evolutiva (InvisÃ­vel)
            # ================================================================
            if SEMANTIC_FEEDBACK_AVAILABLE and process_interaction_feedback:
                try:
                    # Processar feedback semÃ¢ntico de forma assÃ­ncrona (nÃ£o bloqueia resposta)
                    asyncio.create_task(self._process_semantic_feedback_async(user_command, final_answer))
                except Exception as e:
                    logger.debug(f"âš ï¸ Erro no feedback semÃ¢ntico (nÃ£o crÃ­tico): {e}")
            
            logger.info("="*60)
            logger.info(f"ðŸ¤– JARVIS: {final_answer[:100]}...")
            logger.info("="*60)
            
            return final_answer
        
        # Max turns atingido
        logger.warning(f"âš ï¸ Max ReAct turns ({self.max_react_turns}) atingido")
        return "Desculpe, atingi o limite de iteraÃ§Ãµes. Tente reformular sua solicitaÃ§Ã£o."
    
    
    def _build_feedback(self, results: List[Dict[str, Any]]) -> str:
        """ConstrÃ³i feedback das aÃ§Ãµes para prÃ³ximo turno"""
        feedback_lines = []
        
        for r in results:
            status_emoji = "âœ…" if r['status'] == 'success' else "âŒ"
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
        VersÃ£o sÃ­ncrona (backward compatibility)
        
        Args:
            user_command: Comando do usuÃ¡rio
            **kwargs: Argumentos adicionais para process_command
        
        Returns:
            Resposta final
        """
        # Rodar async em event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Criar novo loop se nÃ£o existir
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.process_command(user_command, **kwargs))
    
    
    def get_chat_history(self, last_n: int = 10) -> List[Dict[str, str]]:
        """Retorna histÃ³rico de conversaÃ§Ã£o"""
        return self.chat_history[-last_n:]
    
    
    async def _process_semantic_feedback_async(self, user_input: str, ai_response: str):
        """
        Processa feedback semÃ¢ntico de forma assÃ­ncrona
        
        Args:
            user_input: Entrada do usuÃ¡rio
            ai_response: Resposta da IA
        """
        try:
            # Importar aqui para evitar dependÃªncias circulares
            from src.learning.semantic_feedback import process_interaction_feedback
            
            # Processar feedback (operaÃ§Ã£o sÃ­ncrona em thread separado)
            loop = asyncio.get_event_loop()
            feedback_result = await loop.run_in_executor(
                None, 
                process_interaction_feedback, 
                user_input, 
                ai_response
            )
            
            # Log discreto (nÃ£o interrompe usuÃ¡rio)
            confidence = feedback_result.get('confidence_score', 0.5)
            dissonance = feedback_result.get('dissonance_detected', False)
            
            if dissonance:
                logger.debug(f"ðŸŽ¯ DissonÃ¢ncia detectada - ConfianÃ§a: {confidence:.2f}")
            else:
                logger.debug(f"âœ… InteraÃ§Ã£o positiva - ConfianÃ§a: {confidence:.2f}")
                
        except Exception as e:
            logger.debug(f"âš ï¸ Erro no processamento de feedback semÃ¢ntico: {e}")
    
    
    def clear_history(self):
        """Limpa histÃ³rico de conversaÃ§Ã£o"""
        self.chat_history.clear()
        logger.info("ðŸ—‘ï¸ Chat history cleared")


# ============================================================================
# SINGLETON GETTER (para compatibilidade com cÃ³digo legado)
# ============================================================================
_ai_agent_modular_instance = None

def get_ai_agent(provider: str = 'gemini') -> AIAgentModular:
    """Retorna instÃ¢ncia singleton do AIAgentModular"""
    global _ai_agent_modular_instance
    if _ai_agent_modular_instance is None:
        _ai_agent_modular_instance = AIAgentModular(provider)
    return _ai_agent_modular_instance


# ============================================================================
# BACKWARD COMPATIBILITY ALIAS
# ============================================================================
# Permitir importar como "AIAgent" (cÃ³digo legado)
AIAgent = AIAgentModular
