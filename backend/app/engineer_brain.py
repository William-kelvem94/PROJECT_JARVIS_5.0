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

    async def reason(self, prompt: str, context: str = "") -> str:
        """Processa a tarefa e retorna a resposta completa (Não-Streaming)."""
        logger.info(f"JARVIS [Núcleo High-Load] Analisando (Sync): {prompt[:50]}...")
        
        async for chunk in self.reason_stream(prompt, context, stream=False):
            return chunk # O primeiro chunk no modo stream=False é a resposta completa
        return "Erro interno no cérebro."

    async def reason_stream(self, prompt: str, context: str = "", stream: bool = True):
        """Processa a tarefa gerando chunks (Streaming)."""
        from .persona import persona
        active_model = await self.get_active_lmstudio_model()
        # Obtém o prompt sistema e formata o conteúdo do usuário com base no modelo
        system_prompt = persona.get_system_prompt(active_model)
        user_content = persona.format_prompt(prompt, context, active_model)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content[:7000]} # Limite de contexto para segurança de RAM
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
                async with session.post(self.lm_studio_url, json=payload, timeout=120) as response:
                    if response.status != 200:
                        yield f"Erro técnico ({response.status}) no servidor local."
                        return

                    if stream:
                        async for line in response.content:
                            if line:
                                line_str = line.decode('utf-8').strip()
                                if line_str.startswith("data: "):
                                    data_content = line_str[6:]
                                    if data_content == "[DONE]": break
                                    try:
                                        chunk = json.loads(data_content)
                                        content = chunk['choices'][0]['delta'].get('content', '')
                                        if content: yield content
                                    except: continue
                    else:
                        data = await response.json()
                        yield data['choices'][0]['message']['content']
                        
        except Exception as e:
            logger.error(f"Erro no Cérebro Local: {e}")
            yield "O processamento falhou. Verifique se o LM Studio está aberto."

    async def reason_local(self, prompt: str, context: str = "", model: str = "llama3"):
        return None

# Singleton para uso no sistema
brain = EngineerBrain()
