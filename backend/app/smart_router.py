"""
JARVIS 5.0 - Smart LLM Router
Implementa orquestração híbrida com hierarquia de redundância,
análise de complexidade (Fast vs Deep Thinking) e fallbacks dinâmicos.
"""

import asyncio
import time
import json
import aiohttp
import psutil
from typing import AsyncGenerator, List, Dict, Any, Optional
from loguru import logger
from .http_client import get_http_session

from .config import settings
from .utils.learning_manager import learning_manager

# ── Gemini Model Cache ─────────────────────────────────────────────────────────
_gemini_model_cache: str | None = None
_gemini_model_cache_ts: float = 0.0
_GEMINI_CACHE_TTL: float = 300.0

class SmartRouter:
    def __init__(self):
        self.lm_studio_url = settings.LM_STUDIO_URL
        self.default_local_model = settings.DEFAULT_MODEL
        self._cached_local_model: str | None = None
        self._last_local_check: float = 0.0
        self._local_available: bool = False

    async def _detect_complexity(self, prompt: str) -> str:
        """
        Analisa a complexidade da query para decidir entre 'fast' ou 'deep' thinking.
        """
        # Critérios simples de detecção de complexidade
        complex_keywords = ["analise", "refatore", "arquitetura", "estratégia", "complexo", "debug", "otimize"]
        is_complex = any(kw in prompt.lower() for kw in complex_keywords) or len(prompt) > 500

        # Se o sistema estiver sob carga extrema, forçamos 'fast' para evitar crash
        ram = psutil.virtual_memory().percent
        if ram > 90:
            return "fast"

        return "deep" if is_complex else "fast"

    async def _resolve_gemini_model(self) -> str:
        global _gemini_model_cache, _gemini_model_cache_ts
        now = time.monotonic()
        if _gemini_model_cache and (now - _gemini_model_cache_ts < _GEMINI_CACHE_TTL):
            return _gemini_model_cache

        preferred = [settings.GEMINI_MODEL, "gemini-2.0-flash", "gemini-1.5-flash-latest"]
        session = get_http_session()
        for model in preferred:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
                async with session.post(url, json={"contents": [{"parts": [{"text": "ping"}]}]}, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                    if resp.status in (200, 400):
                        _gemini_model_cache, _gemini_model_cache_ts = model, now
                        return model
            except Exception: continue
        return settings.GEMINI_MODEL

    async def _get_local_model(self) -> str:
        now = time.monotonic()
        if self._cached_local_model and (now - self._last_local_check < 30):
            return self._cached_local_model

        url = self.lm_studio_url.replace("/chat/completions", "/models")
        try:
            session = get_http_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("data"):
                        model = data["data"][0]["id"]
                        self._cached_local_model, self._last_local_check, self._local_available = model, now, True
                        return model
        except Exception: pass
        self._local_available = False
        return self.default_local_model

    async def _call_gemini(self, prompt: str, system_prompt: str, stream: bool) -> AsyncGenerator[str, None]:
        model = await self._resolve_gemini_model()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={settings.GEMINI_API_KEY}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096}
        }
        session = get_http_session()
        async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                raise Exception(f"Gemini API Error: {resp.status}")

            first_chunk = True
            async for line in resp.content:
                line_str = line.decode("utf-8").strip()
                if line_str.startswith("data: "):
                    try:
                        data = json.loads(line_str[6:])
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        if first_chunk:
                            yield " [Gemini] "
                            first_chunk = False
                        yield text
                    except Exception: continue

    async def _call_nvidia(self, prompt: str, system_prompt: str, stream: bool) -> AsyncGenerator[str, None]:
        raise NotImplementedError("NVIDIA endpoint not configured in settings")

    async def _call_local(self, prompt: str, system_prompt: str, stream: bool) -> AsyncGenerator[str, None]:
        model = await self._get_local_model()
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            "temperature": 0.2,
            "stream": stream,
            "max_tokens": 4096
        }
        session = get_http_session()
        async with session.post(self.lm_studio_url, json=payload, timeout=aiohttp.ClientTimeout(total=settings.LM_STUDIO_TIMEOUT)) as resp:
            if resp.status != 200:
                raise Exception(f"Local LLM Error: {resp.status}")

            if stream:
                first_chunk = True
                async for line in resp.content:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        if line_str == "data: [DONE]": break
                        try:
                            data = json.loads(line_str[6:])
                            text = data["choices"][0]["delta"].get("content", "")
                            if text:
                                if first_chunk:
                                    yield " [Local] "
                                    first_chunk = False
                                yield text
                        except Exception: continue
            else:
                data = await resp.json()
                yield data["choices"][0]["message"]["content"]

    async def _call_openrouter(self, prompt: str, system_prompt: str, stream: bool) -> AsyncGenerator[str, None]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "X-Title": "JARVIS 5.0"}
        payload = {
            "model": settings.OPENROUTER_MODEL,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            "stream": stream,
            "temperature": 0.2
        }
        session = get_http_session()
        async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                raise Exception(f"OpenRouter Error: {resp.status}")

            first_chunk = True
            async for line in resp.content:
                line_str = line.decode("utf-8").strip()
                if line_str.startswith("data: "):
                    if line_str == "data: [DONE]": break
                    try:
                        data = json.loads(line_str[6:])
                        text = data["choices"][0].get("delta", {}).get("content", "")
                        if text:
                            if first_chunk:
                                yield " [OpenRouter] "
                                first_chunk = False
                            yield text
                    except Exception: continue

    async def reason_stream(self, prompt: str, system_prompt: str) -> AsyncGenerator[str, None]:
        complexity = await self._detect_complexity(prompt)
        logger.info(f"🧠 Roteamento: Complexidade={complexity}")

        # Hierarquia Baseada em Complexidade e Resiliência
        # Deep Thinking: Gemini -> NVIDIA -> Local -> OpenRouter
        # Fast Thinking: Local -> Gemini -> OpenRouter

        if complexity == "deep":
            pipeline = [
                ("Gemini", self._call_gemini),
                ("NVIDIA", self._call_nvidia),
                ("Local", self._call_local),
                ("OpenRouter", self._call_openrouter),
            ]
        else:
            pipeline = [
                ("Local", self._call_local),
                ("Gemini", self._call_gemini),
                ("OpenRouter", self._call_openrouter),
            ]

        for name, provider in pipeline:
            try:
                logger.info(f"🛰️ Tentando provedor: {name}")
                # Implementação de timeout dinâmico por provedor
                async for chunk in provider(prompt, system_prompt, stream=True):
                    yield chunk
                return # Sucesso!
            except Exception as e:
                logger.warning(f"⚠️ Provedor {name} falhou: {e}. Saltando para próximo...")
                continue

        yield "❌ Erro crítico: Todos os modelos de linguagem falharam ou estão offline."

# Singleton para integração
router = SmartRouter()
