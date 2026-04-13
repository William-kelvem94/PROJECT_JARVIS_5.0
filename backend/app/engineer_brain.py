import os
import aiohttp
import json
from loguru import logger

class EngineerBrain:
    """
    O 'Núcleo de Raciocínio Engenheiro' do JARVIS.
    100% OFFLINE - Opera exclusivamente via LM Studio Local.
    """
    
    def __init__(self, model=None):
        self.lm_studio_url = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
        self.model = model or os.getenv("LM_STUDIO_MODEL", "llama-3.2-3b-instruct")

    async def get_active_lmstudio_model(self) -> str:
        """Busca automaticamente o modelo ativo no LM Studio Local."""
        url = self.lm_studio_url.replace("/chat/completions", "/models")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        if models:
                            return models[0].get("id")
        except Exception:
            pass
        return self.model

    async def reason(self, prompt: str, context: str = ""):
        """Processa a tarefa usando estritamente o Cérebro Local (LM Studio)."""
        logger.info(f"JARVIS [Núcleo Local] Analisando: {prompt[:50]}...")

        active_model = await self.get_active_lmstudio_model()

        # Truncamento rigoroso para i3/1050Ti (Preserva memória de vídeo)
        safe_context = context[:3500] if context else ""
        safe_prompt = prompt[:3500]
        
        messages = [
            {"role": "system", "content": "Você é o JARVIS 5.0, um sistema 100% OFF-LINE. Responda de forma técnica e objetiva."},
            {"role": "user", "content": f"Contexto:\n{safe_context}\n\nTarefa:\n{safe_prompt}"}
        ]
        
        payload = {
            "model": active_model,
            "messages": messages,
            "temperature": 0.2, # Mais focado e menos aleatório para hardware local
            "max_tokens": 2048 # Limite seguro para evitar lentidão extrema
        }

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Processando localmente via {self.lm_studio_url}...")
                async with session.post(self.lm_studio_url, json=payload, timeout=45) as response:
                    if response.status == 200:
                        data = await response.json()
                        reply = data['choices'][0]['message']['content']
                        logger.success("Cérebro Local respondeu offline.")
                        return reply
                    else:
                        return "Erro técnico: O servidor local (LM Studio) não respondeu corretamente."
        except Exception as e:
            logger.error(f"Erro no Cérebro Local: {e}")
            return "Aviso: Cérebro Offline. Certifique-se de que o LM Studio está rodando e o modelo carregado."

    async def reason_local(self, prompt: str, context: str = "", model: str = "llama3"):
        return None

# Singleton para uso no sistema
brain = EngineerBrain()
