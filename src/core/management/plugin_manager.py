"""
JARVIS 5.0 - Plugin Manager (Hot-Loading System)
================================================
Responsabilidade: Carregar e recarregar dinamicamente scripts de habilidades (plugins).
Monitora mudanças nos arquivos para aplicar atualizações sem reiniciar o sistema.

Inspirado no NewClassLoader do PVA.
"""

import os
import sys
import importlib
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SystemEvolutionManager:
    """Sistema de Hot-Reload e Auto-Desenvolvimento (Singularity Edition)"""
    
    def __init__(self, plugins_dir: str = "src/core/actions/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.core_dir = Path("src/core")
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_modules = {} # {rel_path: {module: mod, mtime: time}}
        self.is_running = False
        self._watcher_thread = None
        
        logger.info(f"🧬 SystemEvolutionManager inicializado.")

    def start(self):
        """Inicia o monitoramento de evolução"""
        if self.is_running: return
        self.is_running = True
        self._load_all_dynamic()
        self._watcher_thread = threading.Thread(target=self._watch_loop, daemon=True, name="SystemWatcher")
        self._watcher_thread.start()
        logger.info("📡 Sentinela de Evolução ativado (Hot-Reload Core & Plugins)")

    def _load_all_dynamic(self):
        """Carga inicial de plugins"""
        for file in self.plugins_dir.glob("*.py"):
            if file.name == "__init__.py": continue
            self._hot_reload_module(file)

    def _hot_reload_module(self, file_path: Path):
        """Recarrega qualquer módulo do sistema de forma segura"""
        try:
            # Converter path em dot-notation para importlib
            rel_path = file_path.relative_to(Path.cwd())
            module_name = str(rel_path.with_suffix("")).replace(os.sep, ".")
            
            mtime = file_path.stat().st_mtime
            
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                logger.info(f"🔄 Evolução Aplicada: {module_name}")
            else:
                sys.modules[module_name] = importlib.import_module(module_name)
                logger.info(f"🔌 Nova Capacidade: {module_name}")
            
            self.loaded_modules[str(rel_path)] = {
                "module": sys.modules[module_name],
                "last_modified": mtime
            }
            return True
        except Exception as e:
            logger.error(f"❌ Falha na evolução de {file_path.name}: {e}")
            return False

    def _watch_loop(self):
        """Monitora mudanças em plugins e arquivos CORE autorizados"""
        while self.is_running:
            try:
                # 1. Checar Plugins
                for file in self.plugins_dir.glob("*.py"):
                    self._check_file(file)
                
                # 2. Checar Core (Auto-Correção)
                # Limitamos ao core/intelligence e core/actions por segurança
                for core_file in Path("src/core/intelligence").glob("*.py"):
                    self._check_file(core_file)
                
                time.sleep(3)
            except Exception as e:
                time.sleep(5)

    def _check_file(self, file: Path):
        if file.name == "__init__.py": return
        try:
            mtime = file.stat().st_mtime
            rel_path = str(file.relative_to(Path.cwd()))
            stored_info = self.loaded_modules.get(rel_path)
            
            if not stored_info or mtime > stored_info["last_modified"]:
                logger.info(f"⚡ Mutação detectada em {file.name}. Aplicando auto-correção...")
                self._hot_reload_module(file)
                
                try:
                    from src.interface.ui_signals import ui_signals
                    ui_signals.update_status.emit(f"🧬 DNA Recodificado: {file.stem} atualizado.")
                except: pass
        except: pass

    def get_plugin_actions(self) -> Dict[str, Any]:
        """Coleta todas as ações disponíveis nos plugins carregados"""
        actions = {}
        for rel_path, info in self.loaded_modules.items():
            if "plugins" in rel_path:
                module = info["module"]
                if hasattr(module, "ACTIONS"):
                    actions.update(module.ACTIONS)
        return actions

# Singleton instance
plugin_manager = SystemEvolutionManager()
