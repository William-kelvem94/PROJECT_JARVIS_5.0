# -*- coding: utf-8 -*-
import os
import autopep8
import logging
import py_compile
import time
from pathlib import Path
from typing import Dict, Any, List

from .holodeck import HoloDeck

logger = logging.getLogger("JARVIS-EVOLUTION")

class EvolutionEngine:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.backup_dir = self.root / "data" / "evolution_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.holodeck = HoloDeck(project_root)

    def evolve_safely(self, module_path: str, objective: str, brain_callback) -> bool:
        """Processo completo: Prospecção -> HoloDeck -> Produção."""
        sim_id = f"evolve_{int(time.time())}"
        logger.info(f"🧬 Iniciando Evolução Protegida no HoloDeck: {sim_id}")
        
        # 1. Cria ambiente de simulação com o módulo alvo
        sim_path = self.holodeck.create_simulation(sim_id, modules_to_copy=[module_path])
        
        # 2. Gera a proposta de melhoria
        current_code = self.read_module(module_path)
        prompt = (f"MODULO: {module_path}\nOBJETIVO: {objective}\nCÓDIGO:\n{current_code}\n"
                  "REESCREVA IMPLEMENTANDO A MELHORIA.")
        
        new_code = brain_callback(prompt)
        if not new_code: return False
        
        # 3. Testa na Sandbox (HoloDeck)
        temp_module = sim_path / module_path
        with open(temp_module, "w", encoding="utf-8") as f:
            f.write(new_code)
            
        test_res = self.holodeck.run_tests(sim_id, module_path) # Testa se o arquivo carrega
        
        if test_res["status"] == "success":
            logger.info("📡 Simulação no HoloDeck validada com sucesso! Promovendo para Produção.")
            success = self.apply_update(module_path, new_code)
            self.holodeck.cleanup(sim_id)
            return success
        else:
            logger.error(f"⚠️ Falha na simulação do HoloDeck: {test_res.get('stderr')}")
            self.holodeck.cleanup(sim_id)
            return False

    def read_module(self, module_path: str) -> str:
        """Lê o código de um módulo interno."""
        full_path = self.root / module_path
        if not full_path.exists():
            return ""
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def propose_improvement(self, module_path: str, objective: str, brain_callback) -> bool:
        """
        Usa o LLM para propor uma melhoria no código baseado no conhecimento adquirido.
        """
        current_code = self.read_module(module_path)
        if not current_code: return False
        
        prompt = (
            f"--- MÓDULO ATUAL ---\n{current_code}\n\n"
            f"--- OBJETIVO DE EVOLUÇÃO ---\n{objective}\n\n"
            "Instrução: Re-escreva o código acima implementando a melhoria. "
            "Retorne APENAS o código completo atualizado, formatado em Python profissional."
        )
        
        # Aqui chamamos o cérebro/ollama para gerar o novo código
        new_code = brain_callback(prompt)
        
        if new_code and len(new_code) > 10:
            return self.apply_update(module_path, new_code)
        return False

    def apply_update(self, module_path: str, new_code: str) -> bool:
        """Aplica a alteração de forma segura (Backups + Sanity Check)."""
        full_path = self.root / module_path
        
        # 1. Sanity Check (O código compila?)
        temp_file = full_path.with_suffix(".tmp.py")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(new_code)
            
        try:
            py_compile.compile(str(temp_file), doraise=True)
            logger.info(f"✅ Sanity check passou para {module_path}")
        except py_compile.PyCompileError as e:
            logger.error(f"❌ Código gerado inválido para {module_path}: {e}")
            os.remove(temp_file)
            return False

        # 2. Backup da versão atual
        timestamp = int(os.path.getmtime(full_path))
        backup_path = self.backup_dir / f"{full_path.name}.{timestamp}.bak"
        with open(full_path, "r", encoding="utf-8") as current_f:
            with open(backup_path, "w", encoding="utf-8") as backup_f:
                backup_f.write(current_f.read())

        # 3. Formatação Profissional e Escrita Final
        formatted_code = autopep8.fix_code(new_code)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(formatted_code)
        
        os.remove(temp_file)
        logger.info(f"🚀 Módulo {module_path} evoluído com sucesso!")
        return True

    def get_evolution_status(self) -> Dict[str, Any]:
        backups = list(self.backup_dir.glob("*.bak"))
        return {
            "total_evolutions": len(backups),
            "last_evolution": backups[-1].name if backups else "none"
        }
