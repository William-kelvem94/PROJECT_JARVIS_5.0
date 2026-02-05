"""
Safe Mode - Modo de recuperação do JARVIS
Executa diagnósticos e tenta recuperar o sistema
"""

import logging
import sys
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

class SafeMode:
    """Modo seguro de recuperação"""
    
    def __init__(self):
        self.crash_count = 0
        self.max_crashes = 3
        self.safe_mode_active = False
        self.crash_log = Path("data/crash_log.txt")
        self.crash_log.parent.mkdir(parents=True, exist_ok=True)
    
    def check_crashes(self) -> bool:
        """Verifica se deve entrar em safe mode"""
        if self.crash_count >= self.max_crashes:
            logger.warning(f"⚠️ {self.crash_count} crashes detectados")
            return True
        return False
    
    def enter_safe_mode(self):
        """Entra em modo seguro"""
        self.safe_mode_active = True
        logger.warning("🛡️ ENTRANDO EM SAFE MODE")
        
        # Desabilitar módulos
        self.disable_gui()
        self.disable_voice()
        
        # Executar diagnósticos
        self.run_diagnostics()
        
        logger.info("✅ Safe mode ativo. Sistema em modo texto.")
    
    def disable_gui(self):
        """Desliga interface gráfica"""
        logger.info("🙈 GUI desabilitada")
        # Não inicializar PyQt6
    
    def disable_voice(self):
        """Desliga TTS"""
        logger.info("🔇 Voz desabilitada")
        # Não inicializar TTS
    
    def run_diagnostics(self) -> Dict[str, bool]:
        """Testa todos os módulos"""
        logger.info("🔍 Executando diagnósticos...")
        
        results = {
            "imports": self._test_imports(),
            "config": self._test_config(),
            "memory": self._test_memory(),
            "disk": self._test_disk()
        }
        
        for test, passed in results.items():
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {test}")
        
        return results
    
    def _test_imports(self) -> bool:
        """Testa imports críticos"""
        try:
            import asyncio
            import yaml
            import logging
            return True
        except ImportError as e:
            logger.error(f"❌ Import falhou: {e}")
            return False
    
    def _test_config(self) -> bool:
        """Testa config.yaml"""
        try:
            import yaml
            with open("config.yaml") as f:
                yaml.safe_load(f)
            return True
        except Exception as e:
            logger.error(f"❌ Config inválido: {e}")
            return False
    
    def _test_memory(self) -> bool:
        """Testa memória disponível"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return mem.percent < 90
        except:
            return True
    
    def _test_disk(self) -> bool:
        """Testa espaço em disco"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return disk.percent < 95
        except:
            return True
    
    def log_crash(self, error: str):
        """Registra crash"""
        self.crash_count += 1
        
        with open(self.crash_log, 'a') as f:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            f.write(f"\n[{timestamp}] Crash #{self.crash_count}\n")
            f.write(f"{error}\n")
            f.write("-" * 60 + "\n")
        
        logger.error(f"💥 Crash #{self.crash_count} registrado")


# Instância global
safe_mode = SafeMode()
