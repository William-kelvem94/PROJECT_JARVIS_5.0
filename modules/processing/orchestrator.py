"""
Núcleo de Orquestração - Gerencia comunicação entre módulos
Processa comandos e coordena ações entre módulos
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from core.logger import logger
from core.local_llm import LocalLLM

class MessageType(Enum):
    """Tipos de mensagens no sistema."""
    TEXT = "text"
    VOICE = "voice"
    COMMAND = "command"
    ACTION = "action"
    RESPONSE = "response"

class Orchestrator:
    """
    Núcleo de orquestração do JARVIS.
    Gerencia fluxo de dados entre módulos de entrada, processamento e ação.
    """
    
    def __init__(self, llm: Optional[LocalLLM] = None):
        """
        Inicializa o orquestrador.
        
        Args:
            llm: Instância do LLM local (opcional, pode ser carregado depois)
        """
        self.llm = llm
        self.skills = {}  # Sistema de habilidades/plugins
        self.memory = []  # Memória de curto prazo
        self.context = {}  # Contexto atual da conversa
        
        logger.info("Orchestrator inicializado")
    
    def register_skill(self, skill_name: str, skill_handler: Callable):
        """
        Registra uma habilidade (skill) no sistema.
        
        Args:
            skill_name: Nome da habilidade
            skill_handler: Função que processa a habilidade
        """
        self.skills[skill_name] = skill_handler
        logger.info(f"Skill registrada: {skill_name}")
    
    def set_llm(self, llm: LocalLLM):
        """Define o LLM a ser usado."""
        self.llm = llm
        logger.info("LLM configurado no Orchestrator")
    
    async def process_message(
        self,
        message: str,
        message_type: MessageType = MessageType.TEXT,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário.
        
        Args:
            message: Mensagem do usuário
            message_type: Tipo da mensagem
            context: Contexto adicional
        
        Returns:
            Dicionário com resposta e ações
        """
        logger.info(f"Processando mensagem ({message_type.value}): {message[:50]}...")
        
        # Adicionar ao contexto
        self.memory.append({
            "role": "user",
            "content": message,
            "type": message_type.value
        })
        
        # Analisar intenção usando LLM ou processamento direto
        intent = await self._analyze_intent(message, context)
        
        # Decidir qual skill usar
        skill_result = await self._execute_skill(intent, message, context)
        
        # Se skill não executou, usar LLM para resposta geral
        if not skill_result or not skill_result.get("executed"):
            llm_response = await self._get_llm_response(message, context)
            skill_result = {
                "executed": False,
                "response": llm_response,
                "type": "llm_response"
            }
        
        # Adicionar resposta ao contexto
        self.memory.append({
            "role": "assistant",
            "content": skill_result.get("response", ""),
            "type": skill_result.get("type", "response")
        })
        
        # Limitar tamanho da memória
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]
        
        return {
            "success": True,
            "response": skill_result.get("response", ""),
            "actions": skill_result.get("actions", []),
            "intent": intent,
            "context": self.context
        }
    
    async def _analyze_intent(
        self,
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analisa a intenção da mensagem usando LLM.
        
        Returns:
            Dicionário com intenção e parâmetros extraídos
        """
        if not self.llm:
            # Fallback básico sem LLM
            return {
                "type": "general",
                "confidence": 0.5,
                "parameters": {}
            }
        
        # Prompt para análise de intenção
        intent_prompt = f"""Analise a seguinte mensagem do usuário e identifique a intenção.

Mensagem: {message}

Responda em formato JSON com:
- "type": tipo da intenção (ex: "open_app", "read_file", "search", "general")
- "confidence": confiança (0.0 a 1.0)
- "parameters": objeto com parâmetros extraídos

Habilidades disponíveis: {list(self.skills.keys())}

Resposta (apenas JSON):"""
        
        try:
            response = self.llm.generate(
                intent_prompt,
                system="Você é um analisador de intenções preciso. Retorne apenas JSON válido.",
                max_tokens=100,  # Reduzido para resposta mais rápida
                temperature=0.3
            )
            
            # Tentar parsear JSON da resposta
            import json
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                intent = json.loads(json_match.group())
                return intent
        except Exception as e:
            logger.error(f"Erro ao analisar intenção: {e}")
        
        # Fallback
        return {
            "type": "general",
            "confidence": 0.5,
            "parameters": {}
        }
    
    async def _execute_skill(
        self,
        intent: Dict[str, Any],
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa a skill apropriada baseada na intenção.
        
        Returns:
            Resultado da execução da skill
        """
        intent_type = intent.get("type", "general")
        
        # Verificar se existe skill para esta intenção
        if intent_type in self.skills:
            try:
                handler = self.skills[intent_type]
                
                # Executar handler (pode ser async ou sync)
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(message, intent.get("parameters", {}), context)
                else:
                    result = handler(message, intent.get("parameters", {}), context)
                
                return {
                    "executed": True,
                    "response": result.get("response", "Ação executada com sucesso."),
                    "actions": result.get("actions", []),
                    "type": "skill_execution",
                    "skill": intent_type
                }
            except Exception as e:
                logger.error(f"Erro ao executar skill {intent_type}: {e}")
                return {
                    "executed": False,
                    "response": f"Erro ao executar ação: {str(e)}",
                    "type": "error"
                }
        
        return {"executed": False}
    
    async def _get_llm_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Obtém resposta do LLM com contexto.
        
        Returns:
            Resposta do LLM
        """
        if not self.llm:
            return "Desculpe, o sistema de IA não está disponível no momento."
        
        # Construir prompt com contexto
        context_prompt = ""
        if self.memory:
            recent_history = self.memory[-5:]  # Últimas 5 mensagens
            context_prompt = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ])
        
        system_prompt = """Você é JARVIS, um assistente de IA inteligente e útil.
Você pode controlar o computador do usuário, abrir aplicativos, organizar arquivos e muito mais.
Seja direto, útil e amigável. Use emojis quando apropriado."""
        
        full_prompt = f"{context_prompt}\nuser: {message}\nassistant:"
        
        try:
            # Usar parâmetros otimizados automaticamente (se LLM tiver optimizer)
            response = self.llm.generate(
                full_prompt,
                system=system_prompt,
                max_tokens=250,  # Mantém qualidade mas otimizado
                temperature=0.65  # Balanceado para velocidade e qualidade
            )
            return response
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do LLM: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
    
    def get_memory(self) -> List[Dict[str, Any]]:
        """Retorna a memória de curto prazo."""
        return self.memory.copy()
    
    def clear_memory(self):
        """Limpa a memória de curto prazo."""
        self.memory = []
        logger.info("Memória limpa")

