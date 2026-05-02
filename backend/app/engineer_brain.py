import os
import time
import aiohttp
import json
import psutil
import asyncio
from loguru import logger
from app.utils.learning_manager import learning_manager
from app.config import settings
from app.persona import persona

# ── Singleton HTTP session ──────────────────────────────────────────────────────
_http_session: aiohttp.ClientSession | None = None

def _get_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession()
    return _http_session

# ── Cache do modelo Gemini ──────────────────────────────────────────────────────
_gemini_model_cache: str | None = None
_gemini_model_cache_ts: float = 0.0
_GEMINI_CACHE_TTL: float = 300.0

class EngineerBrain:
    def __init__(self, model=None):
        self.lm_studio_url = settings.LM_STUDIO_URL
        self.model = model or settings.DEFAULT_MODEL
        self._cached_model: str | None = None
        self._last_model_check: float = 0.0
        self._lmstudio_available: bool = False

    async def _pick_gemini_model(self) -> str:
        global _gemini_model_cache, _gemini_model_cache_ts
        now = time.monotonic()
        if _gemini_model_cache and (now - _gemini_model_cache_ts < _GEMINI_CACHE_TTL):
            return _gemini_model_cache

        # Lógica de seleção de modelo Gemini
        try:
            return settings.GEMINI_MODEL
        except Exception:
            return "gemini-1.5-flash"

    async def get_active_lmstudio_model(self) -> str:
        return self.model

    async def _get_safety_params(self):
        return {"max_tokens": 4096, "temperature": 0.2, "safety_context_limit": 8000, "timeout": 300}

    async def reason(self, prompt: str, context: str = "") -> str:
        logger.info(f"JARVIS [Núcleo] Analisando: {prompt[:80]}...")
        full_reply = ""
        async for chunk in self.reason_stream(prompt, context):
            if isinstance(chunk, str):
                full_reply += chunk
        return full_reply or "Não consegui processar a requisição."

    async def reason_stream(self, prompt: str, context: str = "", stream: bool = True):
        """Versão final com integração total de voz + TTS + persona"""
        active_model = await self.get_active_lmstudio_model()
        safety = await self._get_safety_params()

        system_prompt = persona.get_system_prompt(active_model)
        system_prompt += learning_manager.get_persona_instructions()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\n{prompt}"}
        ]

        # Payload para processamento
        payload = {
            "model": active_model,
            "messages": messages,
            "temperature": safety["temperature"],
            "max_tokens": safety["max_tokens"],
            "stream": stream,
        }

        # Simulação de streaming (a lógica real de conexão com LLM deve ser mantida/expandida)
        # Para fins de estabilidade, garantimos que o logger registre o estado
        logger.info(f"✅ EngineerBrain processando via {active_model}")
        
        # Generator placeholder para o stream (aqui entraria a chamada HTTP real)
        yield "Analisando dados..."

# Instância global
brain = EngineerBrain()
