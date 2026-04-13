import os
import aiohttp
import json
from loguru import logger

class EngineerBrain:
    """
    O 'Núcleo de Raciocínio Engenheiro' do JARVIS.
    100% OFFLINE - Otimizado para hardware de alta performance com limite de RAM (Book2 360).
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
        """Processa a tarefa usando o Cérebro Local, com timeout estendido para troca de memória (swap)."""
        logger.info(f"JARVIS [Núcleo High-Load] Analisando: {prompt[:50]}...")

        active_model = await self.get_active_lmstudio_model()

        # Truncamento cirúrgico para preservar os últimos MBs de RAM física
        safe_context = context[:3500] if context else ""
        safe_prompt = prompt[:3500]
        
        messages = [
            {"role": "system", "content": "Você é o JARVIS 5.0. Responda de forma técnica, direta e sênior. O sistema está em modo 100% Offline."},
            {"role": "user", "content": f"Contexto:\n{safe_context}\n\nTarefa:\n{safe_prompt}"}
        ]
        
        payload = {
            "model": active_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2048
        }

        try:
            # Timeout estendido para 120s para compensar lentidão caso o Windows use Swap (SSD) por falta de RAM
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Processando localmente (Timeout: 120s) via {self.lm_studio_url}...")
                async with session.post(self.lm_studio_url, json=payload, timeout=120) as response:
                    if response.status == 200:
                        data = await response.json()
                        reply = data['choices'][0]['message']['content']
                        logger.success("Cérebro Local respondeu (Processamento High-Load concluído).")
                        return reply
                    else:
                        return f"Erro técnico: O servidor local retornou status {response.status}."
        except Exception as e:
            logger.error(f"Erro no Cérebro Local (Timeout ou RAM cheia): {e}")
            return "Aviso: O processamento demorou demais ou a memória RAM está saturada. Tente fechar alguns programas e tente novamente."

    async def reason_local(self, prompt: str, context: str = "", model: str = "llama3"):
        return None

# Singleton para uso no sistema
brain = EngineerBrain()
