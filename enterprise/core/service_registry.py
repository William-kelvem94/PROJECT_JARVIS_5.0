"""
Service Registry - Descoberta e Registro de Serviços
Gerencia registro de microserviços e health checks
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from core.logger import logger

class ServiceStatus(Enum):
    """Status de um serviço."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ServiceInfo:
    """Informações de um serviço."""
    name: str
    version: str
    host: str
    port: int
    endpoints: List[str]
    status: ServiceStatus
    last_heartbeat: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        data = asdict(self)
        data["status"] = self.status.value
        data["last_heartbeat"] = self.last_heartbeat.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServiceInfo":
        """Cria a partir de dicionário."""
        data["status"] = ServiceStatus(data["status"])
        data["last_heartbeat"] = datetime.fromisoformat(data["last_heartbeat"])
        return cls(**data)

class ServiceRegistry:
    """
    Registry para descoberta de serviços.
    Gerencia registro, health checks e descoberta de serviços.
    """
    
    def __init__(self, heartbeat_timeout: float = 60.0):
        """
        Inicializa Service Registry.
        
        Args:
            heartbeat_timeout: Timeout em segundos para considerar serviço morto
        """
        self.services: Dict[str, ServiceInfo] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self.running = False
        
        logger.info(f"Service Registry inicializado (timeout={heartbeat_timeout}s)")
    
    async def start(self):
        """Inicia o registry (inicia health check loop)."""
        if self.running:
            return
        
        self.running = True
        asyncio.create_task(self._health_check_loop())
        logger.info("Service Registry iniciado")
    
    async def stop(self):
        """Para o registry."""
        self.running = False
        logger.info("Service Registry parado")
    
    def register(
        self,
        name: str,
        version: str,
        host: str,
        port: int,
        endpoints: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra um serviço.
        
        Args:
            name: Nome do serviço
            version: Versão
            host: Host
            port: Porta
            endpoints: Lista de endpoints
            metadata: Metadados adicionais
        
        Returns:
            True se registrou com sucesso
        """
        service = ServiceInfo(
            name=name,
            version=version,
            host=host,
            port=port,
            endpoints=endpoints,
            status=ServiceStatus.HEALTHY,
            last_heartbeat=datetime.now(),
            metadata=metadata or {}
        )
        
        self.services[name] = service
        logger.info(f"Serviço registrado: {name} v{version} @ {host}:{port}")
        return True
    
    def unregister(self, name: str) -> bool:
        """
        Remove registro de serviço.
        
        Args:
            name: Nome do serviço
        
        Returns:
            True se removeu
        """
        if name in self.services:
            del self.services[name]
            logger.info(f"Serviço removido: {name}")
            return True
        return False
    
    def heartbeat(self, name: str) -> bool:
        """
        Atualiza heartbeat de um serviço.
        
        Args:
            name: Nome do serviço
        
        Returns:
            True se serviço está registrado
        """
        if name in self.services:
            self.services[name].last_heartbeat = datetime.now()
            self.services[name].status = ServiceStatus.HEALTHY
            return True
        return False
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        """
        Obtém informações de um serviço.
        
        Args:
            name: Nome do serviço
        
        Returns:
            Informações do serviço ou None
        """
        service = self.services.get(name)
        
        # Verificar se serviço ainda está vivo
        if service:
            time_since_heartbeat = (datetime.now() - service.last_heartbeat).total_seconds()
            if time_since_heartbeat > self.heartbeat_timeout:
                service.status = ServiceStatus.UNHEALTHY
        
        return service
    
    def get_service_url(self, name: str, endpoint: Optional[str] = None) -> Optional[str]:
        """
        Obtém URL completa de um serviço.
        
        Args:
            name: Nome do serviço
            endpoint: Endpoint específico (opcional)
        
        Returns:
            URL completa ou None
        """
        service = self.get_service(name)
        if not service:
            return None
        
        base_url = f"http://{service.host}:{service.port}"
        
        if endpoint:
            # Verificar se endpoint existe
            if endpoint in service.endpoints:
                return f"{base_url}{endpoint}"
            else:
                logger.warning(f"Endpoint {endpoint} não encontrado em {name}")
        
        return base_url
    
    def list_services(
        self,
        status_filter: Optional[ServiceStatus] = None
    ) -> List[ServiceInfo]:
        """
        Lista todos os serviços.
        
        Args:
            status_filter: Filtrar por status (opcional)
        
        Returns:
            Lista de serviços
        """
        services = list(self.services.values())
        
        if status_filter:
            services = [s for s in services if s.status == status_filter]
        
        return services
    
    async def _health_check_loop(self):
        """Loop para verificar saúde dos serviços."""
        while self.running:
            await asyncio.sleep(10)  # Verificar a cada 10 segundos
            
            now = datetime.now()
            for service_name, service in list(self.services.items()):
                time_since_heartbeat = (now - service.last_heartbeat).total_seconds()
                
                if time_since_heartbeat > self.heartbeat_timeout:
                    # Serviço não enviou heartbeat, marcar como unhealthy
                    service.status = ServiceStatus.UNHEALTHY
                    logger.warning(
                        f"Serviço {service_name} não enviou heartbeat há "
                        f"{time_since_heartbeat:.1f}s"
                    )
                elif time_since_heartbeat > self.heartbeat_timeout * 0.7:
                    # Aproximando do timeout, marcar como degraded
                    service.status = ServiceStatus.DEGRADED
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Retorna resumo de saúde de todos os serviços."""
        healthy = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        degraded = len([s for s in self.services.values() if s.status == ServiceStatus.DEGRADED])
        unhealthy = len([s for s in self.services.values() if s.status == ServiceStatus.UNHEALTHY])
        
        return {
            "total_services": len(self.services),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "services": {name: info.to_dict() for name, info in self.services.items()}
        }

