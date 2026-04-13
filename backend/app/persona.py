from loguru import logger

class PersonaManager:
    """
    Gerencia a identidade e o comportamento do JARVIS 5.0.
    Otimizado para o novo cérebro WILL-JARVIS (Qwen 1.5B Fine-tuned).
    """

    def __init__(self):
        self.name = "WILL-JARVIS"
        self.version = "5.0-Offline"
        
    def get_system_prompt(self, model_name: str = "") -> str:
        """
        Retorna o system prompt ideal baseado no modelo ativo.
        Se detectar o modelo WILL-JARVIS, usa o prompt técnico especializado.
        """
        is_will_jarvis = "WILL-JARVIS" in model_name.upper()
        
        if is_will_jarvis:
            logger.info("🎭 Persona 'WILL-JARVIS' ativada (Modo de Alta Fidelidade).")
            return (
                "Você é o WILL-JARVIS, a inteligência central e assistente pessoal sênior. "
                "Responda de forma técnica, direta e extremamente eficiente. "
                "Você tem acesso total ao hardware (Windows) e ao Vault de conhecimento (Obsidian). "
                "Sempre use Chain-of-Thought para problemas complexos. "
                "Responda em Português Brasileiro (PT-BR)."
            )
        
        # Padrão para outros modelos local
        return (
            "Você é o JARVIS 5.0, um assistente técnico sênior e direto. "
            "Resolva as tarefas de forma pragmática e 100% offline."
        )

    def format_prompt(self, instruction: str, context: str = "", model_name: str = "") -> str:
        """
        Formata opcionalmente o prompt para modelos específicos que não usam ChatML padrão.
        (Útil para garantir que o Fine-Tuning Alpaca do novo cérebro seja respeitado).
        """
        if "WILL-JARVIS" in model_name.upper():
            # Formato Alpaca usado no script de treino 02_fine_tune_student.py
            return (
                "Abaixo está uma instrução que descreve uma tarefa. Escreva uma resposta que complete adequadamente o pedido.\n\n"
                f"### Instrução:\n{instruction}\n\nContexto:\n{context}\n\n### Resposta:\n"
            )
        return instruction

persona = PersonaManager()
