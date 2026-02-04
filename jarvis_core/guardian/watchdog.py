"""
Guardian - System Watchdog
Monitor de processo e auto-restart
"""

import logging
import psutil
import time
from typing import Optional

logger = logging.getLogger(__name__)

class SystemWatchdog:
    """Monitor de saúde do sistema"""
    
    def __init__(self):
        self.process_name = "main_singularity.py"
        self.crash_count = 0
        self.max_crashes = 3
    
    def is_running(self, process_name: str) -> bool:
        """Verifica se processo está rodando"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and process_name in ' '.join(cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return False
    
    def monitor(self, check_interval: int = 5):
        """Loop de monitoramento"""
        logger.info(f"👁️ Watchdog ativo. Monitorando: {self.process_name}")
        
        while True:
            if not self.is_running(self.process_name):
                logger.warning(f"⚠️ Processo não encontrado: {self.process_name}")
                self.crash_count += 1
                
                if self.crash_count >= self.max_crashes:
                    logger.error(f"❌ Muitos crashes ({self.crash_count}). Entrando em safe mode...")
                    break
                
                logger.info(f"🔄 Tentando restart ({self.crash_count}/{self.max_crashes})...")
                self.restart()
            
            time.sleep(check_interval)
    
    def restart(self) -> bool:
        """Reinicia processo"""
        import subprocess
        import sys
        
        try:
            subprocess.Popen([sys.executable, self.process_name])
            logger.info("✅ Processo reiniciado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao reiniciar: {e}")
            return False
    
    def get_system_health(self) -> dict:
        """Retorna saúde do sistema"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "crash_count": self.crash_count
        }


# Instância global
system_watchdog = SystemWatchdog()
