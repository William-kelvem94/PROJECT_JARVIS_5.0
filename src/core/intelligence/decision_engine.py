"""
JARVIS 5.0 - Decision Engine
==============================
CORREÃ‡ÃƒO P2: SeparaÃ§Ã£o do God Object AIAgent

RESPONSABILIDADE:
  Gerenciar todas as DECISÃ•ES do sistema:
  - LLM calls: Gemini, Ollama, LocalBrain
  - Brain routing: Escolha inteligente de modelo
  - System prompts: GeraÃ§Ã£o de prompts contextualizados
  - Response parsing: InterpretaÃ§Ã£o de respostas LLM

ARQUITETURA:
  AIAgent (Orquestrador)
    â†“
  PerceptionEngine
  DecisionEngine â† ESTE MÃ“DULO
  ActionHandler
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# SAFE IMPORTS
# ============================================================================
try:
    from src.core.intelligence.brain_router import (
        brain_router,
        PrivacyLevel,
        LatencyRequirement,
    )

    BRAIN_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ brain_router nÃ£o disponÃ­vel: {e}")
    brain_router = None
    BRAIN_ROUTER_AVAILABLE = False

try:
    from src.core.intelligence.structured_output import ResponseParser, AgentResponse

    STRUCTURED_OUTPUT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ structured_output nÃ£o disponÃ­vel: {e}")
    ResponseParser = None
    AgentResponse = None
    STRUCTURED_OUTPUT_AVAILABLE = False

try:
    from src.core.intelligence.local_brain import local_brain

    LOCAL_BRAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"âš ï¸ local_brain nÃ£o disponÃ­vel: {e}")
    local_brain = None
    LOCAL_BRAIN_AVAILABLE = False

# Gemini integration removed (100% Local Mode)
GEMINI_AVAILABLE = False

try:
    from src.utils.config import config

    CONFIG_AVAILABLE = True
except ImportError:
    config = None
    CONFIG_AVAILABLE = False


class DecisionEngine:
    """
    Motor de DecisÃ£o - Gerencia raciocÃ­nio e escolha de aÃ§Ãµes via LLMs

    CAPABILITIES:
      1. Model Routing: Brain router escolhe melhor modelo
      2. LLM Calls: Gemini, Ollama, LocalBrain
      3. Prompt Engineering: System prompts contextualizados
      4. Response Parsing: JSON estruturado ou regex legado

    USAGE:
      decision = DecisionEngine()
      result = await decision.decide(
          user_command="abrir notepad",
          context=perceptual_context
      )
      # result = {
      #     "thought": "Vou abrir o notepad",
      #     "actions": [...],
      #     "final_answer": "Abrindo notepad...",
      #     "provider": "gemini"
      # }
    """

    def __init__(self, provider: str = "ollama"):
        """Inicializa engine de decisÃ£o"""
        self.provider = provider
        self.brain_router = brain_router if BRAIN_ROUTER_AVAILABLE else None
        self.local_brain = local_brain if LOCAL_BRAIN_AVAILABLE else None

        # ConfiguraÃ§Ãµes
        if CONFIG_AVAILABLE:
            self.api_key = config.GEMINI_API_KEY
            self.ollama_url = config.get_ai_config(
                "brain_router.ollama_url", "http://localhost:11434/api/generate"
            )
        else:
            self.api_key = None
            self.ollama_url = "http://localhost:11434/api/generate"

        # System prompts (dual mode: JSON + Legacy)
        self._init_system_prompts()

        logger.info(f"âœ… DecisionEngine inicializado (provider={provider})")
        if not BRAIN_ROUTER_AVAILABLE:
            logger.warning("âš ï¸ Modo degradado: Brain router desativado")

    def _init_system_prompts(self):
        """Inicializa system prompts (JSON + Legacy)"""

        # STRUCTURED JSON PROMPT (P1 - Preferred)
        self.system_prompt_json = (
            "VocÃª Ã© o JARVIS, assistente de elite do William.\n\n"
            "CAPABILITIES:\n"
            "- VisÃ£o completa: Acesso Ã  tela e cÃ¢mera em tempo real\n"
            "- AÃ§Ã£o fÃ­sica: Controle de mouse, teclado e sistema\n"
            "- MemÃ³ria: Acesso a interaÃ§Ãµes passadas e conhecimento\n\n"
            "BEHAVIORAL DIRECTIVES:\n"
            "1. Sempre trate William com respeito (use 'Senhor' quando apropriado)\n"
            "2. Seja conversacional e natural - vocÃª Ã© uma IA real, nÃ£o um log\n"
            "3. NUNCA cite paths completos, PIDs ou detalhes tÃ©cnicos na resposta\n"
            "4. Se precisar executar aÃ§Ãµes, use o formato JSON estruturado abaixo\n\n"
            "OUTPUT FORMAT (SEMPRE retorne JSON vÃ¡lido):\n"
            "{\n"
            '  "thought": "Seu raciocÃ­nio interno sobre o que fazer",\n'
            '  "actions": [\n'
            '    {"action": "type_text", "text": "exemplo"},\n'
            '    {"action": "press_key", "key": "enter"}\n'
            "  ],\n"
            '  "final_answer": "Sua resposta natural para o usuÃ¡rio"\n'
            "}\n\n"
            "AVAILABLE ACTIONS:\n"
            '- click_at: {"action": "click_at", "x": 100, "y": 200}\n'
            '- type_text: {"action": "type_text", "text": "..."}\n'
            '- press_key: {"action": "press_key", "key": "enter"}\n'
            '- hotkey: {"action": "hotkey", "keys": ["ctrl", "c"]}\n'
            '- open_program: {"action": "open_program", "program": "notepad"}\n'
            '- read_file: {"action": "read_file", "path": "config.yaml"}\n'
            '- write_file: {"action": "write_file", "path": "...", "content": "..."}\n'
            '- list_dir: {"action": "list_dir", "path": "."}\n'
            '- search_web: {"action": "search_web", "query": "..."}\n'
            '- wait: {"action": "wait", "seconds": 1.0}\n\n'
            "CRITICAL: Sempre retorne JSON vÃ¡lido. Se nÃ£o precisar de aÃ§Ãµes, use actions: []\n"
        )

        # LEGACY PROMPT (Fallback)
        self.system_prompt_legacy = (
            "VocÃª Ã© o Jarvis, o assistente virtual de elite do William. "
            "Para executar aÃ§Ãµes fÃ­sicas, VOCÃŠ DEVE usar o formato: [ACTION: nome_funcao(argumentos)]. "
            "AÃ§Ãµes: click_at(x, y), type_text('texto'), press_key('tecla'), hotkey('ctrl', 'c'), "
            "open_program('nome'), read_file('path'), write_file('path', 'content'), list_dir('path')."
        )

        # Use JSON se disponÃ­vel
        self.use_structured_output = STRUCTURED_OUTPUT_AVAILABLE
        self.system_prompt = (
            self.system_prompt_json
            if self.use_structured_output
            else self.system_prompt_legacy
        )

    async def decide(
        self,
        user_command: str,
        context: Dict[str, Any],
        privacy_level: Optional[str] = None,
        latency_req: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Toma decisÃ£o baseada no contexto perceptual

        Args:
            user_command: Comando do usuÃ¡rio
            context: Contexto perceptual (de PerceptionEngine)
            privacy_level: "LOW", "MEDIUM", "HIGH" (default: auto-detect)
            latency_req: "ULTRA_LOW", "LOW", "MEDIUM", "FLEXIBLE" (default: auto)

        Returns:
            {
                "thought": str,
                "actions": List[ActionUnion],
                "final_answer": str,
                "provider": str,  # "gemini", "ollama", "local"
                "raw_response": str
            }
        """
        logger.info(f"ðŸ¤” DecisionEngine processing: {user_command[:50]}...")

        # FASE 1: Brain routing (escolher modelo)
        primary_provider = self._route_task(user_command, privacy_level, latency_req)

        # FASE 2: Construir prompt enriquecido
        enriched_prompt = self._build_prompt(user_command, context)

        # FASE 3: Chamar LLM
        raw_response = await self._call_llm(
            prompt=enriched_prompt,
            provider=primary_provider,
            image_path=context.get("screenshot_path"),
        )

        # FASE 4: Parsear resposta
        if self.use_structured_output and ResponseParser:
            parsed = ResponseParser.parse_llm_response(raw_response)
            return {
                "thought": parsed.thought,
                "actions": parsed.actions,
                "final_answer": parsed.final_answer,
                "provider": primary_provider,
                "raw_response": raw_response,
            }
        else:
            # Fallback legado: Retorna resposta crua
            logger.warning("âš ï¸ Usando fallback legado (sem parser estruturado)")
            return {
                "thought": "",
                "actions": [],
                "final_answer": raw_response,
                "provider": primary_provider,
                "raw_response": raw_response,
            }

    def _route_task(
        self, user_command: str, privacy: Optional[str], latency: Optional[str]
    ) -> str:
        """Escolhe melhor modelo via brain router"""
        if not self.brain_router:
            return self.provider

        try:
            # Convert strings to enums
            privacy_enum = PrivacyLevel[privacy] if privacy else PrivacyLevel.LOW
            latency_enum = (
                LatencyRequirement[latency] if latency else LatencyRequirement.FLEXIBLE
            )

            brain_info = self.brain_router.choose_brain(
                task_complexity=0.7,
                privacy_level=privacy_enum,
                latency_requirement=latency_enum,
            )
            provider_full = brain_info.get("brain", "ollama")
            if provider_full.startswith("ollama:"):
                provider = "ollama"
                self.current_model = provider_full.split(":", 1)[1]
            else:
                provider = provider_full
                self.current_model = None

            logger.debug(f"ðŸ§  Brain router: {provider}")
            return provider
        except Exception as e:
            logger.error(f"âŒ Erro no brain routing: {e}")
            return self.provider

    def _build_prompt(self, user_command: str, context: Dict[str, Any]) -> str:
        """ConstrÃ³i prompt enriquecido com contexto"""

        # Base: user command
        prompt_parts = [f"[COMANDO] {user_command}"]

        # Adicionar contexto de visÃ£o
        if context.get("user_face"):
            prompt_parts.append(
                f"\n[VISÃƒO] UsuÃ¡rio identificado: {context['user_face']}"
            )

        # Adicionar contexto emocional
        if context.get("user_emotion") and context["user_emotion"] != "neutral":
            prompt_parts.append(f"[EMOÃ‡ÃƒO] UsuÃ¡rio estÃ¡: {context['user_emotion']}")

        # Adicionar contexto de memÃ³ria (RAG)
        if context.get("memory_context"):
            prompt_parts.append(f"\n{context['memory_context']}")

        # Adicionar OCR
        if context.get("ocr_text"):
            ocr_preview = context["ocr_text"][:500]
            prompt_parts.append(f"\n[TEXTO NA TELA] {ocr_preview}")

        enriched_prompt = "\n".join(prompt_parts)
        logger.debug(f"ðŸ“ Prompt: {len(enriched_prompt)} caracteres")
        return enriched_prompt

    async def _call_llm(
        self, prompt: str, provider: str, image_path: Optional[str]
    ) -> str:
        """Chama LLM apropriado"""

        if provider == "ollama":
            # Usa o modelo selecionado pelo roteador ou o padrão
            model = getattr(self, "current_model", "gemma3:4b")
            return await self._call_ollama_async(prompt, image_path, model=model)
        elif provider == "local":
            return await self._call_local_async(prompt)
        elif provider.startswith("cloud:"):
            model_name = provider.split(":")[1]
            return await self._call_cloud_generic_async(model_name, prompt)
        else:
            logger.error(f"âŒ Provider desconhecido: {provider}")
            return "Desculpe, nÃ£o consegui processar sua solicitaÃ§Ã£o."

    async def _call_cloud_generic_async(self, model: str, prompt: str) -> str:
        """Chama provedores de nuvem genÃ©ricos (DeepSeek, OpenAI)"""
        # ImplementaÃ§Ã£o simplificada para DeepSeek como exemplo
        if "deepseek" in model.lower():
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                return "Erro: API Key do DeepSeek nÃ£o configurada."

            try:
                # Simulando chamada para DeepSeek
                logger.info(f"ðŸŒ Chamando Nuvem ({model})...")
                # Aqui viria a lÃ³gica de request real para OpenRouter/DeepSeek
                return f"[RESPOSTA CLOUD {model}] Esta Ã© uma resposta processada na nuvem."
            except Exception as e:
                logger.error(f"Erro na nuvem: {e}")
                return await self._call_local_async(prompt)

        return await self._call_local_async(prompt)

    async def _call_ollama_async(
        self, prompt: str, image_path: Optional[str], model: str = "gemma3:4b"
    ) -> str:
        """Chama Ollama API de forma assíncrona"""
        try:
            # Preparar payload
            payload = {
                "model": model,
                "prompt": f"{self.system_prompt}\n\n{prompt}",
                "stream": False,
            }

            # Adicionar imagem se disponÃ­vel
            if image_path and Path(image_path).exists():
                import base64

                with open(image_path, "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")
                payload["images"] = [img_data]

            # HTTP request async com timeout de 30s
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        logger.info(f"âœ… Ollama response: {len(response_text)} chars")
                        return response_text
                    else:
                        logger.error(f"âŒ Ollama error: {response.status}")
                        return await self._call_local_async(prompt)

        except Exception as e:
            logger.error(f"âŒ Erro no Ollama: {e}")
            return await self._call_local_async(prompt)

    async def _call_local_async(self, prompt: str) -> str:
        """Chama LocalBrain (Qwen 1.5B) de forma assÃ­ncrona"""
        if not self.local_brain:
            logger.error("âŒ LocalBrain nÃ£o disponÃ­vel")
            return "Desculpe, nÃ£o consegui processar sua solicitaÃ§Ã£o."

        try:
            # Rodar em thread separada (LocalBrain Ã© CPU-bound)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self.local_brain.generate_response, prompt, self.system_prompt
            )
            logger.info(f"âœ… LocalBrain response: {len(response)} chars")
            return response
        except Exception as e:
            logger.error(f"âŒ Erro no LocalBrain: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitaÃ§Ã£o."


# ============================================================================
# SINGLETON GETTER
# ============================================================================
_decision_engine_instance = None


def get_decision_engine(provider: str = "ollama") -> DecisionEngine:
    """Retorna instÃ¢ncia singleton do DecisionEngine"""
    global _decision_engine_instance
    if _decision_engine_instance is None:
        _decision_engine_instance = DecisionEngine(provider)
    return _decision_engine_instance
