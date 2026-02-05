"""
Guardian - Health Monitor
Monitoramento de saúde do sistema
"""

import logging
import psutil
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor de saúde do sistema"""
    
    def __init__(self):
        self.health_history = []
        self.max_history = 100
    
    def check_cpu(self) -> float:
        """Uso de CPU (%)"""
        return psutil.cpu_percent(interval=1)
    
    def check_memory(self) -> Dict[str, float]:
        """Uso de memória"""
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_gb": mem.used / (1024**3),
            "total_gb": mem.total / (1024**3)
        }
    
    def check_disk(self) -> Dict[str, float]:
        """Espaço em disco"""
        disk = psutil.disk_usage('/')
        return {
            "percent": disk.percent,
            "used_gb": disk.used / (1024**3),
            "total_gb": disk.total / (1024**3),
            "free_gb": disk.free / (1024**3)
        }
    
    def check_network(self) -> bool:
        """Conectividade de rede"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    def get_health_score(self) -> int:
        """Score de saúde (0-100)"""
        score = 100
        
        # CPU
        cpu = self.check_cpu()
        if cpu > 80:
            score -= 20
        elif cpu > 60:
            score -= 10
        
        # Memória
        mem = self.check_memory()
        if mem["percent"] > 90:
            score -= 30
        elif mem["percent"] > 75:
            score -= 15
        
        # Disco
        disk = self.check_disk()
        if disk["percent"] > 95:
            score -= 25
        elif disk["percent"] > 85:
            score -= 10
        
        # Rede
        if not self.check_network():
            score -= 15
        
        return max(0, score)
    
    def get_full_status(self) -> Dict:
        """Status completo"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": self.check_cpu(),
            "memory": self.check_memory(),
            "disk": self.check_disk(),
            "network_ok": self.check_network(),
            "health_score": self.get_health_score()
        }
        
        # Adicionar ao histórico
        self.health_history.append(status)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)
        
        return status
    
    def get_alerts(self) -> list:
        """Retorna alertas de saúde"""
        alerts = []
        
        cpu = self.check_cpu()
        if cpu > 80:
            alerts.append(f"⚠️ CPU alta: {cpu:.1f}%")
        
        mem = self.check_memory()
        if mem["percent"] > 85:
            alerts.append(f"⚠️ Memória alta: {mem['percent']:.1f}%")
        
        disk = self.check_disk()
        if disk["percent"] > 90:
            alerts.append(f"⚠️ Disco cheio: {disk['percent']:.1f}%")
        
        if not self.check_network():
            alerts.append("⚠️ Sem conexão de rede")
        
        return alerts


# Instância global
health_monitor = HealthMonitor()


# Teste
if __name__ == "__main__":
    monitor = HealthMonitor()
    
    status = monitor.get_full_status()
    print(f"CPU: {status['cpu_percent']:.1f}%")
    print(f"RAM: {status['memory']['percent']:.1f}%")
    print(f"Disco: {status['disk']['percent']:.1f}%")
    print(f"Rede: {'✅' if status['network_ok'] else '❌'}")
    print(f"Score: {status['health_score']}/100")
    
    alerts = monitor.get_alerts()
    if alerts:
        print("\nAlertas:")
        for alert in alerts:
            print(f"  {alert}")
