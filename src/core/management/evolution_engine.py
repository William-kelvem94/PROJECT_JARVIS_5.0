import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class EvolutionEngine:
    """
    O Cérebro de Autodiagnóstico e Evolução do JARVIS.
    Monitora a saúde de todos os módulos e aprende com falhas de execução.
    """

    def __init__(self):
        self.data_dir = Path("data/monitoring")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.pulse_file = Path("data/SYSTEM_PULSE.md")
        
        # Estado atual dos módulos
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
        """Atualiza o status de um módulo específico"""
        if module in self.module_health:
            self.module_health[module] = {
                "status": status,
                "last_check": datetime.now().isoformat(),
                "error": error
            }
            logger.debug(f"EvolutionEngine: {module} reportou status {status}")

    def log_failure(self, task: str, error: str, provider: str):
        """Registra uma falha técnica para análise de evolução"""
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
        log_file = Path("data/EVOLUTION.log")
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
            logger.info(f"🧬 Evolution logged for {file_path}")
        except Exception as e:
            logger.error(f"Failed to log evolution: {e}")

    def _load_failures(self):
        file = self.data_dir / "failure_history.json"
        if file.exists():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.failure_patterns = json.load(f)
            except:
                self.failure_patterns = []

    def _save_failures(self):
        file = self.data_dir / "failure_history.json"
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.failure_patterns[-100:], f, indent=2)

    def generate_pulse_report(self):
        """Gera o relatório SYSTEM_PULSE.md organizado e limpo"""
        try:
            pulse_content = [
                "# 🫀 JARVIS SYSTEM PULSE\n",
                f"**Última Atualização:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n",
                "## 🛠️ Status dos Módulos\n",
                "| Módulo | Estado | Detalhes |",
                "| :--- | :--- | :--- |"
            ]
            
            for mod, data in self.module_health.items():
                icon = "🟢" if data['status'] == "OK" else "🔴" if data['status'] == "FAIL" else "🟡"
                pulse_content.append(f"| {mod} | {icon} {data['status']} | {data['error'] or 'Operacional'} |")
            
            pulse_content.append("\n## 🧠 Histórico de Aprendizado (Auto-Correção)\n")
            if not self.failure_patterns:
                pulse_content.append("*Nenhuma falha crítica detectada recentemente. Sistema estável.*")
            else:
                for fail in self.failure_patterns[-5:]:
                    pulse_content.append(f"- **{fail['timestamp'][:16]}**: Falha no `{fail['provider']}` durante `{fail['task']}`. Erro: `{fail['error']}`")
            
            pulse_content.append("\n## 📡 Sugestões de Melhoria Manual\n")
            # Adicionar sugestão baseada em padrões de erro
            if len(self.failure_patterns) > 5:
                pulse_content.append("- [ ] Detectamos instabilidade no provedor local. Sugestão: Verificar carga da CPU/GPU.")
            else:
                 pulse_content.append("- [ ] Continue o uso normal. O sistema está em fase de coleta de métricas.")

            with open(self.pulse_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(pulse_content))
            
            logger.info("✅ Relatório de Pulso atualizado.")
        except Exception as e:
            logger.error(f"Erro ao gerar pulso: {e}")

# Instância Global
evolution_engine = EvolutionEngine()
