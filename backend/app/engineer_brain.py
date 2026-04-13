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

    async def reason(self, prompt: str, context: str = "", stream: bool = False):
        """Processa a tarefa usando o Cérebro Local. Suporta streaming para latência zero."""
        logger.info(f"JARVIS [Núcleo High-Load] Analisando (Stream={stream}): {prompt[:50]}...")

        from .persona import persona
        active_model = await self.get_active_lmstudio_model()
        system_prompt = persona.get_system_prompt(active_model)

        safe_context = context[:3500] if context else ""
        safe_prompt = prompt[:3500]
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Contexto:\n{safe_context}\n\nTarefa:\n{safe_prompt}"}
        ]
        
        payload = {
            "model": active_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2048,
            "stream": stream
        }

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Processando localmente via {self.lm_studio_url}...")
                async with session.post(self.lm_studio_url, json=payload, timeout=120) as response:
                    if response.status != 200:
                        error_msg = f"Erro técnico: O servidor local retornou status {response.status}."
                        if stream:
                            yield error_msg
                            return
                        return error_msg

                    if stream:
                        full_text = ""
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith("data: "):
                                    data_content = line_str[6:]
                                    if data_content == "[DONE]":
                                        break
                                    try:
                                        chunk = json.loads(data_content)
                                        content = chunk['choices'][0]['delta'].get('content', '')
                                        if content:
                                            full_text += content
                                            yield content
                                    except Exception:
                                        continue
                        logger.success("Cérebro Local concluiu streaming.")
                    else:
                        data = await response.json()
                        reply = data['choices'][0]['message']['content']
                        logger.success("Cérebro Local respondeu (Processamento High-Load concluído).")
                        return reply
        except Exception as e:
            logger.error(f"Erro no Cérebro Local: {e}")
            msg = "Aviso: O processamento falhou ou a memória RAM está saturada."
            if stream:
                yield msg
            else:
                return msg

    async def reason_local(self, prompt: str, context: str = "", model: str = "llama3"):
        return None

# Singleton para uso no sistema
brain = EngineerBrain()
