import os
import time
import aiohttp
import json
import psutil
import asyncio
from loguru import logger
from .utils.learning_manager import learning_manager

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
        """Processa a tarefa gerando chunks (Streaming)."""
        from .persona import persona
        active_model = await self.get_active_lmstudio_model()
        safety = await self._get_safety_params()

        system_prompt = persona.get_system_prompt()

        # Injeção Anti-Alucinação Reforçada
        system_prompt += (
            "\n[DIRETIVA DE FIDELIDADE]: Se a informação não estiver na 'Memória Ativa', "
            "você deve informar que não possui esse dado localmente. "
            "Você tem permissão para sugerir o uso de 'browser_navigate' para buscar o fato na internet caso necessário."
        )

        # Injeção de Persona Evolutiva
        system_prompt += learning_manager.get_persona_instructions()

        user_content = persona.format_prompt(prompt, context, active_model)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content[:safety["safety_context_limit"]]}
        ]

        payload = {
            "model": active_model,
            "messages": messages,
            "temperature": safety["temperature"],
            "max_tokens": safety["max_tokens"],
            "stream": stream,
        }

        # ── Prioridade 0: Motor Nativo (GGUF local via llama-cpp) ─────────────
        try:
            from .native_brain import get_native_brain
            native = get_native_brain()
            if native:
                logger.info("🧠 Usando Motor Nativo (GGUF)...")
                async for chunk in native.generate(prompt, system_prompt=system_prompt, stream=stream):
                    yield chunk
                return
        except Exception as e:
            logger.warning(f"⚠️ Motor Nativo falhou: {e}")

        # ── Prioridade 0.5: Ollama (offline total) ─────────────────────────────
        if getattr(settings, 'OLLAMA_ENABLED', False):
            try:
                session = _get_session()
                url = f"{getattr(settings, 'OLLAMA_URL', 'http://localhost:11434')}/api/chat"
                async with session.post(
                    url,
                    json={"model": getattr(settings, 'OLLAMA_MODEL', 'llama3'), "messages": messages, "stream": True},
                    timeout=aiohttp.ClientTimeout(total=getattr(settings, 'OLLAMA_TIMEOUT', 30)),
                ) as resp:
                    if resp.status == 200:
                        async for line in resp.content:
                            line_str = line.decode('utf-8', errors='ignore').strip()
                            if line_str:
                                try:
                                    chunk = json.loads(line_str)
                                    text = chunk.get('message', {}).get('content', '')
                                    if text:
                                        yield text
                                except Exception:
                                    continue
                        return
            except Exception as e:
                logger.warning(f"Ollama offline: {e}")

        # ── Prioridade 1: LM Studio local ─────────────────────────────────────
        # Pula imediatamente se a última sondagem de /models falhou.
        if self._lmstudio_available:
            try:
                session = _get_session()
                logger.info(f"🧠 Tentando resposta via LM Studio ({self.model})...")
                async with session.post(
                    self.lm_studio_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=settings.LM_STUDIO_TIMEOUT),
                ) as response:
                    if response.status == 200:
                        if stream:
                            async for line in response.content:
                                if not line:
                                    continue
                                try:
                                    line_str = line.decode("utf-8", errors="ignore").strip()
                                    if line_str.startswith("data: "):
                                        data_content = line_str[6:].strip()
                                        if data_content == "[DONE]":
                                            break
                                        chunk_data = json.loads(data_content)
                                        if chunk_data.get("choices"):
                                            content = chunk_data["choices"][0]["delta"].get("content", "")
                                            if content:
                                                yield content
                                except Exception:
                                    continue
                            return
                        else:
                            lms_data = await response.json()
                            text = lms_data["choices"][0]["message"]["content"]
                            learning_manager.learn_from_interaction(prompt, text)
                            yield text
                            return
                    else:
                        logger.warning(f"⚠️ LM Studio retornou status {response.status}. Tentando Gemini...")
            except Exception as e:
                logger.warning(f"⚠️ LM Studio falhou durante geração: {e}. Tentando Gemini...")
        else:
            logger.info("⏭️ LM Studio indisponível (probe falhou). Indo direto para Gemini...")

        # ── Prioridade 2: Gemini via streamGenerateContent (SSE real) ─────────
        gemini_key = settings.GEMINI_API_KEY
        if not gemini_key:
            logger.warning("❌ Gemini Key não configurada.")
        else:
            try:
                gemini_model = await self._pick_gemini_model()
                logger.info(f"☁️ Chamando Gemini streaming ({gemini_model})")
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{gemini_model}:streamGenerateContent?alt=sse&key={gemini_key}"
                )
                gemini_payload = {
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [
                        {"role": "user", "parts": [{"text": user_content[:safety["safety_context_limit"]]}]}
                    ],
                    "generationConfig": {
                        "temperature": safety["temperature"],
                        "maxOutputTokens": safety["max_tokens"],
                    },
                }

                session = _get_session()
                has_content = False
                async with session.post(
                    url, json=gemini_payload, timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        async for raw_line in response.content:
                            line_str = raw_line.decode("utf-8", errors="ignore").strip()
                            if not line_str.startswith("data: "):
                                continue
                            data_str = line_str[6:].strip()
                            if not data_str or data_str == "[DONE]":
                                continue
                            try:
                                chunk_data = json.loads(data_str)
                                candidates = chunk_data.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    for part in parts:
                                        text = part.get("text", "")
                                        if text:
                                            if not has_content:
                                                yield " [Modo Cloud] "
                                                has_content = True
                                            yield text
                            except Exception:
                                continue
                        if has_content:
                            logger.success("✅ Resposta recebida via Gemini (streaming)")
                            return
                    else:
                        error_body = await response.text()
                        logger.error(f"❌ Gemini erro {response.status}: {error_body}")
                        # Invalida cache para forçar nova sondagem na próxima chamada
                        global _gemini_model_cache_ts
                        _gemini_model_cache_ts = 0.0
            except Exception as e:
                logger.error(f"❌ Falha crítica no fallback Gemini: {e}")

        # ── Prioridade 3: OpenRouter via streaming SSE ─────────────────────────
        or_key = settings.OPENROUTER_API_KEY
        if not or_key:
            logger.warning("❌ OpenRouter API Key não encontrada no ambiente.")
        else:
            try:
                logger.info(f"☁️ Chamando OpenRouter (Key: {or_key[:4]}...{or_key[-4:]})")
                # Deduplica candidatos mantendo ordem de preferência
                seen_or: set[str] = set()
                unique_candidates: list[str] = []
                for c in [settings.OPENROUTER_MODEL, "google/gemini-2.5-flash", "google/gemini-2.0-flash-001", "google/gemini-flash-1.5"]:
                    if c and c not in seen_or:
                        seen_or.add(c)
                        unique_candidates.append(c)

                session = _get_session()
                for candidate in unique_candidates:
                    try:
                        async with session.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {or_key}",
                                "Content-Type": "application/json",
                                "X-Title": "JARVIS 5.0",
                            },
                            json={
                                "model": candidate,
                                "messages": messages,
                                "stream": True,
                            },
                            timeout=aiohttp.ClientTimeout(total=60),
                        ) as response:
                            if response.status == 200:
                                has_or_content = False
                                async for raw_line in response.content:
                                    line_str = raw_line.decode("utf-8", errors="ignore").strip()
                                    if not line_str.startswith("data: "):
                                        continue
                                    data_str = line_str[6:].strip()
                                    if not data_str or data_str == "[DONE]":
                                        continue
                                    try:
                                        chunk_data = json.loads(data_str)
                                        if chunk_data.get("choices"):
                                            content = chunk_data["choices"][0].get("delta", {}).get("content", "")
                                            if content:
                                                if not has_or_content:
                                                    yield " [OpenRouter] "
                                                    has_or_content = True
                                                yield content
                                    except Exception:
                                        continue
                                if has_or_content:
                                    logger.success(f"✅ Resposta recebida via OpenRouter ({candidate})")
                                    return
                            else:
                                error_body = await response.text()
                                logger.warning(f"⚠️ OpenRouter {candidate} erro {response.status}: {error_body}")
                    except Exception as e:
                        logger.warning(f"⚠️ OpenRouter {candidate} falhou: {e}")
                        continue
            except Exception as e:
                logger.error(f"❌ Falha crítica no OpenRouter: {e}")

        yield "Sistemas offline. Verifique suas Chaves de API no arquivo .env ou a conexão com a internet."

    async def reason_local(self, prompt: str, context: str = "", model: str = None):
        """Versão simplificada para chamadas rápidas locais."""
        if model:
            self.model = model
        return await self.reason(prompt, context=context)


# Singleton para uso no sistema
brain = EngineerBrain()
