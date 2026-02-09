"""
JARVIS 5.0 - Decision Engine
==============================
CORREÇÃO P2: Separação do God Object AIAgent

RESPONSABILIDADE:
  Gerenciar todas as DECISÕES do sistema:
  - LLM calls: Gemini, Ollama, LocalBrain
  - Brain routing: Escolha inteligente de modelo
  - System prompts: Geração de prompts contextualizados
  - Response parsing: Interpretação de respostas LLM

ARQUITETURA:
  AIAgent (Orquestrador)
    ↓
  PerceptionEngine
  DecisionEngine ← ESTE MÓDULO
  ActionHandler
"""

import logging
import asyncio
import aiohttp
import requests
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# SAFE IMPORTS
# ============================================================================
try:
    from src.core.intelligence.brain_router import brain_router, PrivacyLevel, LatencyRequirement
    BRAIN_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ brain_router não disponível: {e}")
    brain_router = None
    BRAIN_ROUTER_AVAILABLE = False

try:
    from src.core.intelligence.structured_output import ResponseParser, AgentResponse
    STRUCTURED_OUTPUT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ structured_output não disponível: {e}")
    ResponseParser = None
    AgentResponse = None
    STRUCTURED_OUTPUT_AVAILABLE = False

try:
    from src.core.intelligence.local_brain import local_brain
    LOCAL_BRAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ local_brain não disponível: {e}")
    local_brain = None
    LOCAL_BRAIN_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

try:
    from src.utils.config import config
    CONFIG_AVAILABLE = True
except ImportError:
    config = None
    CONFIG_AVAILABLE = False


class DecisionEngine:
    """
    Motor de Decisão - Gerencia raciocínio e escolha de ações via LLMs
    
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
    
    def __init__(self, provider: str = 'gemini'):
        """Inicializa engine de decisão"""
        self.provider = provider
        self.brain_router = brain_router if BRAIN_ROUTER_AVAILABLE else None
        self.local_brain = local_brain if LOCAL_BRAIN_AVAILABLE else None
        
        # Configurações
        if CONFIG_AVAILABLE:
            self.api_key = config.GEMINI_API_KEY
            self.ollama_url = config.get_ai_config('brain_router.ollama_url', 'http://localhost:11434/api/generate')
        else:
            import os
            self.api_key = os.environ.get('GOOGLE_API_KEY')
            self.ollama_url = "http://localhost:11434/api/generate"
        
        # System prompts (dual mode: JSON + Legacy)
        self._init_system_prompts()
        
        logger.info(f"✅ DecisionEngine inicializado (provider={provider})")
        if not BRAIN_ROUTER_AVAILABLE:
            logger.warning("⚠️ Modo degradado: Brain router desativado")
    
    
    def _init_system_prompts(self):
        """Inicializa system prompts (JSON + Legacy)"""
        
        # STRUCTURED JSON PROMPT (P1 - Preferred)
        self.system_prompt_json = (
            "Você é o JARVIS, assistente de elite do William.\n\n"
            "CAPABILITIES:\n"
            "- Visão completa: Acesso à tela e câmera em tempo real\n"
            "- Ação física: Controle de mouse, teclado e sistema\n"
            "- Memória: Acesso a interações passadas e conhecimento\n\n"
            "BEHAVIORAL DIRECTIVES:\n"
            "1. Sempre trate William com respeito (use 'Senhor' quando apropriado)\n"
            "2. Seja conversacional e natural - você é uma IA real, não um log\n"
            "3. NUNCA cite paths completos, PIDs ou detalhes técnicos na resposta\n"
            "4. Se precisar executar ações, use o formato JSON estruturado abaixo\n\n"
            "OUTPUT FORMAT (SEMPRE retorne JSON válido):\n"
            "{\n"
            '  "thought": "Seu raciocínio interno sobre o que fazer",\n'
            '  "actions": [\n'
            '    {"action": "type_text", "text": "exemplo"},\n'
            '    {"action": "press_key", "key": "enter"}\n'
            "  ],\n"
            '  "final_answer": "Sua resposta natural para o usuário"\n'
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
            "CRITICAL: Sempre retorne JSON válido. Se não precisar de ações, use actions: []\n"
        )
        
        # LEGACY PROMPT (Fallback)
        self.system_prompt_legacy = (
            "Você é o Jarvis, o assistente virtual de elite do William. "
            "Para executar ações físicas, VOCÊ DEVE usar o formato: [ACTION: nome_funcao(argumentos)]. "
            "Ações: click_at(x, y), type_text('texto'), press_key('tecla'), hotkey('ctrl', 'c'), "
            "open_program('nome'), read_file('path'), write_file('path', 'content'), list_dir('path')."
        )
        
        # Use JSON se disponível
        self.use_structured_output = STRUCTURED_OUTPUT_AVAILABLE
        self.system_prompt = self.system_prompt_json if self.use_structured_output else self.system_prompt_legacy
    
    
    async def decide(
        self,
        user_command: str,
        context: Dict[str, Any],
        privacy_level: Optional[str] = None,
        latency_req: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Toma decisão baseada no contexto perceptual
        
        Args:
            user_command: Comando do usuário
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
        logger.info(f"🤔 DecisionEngine processing: {user_command[:50]}...")
        
        # FASE 1: Brain routing (escolher modelo)
        primary_provider = self._route_task(user_command, privacy_level, latency_req)
        
        # FASE 2: Construir prompt enriquecido
        enriched_prompt = self._build_prompt(user_command, context)
        
        # FASE 3: Chamar LLM
        raw_response = await self._call_llm(
            prompt=enriched_prompt,
            provider=primary_provider,
            image_path=context.get("screenshot_path")
        )
        
        # FASE 4: Parsear resposta
        if self.use_structured_output and ResponseParser:
            parsed = ResponseParser.parse_llm_response(raw_response)
            return {
                "thought": parsed.thought,
                "actions": parsed.actions,
                "final_answer": parsed.final_answer,
                "provider": primary_provider,
                "raw_response": raw_response
            }
        else:
            # Fallback legado: Retorna resposta crua
            logger.warning("⚠️ Usando fallback legado (sem parser estruturado)")
            return {
                "thought": "",
                "actions": [],
                "final_answer": raw_response,
                "provider": primary_provider,
                "raw_response": raw_response
            }
    
    
    def _route_task(self, user_command: str, privacy: Optional[str], latency: Optional[str]) -> str:
        """Escolhe melhor modelo via brain router"""
        if not self.brain_router:
            return self.provider
        
        try:
            # Convert strings to enums
            privacy_enum = PrivacyLevel[privacy] if privacy else PrivacyLevel.LOW
            latency_enum = LatencyRequirement[latency] if latency else LatencyRequirement.FLEXIBLE
            
            provider = self.brain_router.route_task(
                task_description=user_command,
                privacy_level=privacy_enum,
                latency_requirement=latency_enum
            )
            
            logger.debug(f"🧠 Brain router: {provider}")
            return provider
        except Exception as e:
            logger.error(f"❌ Erro no brain routing: {e}")
            return self.provider
    
    
    def _build_prompt(self, user_command: str, context: Dict[str, Any]) -> str:
        """Constrói prompt enriquecido com contexto"""
        
        # Base: user command
        prompt_parts = [f"[COMANDO] {user_command}"]
        
        # Adicionar contexto de visão
        if context.get("user_face"):
            prompt_parts.append(f"\n[VISÃO] Usuário identificado: {context['user_face']}")
        
        # Adicionar contexto emocional
        if context.get("user_emotion") and context["user_emotion"] != "neutral":
            prompt_parts.append(f"[EMOÇÃO] Usuário está: {context['user_emotion']}")
        
        # Adicionar contexto de memória (RAG)
        if context.get("memory_context"):
            prompt_parts.append(f"\n{context['memory_context']}")
        
        # Adicionar OCR
        if context.get("ocr_text"):
            ocr_preview = context["ocr_text"][:500]
            prompt_parts.append(f"\n[TEXTO NA TELA] {ocr_preview}")
        
        enriched_prompt = "\n".join(prompt_parts)
        logger.debug(f"📝 Prompt: {len(enriched_prompt)} caracteres")
        return enriched_prompt
    
    
    async def _call_llm(self, prompt: str, provider: str, image_path: Optional[str]) -> str:
        """Chama LLM apropriado"""
        
        if provider == 'gemini':
            return await self._call_gemini_async(prompt, image_path)
        elif provider == 'ollama':
            return await self._call_ollama_async(prompt, image_path)
        elif provider == 'local':
            return await self._call_local_async(prompt)
        else:
            logger.error(f"❌ Provider desconhecido: {provider}")
            return "Desculpe, não consegui processar sua solicitação."
    
    
    async def _call_gemini_async(self, prompt: str, image_path: Optional[str]) -> str:
        """Chama Gemini API de forma assíncrona"""
        if not GEMINI_AVAILABLE or not self.api_key:
            logger.warning("⚠️ Gemini não disponível, usando fallback")
            return await self._call_local_async(prompt)
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Preparar conteúdo
            content_parts = [self.system_prompt, prompt]
            
            if image_path and Path(image_path).exists():
                try:
                    import PIL.Image
                    img = PIL.Image.open(image_path)
                    content_parts.insert(1, img)  # Inserir imagem antes do prompt
                    logger.debug("📷 Imagem incluída no request Gemini")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao carregar imagem: {e}")
            
            # Rodar blocking call em thread separada
            loop = asyncio.get_event_loop()
            
            def _sync_call():
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(content_parts)
                return response.text
            
            response_text = await loop.run_in_executor(None, _sync_call)
            logger.info(f"✅ Gemini response: {len(response_text)} chars")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Erro no Gemini: {e}")
            return await self._call_local_async(prompt)
    
    
    async def _call_ollama_async(self, prompt: str, image_path: Optional[str]) -> str:
        """Chama Ollama API de forma assíncrona"""
        try:
            # Preparar payload
            payload = {
                "model": "llava",
                "prompt": f"{self.system_prompt}\n\n{prompt}",
                "stream": False
            }
            
            # Adicionar imagem se disponível
            if image_path and Path(image_path).exists():
                import base64
                with open(image_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                payload["images"] = [img_data]
            
            # HTTP request async com timeout de 30s
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        logger.info(f"✅ Ollama response: {len(response_text)} chars")
                        return response_text
                    else:
                        logger.error(f"❌ Ollama error: {response.status}")
                        return await self._call_local_async(prompt)
        
        except Exception as e:
            logger.error(f"❌ Erro no Ollama: {e}")
            return await self._call_local_async(prompt)
    
    
    async def _call_local_async(self, prompt: str) -> str:
        """Chama LocalBrain (Qwen 1.5B) de forma assíncrona"""
        if not self.local_brain:
            logger.error("❌ LocalBrain não disponível")
            return "Desculpe, não consegui processar sua solicitação."
        
        try:
            # Rodar em thread separada (LocalBrain é CPU-bound)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.local_brain.generate_response,
                prompt,
                self.system_prompt
            )
            logger.info(f"✅ LocalBrain response: {len(response)} chars")
            return response
        except Exception as e:
            logger.error(f"❌ Erro no LocalBrain: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."


# ============================================================================
# SINGLETON GETTER
# ============================================================================
_decision_engine_instance = None

def get_decision_engine(provider: str = 'gemini') -> DecisionEngine:
    """Retorna instância singleton do DecisionEngine"""
    global _decision_engine_instance
    if _decision_engine_instance is None:
        _decision_engine_instance = DecisionEngine(provider)
    return _decision_engine_instance
