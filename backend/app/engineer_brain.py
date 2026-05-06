import os
import time
import aiohttp
import json
import psutil
import asyncio
from loguru import logger
from .smart_router import router

from .config import settings

# ── Singleton HTTP session ──────────────────────────────────────────────────────
# Uma única ClientSession reutilizada por todas as chamadas (keep-alive, connection pool).
_http_session: aiohttp.ClientSession | None = None

def _get_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession()
    return _http_session

# ── Cache do modelo Gemini ──────────────────────────────────────────────────────
# Evita sondagem cara (4 × 8 s) a cada chamada. TTL de 5 minutos.
_gemini_model_cache: str | None = None
_gemini_model_cache_ts: float = 0.0
_GEMINI_CACHE_TTL: float = 300.0  # segundos


class EngineerBrain:
    def __init__(self, model=None):
        self.lm_studio_url = settings.LM_STUDIO_URL
        self.model = model or settings.DEFAULT_MODEL
        self._cached_model: str | None = None
        self._last_model_check: float = 0.0
        # Tracks whether the last /models probe succeeded — evita double-timeout quando offline
        self._lmstudio_available: bool = False

    async def _pick_gemini_model(self) -> str:
        """
        Resolve um modelo Gemini válido para streamGenerateContent.
        Resultado mantido em cache por 5 minutos — elimina o custo de sondagem por chamada.
        """
        global _gemini_model_cache, _gemini_model_cache_ts

        now = time.monotonic()
        if _gemini_model_cache and (now - _gemini_model_cache_ts < _GEMINI_CACHE_TTL):
            return _gemini_model_cache

        gemini_key = settings.GEMINI_API_KEY
        preferred = [
            settings.GEMINI_MODEL,
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash-latest",
        ]
        seen: set[str] = set()
        ordered: list[str] = []
        for item in preferred:
            if item and item not in seen:
                seen.add(item)
                ordered.append(item)

        session = _get_session()
        for model in ordered:
            test_url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                f"?key={gemini_key}"
            )
            test_payload = {
                "contents": [{"role": "user", "parts": [{"text": "ping"}]}],
                "generationConfig": {"maxOutputTokens": 1},
            }
            try:
                async with session.post(
                    test_url, json=test_payload, timeout=aiohttp.ClientTimeout(total=6)
                ) as response:
                    if response.status in (200, 400):
                        _gemini_model_cache = model
                        _gemini_model_cache_ts = now
                        logger.info(f"🔍 Modelo Gemini resolvido e cacheado: {model}")
                        return model
            except Exception:
                continue

        # Fallback: listagem dinâmica
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
            async with session.get(list_url, timeout=aiohttp.ClientTimeout(total=6)) as response:
                if response.status == 200:
                    data = await response.json()
                    for m in data.get("models", []):
                        name = m.get("name", "")
                        methods = m.get("supportedGenerationMethods", [])
                        if "generateContent" in methods and name.startswith("models/"):
                            resolved = name.split("/", 1)[1]
                            _gemini_model_cache = resolved
                            _gemini_model_cache_ts = now
                            return resolved
        except Exception:
            pass

        fallback = settings.GEMINI_MODEL
        _gemini_model_cache = fallback
        _gemini_model_cache_ts = now
        return fallback

    async def get_active_lmstudio_model(self) -> str:
        """Busca automaticamente o modelo ativo no LM Studio Local com cache de 30s."""
        now = time.monotonic()
        if self._cached_model and (now - self._last_model_check < 30):
            return self._cached_model

        url = self.lm_studio_url.replace("/chat/completions", "/models")
        try:
            session = _get_session()
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])
                    if models:
                        active = models[0].get("id")
                        logger.info(f"🧠 Cérebro detectado no LM Studio: {active}")
                        self._cached_model = active
                        self._last_model_check = now
                        self._lmstudio_available = True
                        return active
        except Exception:
            pass

        logger.warning("⚠️ LM Studio não detectado ou porta 1234 fechada.")
        self._lmstudio_available = False
        self._cached_model = self.model
        self._last_model_check = now
        return self.model

    async def _get_safety_params(self):
        """Monitora o hardware e retorna parâmetros para máxima inteligência vs estabilidade."""
        ram_percent = psutil.virtual_memory().percent
        # Em carga extrema, reduzimos a janela de contexto para proteger a estabilidade,
        # mas mantemos a temperatura baixa para garantir que ele continue 'inteligente' e técnico.
        if ram_percent >= 90:
            logger.warning(f"🚀 ALTA CARGA DETECTADA: RAM {ram_percent}%. Priorizando Contexto Crítico.")
            return {
                "max_tokens": 1024,
                "temperature": 0.1,
                "safety_context_limit": 3500,
                "timeout": 300
            }

        return {
            "max_tokens": 4096,
            "temperature": 0.2,
            "safety_context_limit": 8000,
            "timeout": 300
        }

    async def reason(self, prompt: str, context: str = "") -> str:
        """Processa a tarefa e retorna a resposta completa (Não-Streaming)."""
        logger.info(f"JARVIS [Núcleo High-Load] Analisando (Sync): {prompt[:50]}...")

        full_reply = ""
        async for chunk in self.reason_stream(prompt, context, stream=True):
            if isinstance(chunk, str) and not chunk.startswith("Erro técnico") and not chunk.startswith("O processamento falhou"):
                full_reply += chunk

        return full_reply if full_reply else "O cérebro não conseguiu processar esta requisição ou o servidor local caiu."

    async def reason_stream(self, prompt: str, context: str = "", stream: bool = True):
        """Processa a tarefa gerando chunks (Streaming) via SmartRouter."""
        from .persona import persona

        system_prompt = persona.get_system_prompt()

        # Injeção Anti-Alucinação Reforçada
        system_prompt += (
            "\n[DIRETIVA DE FIDELIDADE]: Se a informação não estiver na 'Memória Ativa', "
            "você deve informar que não possui esse dado localmente. "
            "Você tem permissão para sugerir o uso de 'browser_navigate' para buscar o fato na internet caso necessário."
        )

        # Injeção de Persona Evolutiva
        system_prompt += learning_manager.get_persona_instructions()

        user_content = persona.format_prompt(prompt, context, "Hybrid-Router")

        # Delegação para o SmartRouter
        async for chunk in router.reason_stream(user_content, system_prompt):
            yield chunk

    async def reason_local(self, prompt: str, context: str = "", model: str = None):
        """Versão simplificada para chamadas rápidas locais."""
        if model:
            self.model = model
        return await self.reason(prompt, context=context)


# Singleton para uso no sistema
brain = EngineerBrain()
