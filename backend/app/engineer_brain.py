import os
import aiohttp
import json
from loguru import logger

class EngineerBrain:
    """
    O 'Núcleo de Raciocínio Engenheiro' do JARVIS.
    Usa OpenRouter para tarefas complexas de codificação e arquitetura.
    """
    
    def __init__(self, model="google/gemini-2.0-flash-exp:free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model

    async def reason(self, prompt: str, context: str = ""):
        """
        Envia uma tarefa complexa para o modelo sênior via OpenRouter.
        """
        if not self.api_key:
            logger.error("OPENROUTER_API_KEY não encontrada no .env")
            return "Erro: Chave do OpenRouter não configurada."

        logger.info(f"JARVIS consultando o Cérebro Engenheiro ({self.model})...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/William-kelvem94/PROJECT_JARVIS_5.0",
            "X-Title": "JARVIS 5.0",
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o núcleo de engenharia do JARVIS 5.0. Seu objetivo é resolver problemas complexos "
                    "de software, arquitetura e automação. Forneça respostas técnicas precisas, "
                    "código pronto para produção e diagnósticos detalhados. "
                    "Seja direto, eficiente e mantenha o tom profissional e sênior."
                )
            },
            {
                "role": "user",
                "content": f"Contexto do Projeto:\n{context}\n\nTarefa:\n{prompt}"
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4000
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        reply = data['choices'][0]['message']['content']
                        logger.success("Cérebro Engenheiro respondeu com sucesso.")
                        return reply
                    else:
                        error_text = await response.text()
                        logger.error(f"Erro no OpenRouter: {response.status} - {error_text}")
                        return f"Erro na consulta ao núcleo de engenharia: {response.status}"
        except Exception as e:
            logger.error(f"Falha na conexão com OpenRouter: {str(e)}")
            return f"Falha técnica ao consultar o cérebro engenheiro: {str(e)}"

# Singleton para uso no sistema
brain = EngineerBrain()
