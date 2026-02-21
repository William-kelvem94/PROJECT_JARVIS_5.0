# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("JARVIS-HOLODECK")

class HoloDeck:
    """
    Simulador de Ambiente Isolado (Sandbox).
    Onde o JARVIS testa novas funções e correções antes da implantação.
    """
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.holo_root = self.root / "data" / "holodeck"
        self.holo_root.mkdir(parents=True, exist_ok=True)
        
    def create_simulation(self, sim_id: str, modules_to_copy: list = None) -> Path:
        """Cria um ambiente isolado para testes."""
        sim_path = self.holo_root / sim_id
        if sim_path.exists():
            shutil.rmtree(sim_path)
        sim_path.mkdir()
        
        # Copia dependências básicas e módulos solicitados
        if modules_to_copy:
            for mod in modules_to_copy:
                src = self.root / mod
                if src.exists():
                    dst = sim_path / mod
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if src.is_dir():
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
        
        logger.info(f"🌌 Simulação '{sim_id}' inicializada no HoloDeck.")
        return sim_path

    def run_tests(self, sim_id: str, script_path: str) -> Dict[str, Any]:
        """Executa um script de teste dentro da simulação."""
        sim_path = self.holo_root / sim_id
        full_script = sim_path / script_path
        
        if not full_script.exists():
            return {"status": "error", "message": "Script de teste não encontrado."}
            
        try:
            # Roda em subset de processo isolado
            result = subprocess.run(
                ["python", str(full_script)],
                cwd=str(sim_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Simulação excedeu o tempo limite (Timeout)."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cleanup(self, sim_id: str):
        """Remove a simulação do HoloDeck."""
        sim_path = self.holo_root / sim_id
        if sim_path.exists():
            shutil.rmtree(sim_path)
            logger.info(f"🧹 Simulação '{sim_id}' descartada.")

    def get_active_simulations(self):
        return [d.name for d in self.holo_root.iterdir() if d.is_dir()]
