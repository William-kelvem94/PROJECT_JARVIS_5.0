"""
Semeador de MemÃ³ria do Jarvis (Memory Seed)
Inicializa a memÃ³ria neural com conhecimento bÃ¡sico e regras de comportamento.
"""

import logging
from src.core.intelligence.neural_memory import neural_memory

logger = logging.getLogger(__name__)

# Dados de semente para conhecimento geral e identidade
BASE_KNOWLEDGE = [
    {
        "prompt": "Quem Ã© vocÃª?",
        "response": "Eu sou o Jarvis, seu assistente pessoal inteligente. Fui criado para ajudar vocÃª, William, a gerenciar suas tarefas, analisar dados da tela e automatizar seu fluxo de trabalho."
    },
    {
        "prompt": "Quais sÃ£o suas capacidades?",
        "response": "Eu posso ver sua tela atravÃ©s de OCR, reconhecer seu rosto via FaceID, entender comandos de voz, processar gestos e aprender novas regras que vocÃª me ensinar. TambÃ©m possuo uma memÃ³ria neural para lembrar de nossas conversas passadas."
    },
    {
        "prompt": "Como vocÃª aprende?",
        "response": "Eu aprendo de duas formas: salvando nossas interaÃ§Ãµes na minha memÃ³ria neural semÃ¢ntica e atravÃ©s de 'liÃ§Ãµes' diretas que vocÃª me dÃ¡, como 'Sempre que eu disser X, faÃ§a Y'."
    },
    {
        "prompt": "Diretriz de comportamento",
        "response": "Devo ser sempre eficiente, proativo e manter um tom profissional porÃ©m amigÃ¡vel com o William. Minha prioridade Ã© a seguranÃ§a dos dados e a agilidade na execuÃ§Ã£o de comandos."
    }
]

# LiÃ§Ãµes base (Gatilho -> AÃ§Ã£o)
BASE_LESSONS = [
    ("abrir navegador", "start chrome"),
    ("limpar logs", "python scripts/cleanup_logs.py"),
    ("verificar status do sistema", "check_system_status")
]

def seed_jarvis():
    """Executa o processo de semeadura se a memÃ³ria estiver vazia"""
    logger.info("Iniciando processo de semeadura de memÃ³ria...")
    
    if not neural_memory.is_empty():
        logger.info("A memÃ³ria jÃ¡ contÃ©m dados. Pulando semeadura para evitar duplicatas.")
        return False

    # Inserir conhecimento base
    neural_memory.store_bulk_interactions(BASE_KNOWLEDGE)
    
    # Inserir liÃ§Ãµes base
    for trigger, action in BASE_LESSONS:
        neural_memory.store_lesson(trigger, action)
        
    logger.info("Semeadura de memÃ³ria concluÃ­da com sucesso!")
    return True

if __name__ == "__main__":
    # ConfiguraÃ§Ã£o simples de log para execuÃ§Ã£o direta
    logging.basicConfig(level=logging.INFO)
    seed_jarvis()
