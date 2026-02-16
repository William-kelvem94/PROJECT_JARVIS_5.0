import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("JARVIS-DISTILLER")


class KnowledgeDistiller:
    """
    Analisa interaÃ§Ãµes passadas para extrair 'Golden Commands'.
    Golden Commands sÃ£o sequÃªncias de aÃ§Ãµes que levaram ao sucesso
    e podem ser reutilizadas como contexto de alta prioridade.
    """

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.gold_memories_path = self.data_dir / "memories" / "gold_commands.json"
        self.log_path = self.data_dir / "logs" / "agent_interactions.jsonl"

        # Garantir diretÃ³rios
        self.gold_memories_path.parent.mkdir(parents=True, exist_ok=True)

        self._load_gold_commands()

    def _load_gold_commands(self):
        """Carrega comandos de ouro existentes"""
        if self.gold_memories_path.exists():
            try:
                with open(self.gold_memories_path, "r", encoding="utf-8") as f:
                    self.gold_commands = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar Golden Commands: {e}")
                self.gold_commands = {}
        else:
            self.gold_commands = {}

    def distill_interaction(
        self,
        user_command: str,
        thought: str,
        actions: List[Dict[str, Any]],
        success: bool = True,
    ):
        """
        Processa uma interaÃ§Ã£o recente. Se for bem-sucedida, armazena como potencial
        exemplo de alta qualidade para o RAG.
        """
        if not success or not actions:
            return

        # Normalizar comando para identificar padrÃµes
        cmd_key = user_command.lower().strip()

        # Armazenar a melhor versÃ£o do raciocÃ­nio e aÃ§Ãµes para este comando
        interaction_data = {
            "command": user_command,
            "thought": thought,
            "actions": actions,
            "timestamp": datetime.now().isoformat(),
            "usage_count": self.gold_commands.get(cmd_key, {}).get("usage_count", 0)
            + 1,
        }

        self.gold_commands[cmd_key] = interaction_data
        self._save_gold_commands()

        # Registrar no log de destilaÃ§Ã£o
        logger.info(f"âœ¨ Conhecimento destilado para: '{user_command}'")

    def _save_gold_commands(self):
        """Salva a base de comandos de ouro"""
        try:
            with open(self.gold_memories_path, "w", encoding="utf-8") as f:
                json.dump(self.gold_commands, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar Golden Commands: {e}")

    def get_relevant_examples(self, current_command: str, limit: int = 2) -> str:
        """
        Busca exemplos 'Golden' que combinam com o comando atual para injetar no prompt.
        """
        import difflib

        matches = difflib.get_close_matches(
            current_command.lower(), self.gold_commands.keys(), n=limit, cutoff=0.6
        )

        if not matches:
            return ""

        context_blocks = ["### EXEMPLOS DE SUCESSO ANTERIORES (GOLDEN COMMANDS):"]
        for match in matches:
            cmd_data = self.gold_commands[match]
            block = f"Comando: {cmd_data['command']}\n"
            block += f"RaciocÃ­nio: {cmd_data['thought']}\n"
            block += f"AÃ§Ãµes: {json.dumps(cmd_data['actions'], ensure_ascii=False)}"
            context_blocks.append(block)

        return "\n\n".join(context_blocks) + "\n"


# InstÃ¢ncia global
from src.utils.config import config

knowledge_distiller = KnowledgeDistiller(Path(config.PROJECT_ROOT) / "data")
