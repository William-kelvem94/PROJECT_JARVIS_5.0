import os
import aiohttp
import json
import psutil
import asyncio
from loguru import logger

class EngineerBrain:
    """
    O 'Núcleo de Raciocínio Engenheiro' do JARVIS.
    100% OFFLINE - Otimizado para hardware de alta performance com limite de RAM (Book2 360).
    Inclui 'Modo Antigravidade' para evitar travamentos do sistema.
    """
    
    def __init__(self, model=None):
        self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
        self.model = model or os.getenv("LM_STUDIO_MODEL", "llama-3.2-3b-instruct")
        self._cached_model = None
        self._last_model_check = 0

    async def get_active_lmstudio_model(self) -> str:
        """Busca automaticamente o modelo ativo no LM Studio Local com cache de 30s."""
        import time
        now = time.time()
        if self._cached_model and (now - self._last_model_check < 30):
            return self._cached_model

        url = self.lm_studio_url.replace("/chat/completions", "/models")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        if models:
                            active = models[0].get("id")
                            logger.info(f"🧠 Cérebro detectado no LM Studio: {active}")
                            self._cached_model = active
                            self._last_model_check = now
                            return active
        except Exception:
            logger.warning("⚠️ LM Studio não detectado ou porta 1234 fechada.")
        
        self._cached_model = self.model
        self._last_model_check = now
        return self.model

    async def _get_safety_params(self):
        """Monitora o hardware e retorna parâmetros para máxima inteligência vs estabilidade."""
        ram_percent = psutil.virtual_memory().percent
        
        # Em carga extrema, reduzimos a janela de contexto para proteger a estabilidade,
        # mas mantemos a temperatura baixa para garantir que ele continue 'inteligente' e técnico.
        if ram_percent > 90:
            logger.warning(f"🚀 ALTA CARGA DETECTADA: RAM {ram_percent}%. Priorizando Contexto Crítico.")
            return {
                "max_tokens": 1024,
                "temperature": 0.1,
                "safety_context_limit": 3500, # Reduzido para não travar
                "timeout": 300
            }
        
        return {
            "max_tokens": 4096, # Máximo para raciocínios longos
            "temperature": 0.2,
            "safety_context_limit": 8000,
            "timeout": 300 # 5 Minutos de teto seguro
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
        
        # Obtém o prompt sistema e formata o conteúdo do usuário com base no modelo
        system_prompt = persona.get_system_prompt(active_model)
        
        # Injeção Anti-Alucinação Reforçada
        system_prompt += (
            "\n[DIRETIVA DE FIDELIDADE]: Se a informação não estiver na 'Memória Ativa', "
            "você deve informar que não possui esse dado localmente. "
            "Você tem permissão para sugerir o uso de 'browser_navigate' para buscar o fato na internet caso necessário."
        )

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
            "stream": stream
        }

        try:
            # 1. TENTA LM STUDIO LOCAL (Prioridade 1 - Offline First)
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.lm_studio_url, 
                    json=payload, 
                    timeout=aiohttp.ClientTimeout(total=5) # Timeout curto para falhar rápido e ir pro fallback
                ) as response:
                    if response.status == 200:
                        if stream:
                            async for line in response.content:
                                if line:
                                    try:
                                        line_str = line.decode('utf-8', errors='ignore').strip()
                                        if line_str.startswith("data: "):
                                            data_content = line_str[6:].strip()
                                            if data_content == "[DONE]": break
                                            chunk = json.loads(data_content)
                                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                                content = chunk['choices'][0]['delta'].get('content', '')
                                                if content: yield content
                                    except: continue
                            return # Sucesso local finaliza aqui
                        else:
                            data = await response.json()
                            yield data['choices'][0]['message']['content']
                            return

        except Exception as e:
            logger.warning(f"⚠️ LM Studio Local Offline: {e}. Tentando Gemini...")

        # 2. TENTA GEMINI (Prioridade 2)
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
        if not gemini_key or gemini_key.startswith("AIza"): # Bloqueia se for a chave velha
            logger.warning(f"❌ Gemini Key inválida ou antiga detectada: {gemini_key[:4]}...")
        else:
            try:
                logger.info(f"☁️ Chamando API Gemini 1.5 Flash (Key: {gemini_key[:4]}...{gemini_key[-4:]})")
                # Endpoint v1beta para suporte total a novos modelos e chaves AQ.
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                
                # Formato de payload exato para Gemini v1beta
                contents = []
                for m in messages:
                    # O Gemini Pro não aceita o role 'system' dentro de contents, deve ser 'user' ou 'model'
                    role = "user" if m["role"] in ["user", "system"] else "model"
                    contents.append({"role": role, "parts": [{"text": m["content"]}]})

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json={"contents": contents}, timeout=12) as response:
                        if response.status == 200:
                            data = await response.json()
                            if 'candidates' in data and len(data['candidates']) > 0:
                                text = data['candidates'][0]['content']['parts'][0]['text']
                                if text:
                                    logger.success("✅ Resposta recebida via Gemini Cloud")
                                    yield " [Modo Cloud] " + text
                                    return
                        else:
                            error_body = await response.text()
                            logger.error(f"❌ Gemini erro {response.status}: {error_body}")
            except Exception as e:
                logger.error(f"❌ Falha crítica no fallback Gemini: {e}")

        # 3. TENTA OPENROUTER (Prioridade 3)
        or_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not or_key:
            logger.warning("❌ OpenRouter API Key não encontrada no ambiente.")
        else:
            try:
                logger.info(f"☁️ Chamando API OpenRouter (Key: {or_key[:4]}...{or_key[-4:]})...")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {or_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "google/gemini-flash-1.5",
                            "messages": messages
                        },
                        timeout=15
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            text = data['choices'][0]['message']['content']
                            if text:
                                logger.success("✅ Resposta recebida via OpenRouter")
                                yield " [OpenRouter] " + text
                                return
                        else:
                            error_body = await response.text()
                            logger.error(f"❌ OpenRouter erro {response.status}: {error_body}")
            except Exception as e:
                 logger.error(f"❌ Falha crítica no OpenRouter: {e}")

        yield "Sistemas offline. Verifique suas Chaves de API no arquivo .env ou a conexão com a internet."

    async def reason_local(self, prompt: str, context: str = "", model: str = None):
        """Versão simplificada para chamadas rápidas locais."""
        if model: self.model = model
        return await self.reason(prompt, context=context)

# Singleton para uso no sistema
brain = EngineerBrain()
