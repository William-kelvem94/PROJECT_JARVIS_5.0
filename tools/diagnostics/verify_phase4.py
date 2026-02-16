import logging
import sys
import os

# Adicionar root ao path
sys.path.append(os.getcwd())

from src.learning.knowledge_distiller import knowledge_distiller
from src.core.actions.advanced_action_controller import advanced_action_controller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY-PHASE4")


def test_knowledge_distiller():
    logger.info("Testing Knowledge Distiller...")
    user_cmd = "abra o notepad e escreva jarvis"
    thought = "Vou abrir o notepad e digitar o comando"
    actions = [
        {"action": "open_program", "program": "notepad"},
        {"action": "type_text", "text": "JARVIS 5.0"},
    ]

    knowledge_distiller.distill_interaction(user_cmd, thought, actions, success=True)

    # Test recall
    examples = knowledge_distiller.get_relevant_examples("notepad jarvis")
    if "JARVIS 5.0" in examples:
        logger.info("✅ Knowledge Distiller: Recall SUCCESS")
    else:
        logger.error("❌ Knowledge Distiller: Recall FAILED")


def test_window_management():
    logger.info("Testing Window Management (Dry Run)...")
    # Apenas verifica se o método existe e não quebra com parâmetros mock
    try:
        # Tenta focar a janela atual (deve funcionar se houver uma janela ativa)
        advanced_action_controller.window_manage(operation="focus")
        logger.info("✅ Window Management: Basic call SUCCESS")
    except Exception as e:
        logger.error(f"❌ Window Management: FAILED - {e}")


if __name__ == "__main__":
    test_knowledge_distiller()
    test_window_management()
    logger.info("Fase 4 Verification Complete.")
