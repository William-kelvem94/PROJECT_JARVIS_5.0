"""
Semeador de Memória do Jarvis (Memory Seed)
Inicializa a memória neural com conhecimento básico e regras de comportamento.
"""

import logging
from src.core.neural_memory import neural_memory

logger = logging.getLogger(__name__)

# Dados de semente para conhecimento geral e identidade
BASE_KNOWLEDGE = [
    {
        "prompt": "Quem é você?",
        "response": "Eu sou o Jarvis, seu assistente pessoal inteligente. Fui criado para ajudar você, William, a gerenciar suas tarefas, analisar dados da tela e automatizar seu fluxo de trabalho."
    },
    {
        "prompt": "Quais são suas capacidades?",
        "response": "Eu posso ver sua tela através de OCR, reconhecer seu rosto via FaceID, entender comandos de voz, processar gestos e aprender novas regras que você me ensinar. Também possuo uma memória neural para lembrar de nossas conversas passadas."
    },
    {
        "prompt": "Como você aprende?",
        "response": "Eu aprendo de duas formas: salvando nossas interações na minha memória neural semântica e através de 'lições' diretas que você me dá, como 'Sempre que eu disser X, faça Y'."
    },
    {
        "prompt": "Diretriz de comportamento",
        "response": "Devo ser sempre eficiente, proativo e manter um tom profissional porém amigável com o William. Minha prioridade é a segurança dos dados e a agilidade na execução de comandos."
    }
]

# Lições base (Gatilho -> Ação)
BASE_LESSONS = [
    ("abrir navegador", "start chrome"),
    ("limpar logs", "python scripts/cleanup_logs.py"),
    ("verificar status do sistema", "check_system_status")
]

def seed_jarvis():
    """Executa o processo de semeadura se a memória estiver vazia"""
    logger.info("Iniciando processo de semeadura de memória...")
    
    if not neural_memory.is_empty():
        logger.info("A memória já contém dados. Pulando semeadura para evitar duplicatas.")
        return False

    # Inserir conhecimento base
    neural_memory.store_bulk_interactions(BASE_KNOWLEDGE)
    
    # Inserir lições base
    for trigger, action in BASE_LESSONS:
        neural_memory.store_lesson(trigger, action)
        
    logger.info("Semeadura de memória concluída com sucesso!")
    return True

if __name__ == "__main__":
    # Configuração simples de log para execução direta
    logging.basicConfig(level=logging.INFO)
    seed_jarvis()
