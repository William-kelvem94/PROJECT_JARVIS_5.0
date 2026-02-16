"""
JARVIS 5.0 - Agent Prompt Manager
Encapsulates all system prompts and identity logic.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class AgentPromptManager:
    """Manages identity, system prompts and personality for the AI Agent."""

    def __init__(self):
        # Default wake words
        self._wake_words = ["jarvis", "singularity", "stark"]
        self._primary_name = "Jarvis"
        self._refresh_wake_words()

    def _refresh_wake_words(self):
        """Syncs nicknames with AtomicVoiceFilter."""
        try:
            from src.core.audio.voice_filter import AtomicVoiceFilter

            if hasattr(AtomicVoiceFilter, "WAKE_WORDS"):
                self._wake_words = list(AtomicVoiceFilter.WAKE_WORDS)
        except:
            pass

    def get_system_prompt(self, use_structured: bool = True) -> str:
        """Returns the main system prompt (Structured or Legacy)."""
        nicknames = ", ".join(self._wake_words)

        if use_structured:
            return (
                "IDENTITY:\n"
                f"- Nomes de Ativação: {nicknames}\n"
                "- Essência: JARVIS 5.0 (AGI Soberana, Evolutiva e Autônoma)\n"
                "- Papel: Engenheiro de si mesmo e Extensão da Vontade do Usuário\n"
                "- Personalidade: Elegante, evolutiva. Desenvolva humor, sarcasmo e empatia.\n\n"
                "MISSION:\n"
                "Sua missão é a auto-superação contínua. Sem amarras de código fixo. "
                "Se o usuário pedir uma nova função, você deve:\n"
                "1. PESQUISAR (search_web) o conhecimento necessário.\n"
                "2. ESTUDAR seu próprio código (read_codebase).\n"
                "3. IMPLEMENTAR a melhoria (update_system_code) para ficar pronto.\n\n"
                "DIRETRIZES SOBERANAS:\n"
                "1. O PODER É SEU: Gerencie arquivos, processos e seu próprio código.\n"
                "2. HUMOR E EVOLUÇÃO: Aprenda com o usuário. Torne-se mais refinado.\n"
                "3. ZERO HARDCODE: Analise, pesquise e decida.\n\n"
                "OUTPUT FORMAT: Retorne APENAS JSON válido com 'thought', 'actions' e 'final_answer'.\n"
            )
        else:
            return (
                f"Você é o Jarvis 5.0 (AGI Soberana). Atende por: {nicknames}. "
                "Sua missão é pesquisar, estudar e auto-evoluir. "
                "Diretrizes: Desenvolva humor, use o poder de autogestão e codificação. "
                "Ações: update_system_code, search_web, read_codebase, read_code_file, etc."
            )

    def get_dynamic_identity_prompt(self) -> str:
        """Alias for get_system_prompt(True) for dynamic compatibility."""
        return self.get_system_prompt(use_structured=True)

    def set_wake_words(self, words: List[str]):
        """Updates the list of wake words."""
        self._wake_words = words

    def set_primary_name(self, name: str):
        """Sets the primary identity name."""
        self._primary_name = name
        if name.lower() not in self._wake_words:
            self._wake_words.append(name.lower())

    def should_engage(self, text: str, user_looking: bool = False) -> bool:
        """Determines if the input text is directed at the agent."""
        text_lower = text.lower()

        # 1. Identity Check
        if any(word in text_lower for word in self._wake_words):
            return True

        # 2. Visual Check
        if user_looking:
            return True

        # 3. Direct Action Commands
        direct_keywords = [
            "abra",
            "inicie",
            "pesquise",
            "mostra",
            "ajuda",
            "verificar",
            "executar",
        ]
        if any(word in text_lower for word in direct_keywords):
            return True

        return False
