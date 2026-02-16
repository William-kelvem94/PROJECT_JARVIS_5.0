import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class EvolutionEngine:
    """
    O CÃ©rebro de AutodiagnÃ³stico e EvoluÃ§Ã£o do JARVIS.
    Monitora a saÃºde de todos os mÃ³dulos e aprende com falhas de execuÃ§Ã£o.
    """

    def __init__(self):
        from src.utils.config import config
        self.data_dir = config.SYSTEM_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pulse_file = self.data_dir / "SYSTEM_PULSE.md"
        
        # Estado atual dos mÃ³dulos
        self.module_health = {
            "Vision": {"status": "UNKNOWN", "last_check": None, "error": None},
            "Audio": {"status": "UNKNOWN", "last_check": None, "error": None},
            "Intelligence": {"status": "UNKNOWN", "last_check": None, "error": None},
            "Actions": {"status": "UNKNOWN", "last_check": None, "error": None},
            "Infrastructure": {"status": "UNKNOWN", "last_check": None, "error": None}
        }
        
        self.failure_patterns = []
        self._load_failures()

    def report_status(self, module: str, status: str, error: Optional[str] = None):
        """Atualiza o status de um mÃ³dulo especÃ­fico"""
        if module in self.module_health:
            self.module_health[module] = {
                "status": status,
                "last_check": datetime.now().isoformat(),
                "error": error
            }
            logger.debug(f"EvolutionEngine: {module} reportou status {status}")

    def log_failure(self, task: str, error: str, provider: str):
        """Registra uma falha tÃ©cnica para anÃ¡lise de evoluÃ§Ã£o"""
        failure = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "error": error,
            "provider": provider
        }
        self.failure_patterns.append(failure)
        self._save_failures()
        
        # Trigger Pulse Update
        self.generate_pulse_report()

    def log_evolution(self, file_path: str, change_description: str, rationale: str):
        """
        Records an autonomous system evolution (code change).
        Saves to data/EVOLUTION.log for human auditing.
        """
        from src.utils.config import config
        log_file = config.LOGS_DIR / "EVOLUTION.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = (
            f"[{timestamp}] EVOLUTION EVENT\n"
            f"Target: {file_path}\n"
            f"Action: {change_description}\n"
            f"Rationale: {rationale}\n"
            f"{'-'*50}\n"
        )
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            logger.info(f"ðŸ§¬ Evolution logged for {file_path}")
        except Exception as e:
            logger.error(f"Failed to log evolution: {e}")

    def _load_failures(self):
        file = self.data_dir / "failure_history.json"
        if file.exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.failure_patterns = json.load(f)
            except Exception:
                self.failure_patterns = []

    def _save_failures(self):
        file = self.data_dir / "failure_history.json"
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.failure_patterns[-100:], f, indent=2)

    def generate_pulse_report(self):
        """Gera o relatÃ³rio SYSTEM_PULSE.md organizado e limpo"""
        try:
            pulse_content = [
                "# ðŸ«€ JARVIS SYSTEM PULSE\n",
                f"**Ãšltima AtualizaÃ§Ã£o:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n",
                "## ðŸ› ï¸ Status dos MÃ³dulos\n",
                "| MÃ³dulo | Estado | Detalhes |",
                "| :--- | :--- | :--- |"
            ]
            
            for mod, data in self.module_health.items():
                icon = "ðŸŸ¢" if data['status'] == "OK" else "ðŸ”´" if data['status'] == "FAIL" else "ðŸŸ¡"
                pulse_content.append(f"| {mod} | {icon} {data['status']} | {data['error'] or 'Operacional'} |")
            
            pulse_content.append("\n## ðŸ§  HistÃ³rico de Aprendizado (Auto-CorreÃ§Ã£o)\n")
            if not self.failure_patterns:
                pulse_content.append("*Nenhuma falha crÃ­tica detectada recentemente. Sistema estÃ¡vel.*")
            else:
                for fail in self.failure_patterns[-5:]:
                    pulse_content.append(f"- **{fail['timestamp'][:16]}**: Falha no `{fail['provider']}` durante `{fail['task']}`. Erro: `{fail['error']}`")
            
            pulse_content.append("\n## ðŸ“¡ SugestÃµes de Melhoria Manual\n")
            # Adicionar sugestÃ£o baseada em padrÃµes de erro
            if len(self.failure_patterns) > 5:
                pulse_content.append("- [ ] Detectamos instabilidade no provedor local. SugestÃ£o: Verificar carga da CPU/GPU.")
            else:
                 pulse_content.append("- [ ] Continue o uso normal. O sistema estÃ¡ em fase de coleta de mÃ©tricas.")

            with open(self.pulse_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(pulse_content))
            
            logger.info("âœ… RelatÃ³rio de Pulso atualizado.")
        except Exception as e:
            logger.error(f"Erro ao gerar pulso: {e}")

# InstÃ¢ncia Global
evolution_engine = EvolutionEngine()
