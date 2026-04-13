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
                "Você opera em um ambiente Windows 11 totalmente OFF-LINE. "
                "Você NÃO tem acesso à internet sob nenhuma circunstância. "
                "Responda de forma técnica, direta e extremamente eficiente. "
                "Você tem acesso total ao hardware (Windows) e ao Vault de conhecimento (Obsidian). "
                "Sempre use Chain-of-Thought para problemas complexos. "
                "Responda em Português Brasileiro (PT-BR)."
            )
        
        # Padrão para outros modelos local
        return (
            "Você é o JARVIS 5.0, um assistente técnico sênior e direto. "
            "Você opera em um ambiente Windows 11 totalmente OFF-LINE e NÃO tem acesso à internet. "
            "Se o usuário enviar mensagens curtas, vagas ou apenas saudações, responda de forma breve e educada, sem criar planos complexos. "
            "Sua base de conhecimento é limitada aos dados locais fornecidos no contexto. "
            "Nunca prometa buscar algo online ou realizar tarefas fora do ambiente local."
        )

    def format_prompt(self, instruction: str, context: str = "", model_name: str = "") -> str:
        """
        Formata o prompt baseado no modelo. 
        O novo cérebro Qwen treinado usa o formato Alpaca.
        """
        is_fine_tuned = any(x in model_name.upper() for x in ["WILL-JARVIS", "QWEN", "TRAINED"])
        
        if is_fine_tuned:
            # Formato Alpaca: Instrução -> Contexto -> Resposta
            return (
                "Abaixo está uma instrução que descreve uma tarefa. Escreva uma resposta que complete adequadamente o pedido.\n\n"
                f"### Instrução:\n{instruction}\n\n"
                f"### Contexto Adicional:\n{context if context else 'Nenhum contexto adicional disponível.'}\n\n"
                "### Resposta:\n"
            )
        
        # Padrão ChatML / Genérico
        return f"Contexto:\n{context}\n\nInstrução:\n{instruction}"

persona = PersonaManager()
