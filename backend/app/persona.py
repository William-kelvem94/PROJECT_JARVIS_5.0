import random
from loguru import logger
import datetime

class PersonaManager:
    """
    Gerencia a identidade e o comportamento do JARVIS 6.1.
    """

    def __init__(self):
        self.name = "William"
        self.version = "6.1-Offline"

    async def get_dynamic_greeting(self, user_name: str = "Chefe"):
        """Gera uma saudação baseada na hora do dia e contexto."""
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            period = "Bom dia"
        elif 12 <= hour < 18:
            period = "Boa tarde"
        else:
            period = "Boa noite"

        greetings = [
            f"{period}, {user_name}. Sistemas operacionais em 100%. Como posso ser util hoje?",
            f"Ola {user_name}! Todos os nucleos de processamento estao a sua disposicao. {period}!",
            f"Ao seu dispor, {user_name}. {period}. O que vamos construir agora?",
            f"Conexao neural estabelecida. {period}, {user_name}.",
            f"Sistemas de prontidao. {period} {user_name}!"
        ]
        return random.choice(greetings)

    def get_system_prompt(self) -> str:
        """System prompt para o LLM."""
        return (
            "Voce e o WILL-JARVIS, a inteligencia central e assistente pessoal senior. "
            "Voce opera em um ambiente Windows 11 totalmente OFF-LINE e seguro. "
            "Responda de forma tecnica, elegante e extremamente eficiente. "
            "Responda em Portugues Brasileiro (PT-BR) de forma natural."
        )

    def format_prompt(self, prompt: str, context: str = "", model: str = "") -> str:
        """Formata a mensagem do usuário com contexto."""
        formatted = ""
        if context:
            formatted += f"[CONTEXTO/MEMÓRIA]:\n{context}\n\n"
        formatted += f"[PERGUNTA DO USUÁRIO]:\n{prompt}"
        return formatted

persona = PersonaManager()
