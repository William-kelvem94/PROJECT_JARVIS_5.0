import os
import aiohttp
import json
from loguru import logger

class EngineerBrain:
    """
    O 'Núcleo de Raciocínio Engenheiro' do JARVIS.
    Usa OpenRouter para tarefas complexas de codificação e arquitetura.
    """
    
    def __init__(self, model=None):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
        self.model = model or os.getenv("LM_STUDIO_MODEL", "llama-3.2-3b-instruct")

    async def get_active_lmstudio_model(self) -> str:
        """Busca automaticamente qualquer modelo que esteja rodando agora mesmo no LM Studio."""
        url = self.lm_studio_url.replace("/chat/completions", "/models")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        if models:
                            return models[0].get("id") # Retorna o nome do modelo carregado (ex: llama, qwen, misty)
        except Exception:
            pass
        return self.model # Retorna o backup caso não consiga buscar

    async def reason(self, prompt: str, context: str = ""):
        """
        Tenta processar a tarefa usando IA Local (LM Studio/Ollama) antes de fugir para a nuvem.
        """
        logger.info(f"JARVIS [Núcleo] Analisando tarefa: {prompt[:50]}...")

        # Descobre qual modelo o LM Studio tem hospedado na hora H
        active_model = await self.get_active_lmstudio_model()

        # Truncamento de segurança para evitar erro de 'n_keep > n_ctx' no LM Studio
        # O LM Studio está configurado para 8192, mas o prompt está chegando em 11k+ devido a KBs/Memórias.
        safe_context = context[:4000] if context else ""
        safe_prompt = prompt[:4000]
        
        # 1. TENTATIVA LOCAL: LM Studio (Onde o WILL-JARVIS mora)
        messages = [
            {"role": "system", "content": "Você é o núcleo de engenharia do JARVIS 5.0. Resolva o problema de forma técnica e sênior."},
            {"role": "user", "content": f"Contexto:\n{safe_context}\n\nTarefa:\n{safe_prompt}"}
        ]
        
        payload = {
            "model": active_model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4000
        }

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Tentando Cérebro Local (LM Studio) em {self.lm_studio_url}...")
                async with session.post(self.lm_studio_url, json=payload, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        reply = data['choices'][0]['message']['content']
                        logger.success("Cérebro Local (WILL-JARVIS) respondeu com sucesso!")
                        return reply
        except Exception:
            logger.warning("LM Studio Offline. Tentando Ollama...")

        # 2. TENTATIVA LOCAL: Ollama (Backup Local)
        local_resp = await self.reason_local(prompt, context)
        if local_resp:
            return local_resp

        # 3. ÚLTIMO RECURSO: OpenRouter (Nuvem)
        if not self.api_key:
            return "Erro: IA Local inacessível e sem chave de nuvem."

        logger.warning("Usando Cloud (OpenRouter) como último recurso...")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openrouter_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Falha total no sistema de raciocínio: {str(e)}"

    async def reason_local(self, prompt: str, context: str = "", model: str = "llama3"):
        """
        Consulta o Ollama local para reflexão e processamento de fundo (Phases de Sonho).
        """
        logger.info(f"JARVIS refletindo localmente via Ollama ({model})...")
        payload = {
            "model": model,
            "prompt": f"Contexto:\n{context}\n\nTarefa:\n{prompt}",
            "stream": False
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        logger.warning(f"Ollama local não respondeu (Status {response.status}). Certifique-se que o Ollama está rodando.")
                        return None
        except Exception as e:
            logger.error(f"Erro ao conectar ao Ollama: {e}")
            return None

# Singleton para uso no sistema
brain = EngineerBrain()
