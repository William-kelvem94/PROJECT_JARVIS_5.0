"""
Monitoramento persistente do sistema JARVIS 5.0 (OTIMIZADO)
"""
import time
import json
import threading
from pathlib import Path
import psutil
from datetime import datetime
import logging

class JarvisSystemMonitor:
    """Monitora e persiste métricas do sistema com baixo consumo"""
    
    def __init__(self, data_dir="data/monitoring"):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / "system_metrics.jsonl"
        self.health_file = self.data_dir / "system_health.json"
        
        self.running = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        self.interval = 300  # 5 minutos
        
    def start_monitoring(self, interval=None):
        if self.running: return
        if interval: self.interval = interval
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"✅ Monitoring started (Interval: {self.interval}s)")
        return self
    
    def _monitor_loop(self):
        while self.running:
            try:
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent
                }
                with open(self.metrics_file, 'a') as f:
                    f.write(json.dumps(metrics) + '\n')
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")
            
            time.sleep(self.interval)

    def log_error(self, error_msg):
        self.logger.error(f"System Error: {error_msg}")

system_monitor = JarvisSystemMonitor()
