from loguru import logger

class PersonaManager:
    """
    Gerencia a identidade e o comportamento do JARVIS 5.0.
    Otimizado para o novo cérebro WILL-JARVIS (Qwen 1.5B Fine-tuned).
    """

    def __init__(self):
        self.name = "WILL-JARVIS"
        self.version = "5.0-Offline"
        
    def get_context(self, memories, kb_context):
        context_str = ""
        if memories:
            context_str += "[MEMÓRIA LOCAL (FATOS RECENTES)]:\n"
            context_str += "\n".join([f"- {m}" for m in memories])
            
        if kb_context:
            context_str += "\n\n[CONHECIMENTO GLOBAL (OBSIDIAN)]:\n" + kb_context
            
        return context_str if context_str else "Nenhum contexto relevante encontrado."

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
                "Você é o WILL-JARVIS. Abaixo está uma instrução e um contexto de sua memória. "
                "Importante: Use a memória APENAS se for relevante para a instrução. "
                "Se a instrução for simples/conversa fiada, ignore os dados técnicos da memória.\n\n"
                "### Instrução:\n{instruction}\n\n"
                "### Memória Ativa (Local + Obsidian):\n{context}\n\n"
                "### Resposta:\n"
            ).replace("{instruction}", instruction).replace("{context}", context if context else "Vazia")
        
        # Padrão ChatML / Genérico
        return (
            "CONTEXTO DE MEMÓRIA (SÓ USE SE NECESSÁRIO):\n"
            f"{context}\n\n"
            "COMANDO DO CHEFE:\n"
            f"{instruction}"
        )

persona = PersonaManager()
