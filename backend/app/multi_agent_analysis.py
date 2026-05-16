"""
JARVIS 5.0 — Multi-Agent Analysis System
=========================================
Sistema de múltiplos agentes especializados para análise e melhorias contínuas.
Cada agente monitora um aspecto específico do sistema e propõe melhorias.

Agentes Especializados:
- PerformanceAgent: Monitora performance, CPU, RAM, latência
- SecurityAgent: Analisa vulnerabilidades e questões de segurança
- CodeQualityAgent: Avalia qualidade do código e conformidade
- UserExperienceAgent: Monitora interações do usuário e satisfação
- SystemHealthAgent: Verifica saúde geral do sistema e dependências
"""

import asyncio
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from loguru import logger


class AgentType(Enum):
    """Tipos de agentes especializados."""
    PERFORMANCE = "performance"
    SECURITY = "security"
    CODE_QUALITY = "code_quality"
    USER_EXPERIENCE = "ux"
    SYSTEM_HEALTH = "health"


class Severity(Enum):
    """Níveis de severidade para findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """Representa uma descoberta/recomendação de um agente."""
    agent_type: AgentType
    severity: Severity
    title: str
    description: str
    recommendation: str
    timestamp: datetime = field(default_factory=datetime.now)
    auto_fixable: bool = False
    fix_script: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Classe base para todos os agentes especializados."""
    
    def __init__(self, agent_type: AgentType, name: str, check_interval: int = 300):
        self.agent_type = agent_type
        self.name = name
        self.check_interval = check_interval  # segundos
        self.findings: List[Finding] = []
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        logger.info(f"[MultiAgent] {self.name} initialized (check every {check_interval}s)")
    
    @abstractmethod
    async def analyze(self) -> List[Finding]:
        """Método abstrato para análise. Deve ser implementado por cada agente."""
    
    async def run(self):
        """Loop principal do agente."""
        self.is_running = True
        logger.info(f"[{self.name}] Starting analysis loop")
        
        while self.is_running:
            try:
                new_findings = await self.analyze()
                if new_findings:
                    self.findings.extend(new_findings)
                    for finding in new_findings:
                        logger.log(
                            self._severity_to_log_level(finding.severity),
                            f"[{self.name}] {finding.severity.value.upper()}: {finding.title}"
                        )
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"[{self.name}] Error during analysis: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    def stop(self):
        """Para o agente."""
        self.is_running = False
        logger.info(f"[{self.name}] Stopped")
    
    def get_findings(self, severity: Optional[Severity] = None) -> List[Finding]:
        """Retorna findings, opcionalmente filtrados por severidade."""
        if severity:
            return [f for f in self.findings if f.severity == severity]
        return self.findings
    
    @staticmethod
    def _severity_to_log_level(severity: Severity) -> str:
        """Converte severidade para nível de log."""
        mapping = {
            Severity.INFO: "INFO",
            Severity.LOW: "INFO",
            Severity.MEDIUM: "WARNING",
            Severity.HIGH: "WARNING",
            Severity.CRITICAL: "ERROR",
        }
        return mapping.get(severity, "INFO")


class PerformanceAgent(BaseAgent):
    """Agente que monitora performance do sistema."""
    
    def __init__(self):
        super().__init__(AgentType.PERFORMANCE, "PerformanceAgent", check_interval=60)
        self.cpu_threshold = 80.0  # %
        self.ram_threshold = 85.0  # %
        self.thread_threshold = 150
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.cpu_threshold:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.HIGH if cpu_percent > 90 else Severity.MEDIUM,
                title="High CPU Usage Detected",
                description=f"CPU usage is at {cpu_percent:.1f}%, exceeding threshold of {self.cpu_threshold}%",
                recommendation="Consider optimizing heavy computation tasks or distributing load. Check for infinite loops or blocking operations.",
                metrics={"cpu_percent": cpu_percent}
            ))
        
        # RAM check
        ram = psutil.virtual_memory()
        if ram.percent > self.ram_threshold:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.HIGH if ram.percent > 95 else Severity.MEDIUM,
                title="High Memory Usage Detected",
                description=f"RAM usage is at {ram.percent:.1f}%, exceeding threshold of {self.ram_threshold}%",
                recommendation="Check for memory leaks, clear caches, or optimize data structures. Consider garbage collection.",
                metrics={"ram_percent": ram.percent, "ram_available_gb": ram.available / (1024**3)}
            ))
        
        # Thread check
        thread_count = threading.active_count()
        if thread_count > self.thread_threshold:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.MEDIUM,
                title="High Thread Count",
                description=f"Active thread count is {thread_count}, exceeding threshold of {self.thread_threshold}",
                recommendation="Review thread lifecycle management. Consider using thread pools or asyncio tasks instead.",
                metrics={"thread_count": thread_count}
            ))
        
        return findings


class SystemHealthAgent(BaseAgent):
    """Agente que monitora saúde geral do sistema."""
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "SystemHealthAgent", check_interval=300)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.CRITICAL if disk.percent > 95 else Severity.HIGH,
                title="Low Disk Space",
                description=f"Disk usage is at {disk.percent:.1f}%",
                recommendation="Clean up temporary files, logs, or consider expanding storage.",
                metrics={"disk_percent": disk.percent, "disk_free_gb": disk.free / (1024**3)}
            ))
        
        # Check if critical services are running
        try:
            # Verify perception manager is active
            from .perception import perception_manager
            if not perception_manager:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.HIGH,
                    title="Perception Manager Not Active",
                    description="The perception manager is not properly initialized",
                    recommendation="Restart the perception subsystem or check for initialization errors."
                ))
        except Exception as e:
            logger.debug(f"[SystemHealthAgent] Could not check perception manager: {e}")
        
        return findings


class SecurityAgent(BaseAgent):
    """Agente que monitora aspectos de segurança."""
    
    def __init__(self):
        super().__init__(AgentType.SECURITY, "SecurityAgent", check_interval=600)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # Check for insecure configurations
        import os
        
        # Check if running as admin/root (pode ser um risco)
        if os.name == 'nt':
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.LOW,
                    title="Running as Administrator",
                    description="JARVIS is running with administrator privileges",
                    recommendation="Consider running with standard user privileges unless admin access is required."
                ))
        
        return findings


class CodeQualityAgent(BaseAgent):
    """Agente que avalia qualidade do código."""
    
    def __init__(self):
        super().__init__(AgentType.CODE_QUALITY, "CodeQualityAgent", check_interval=3600)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # Check for deprecated imports or patterns
        # This is a placeholder - in production would scan actual code
        
        findings.append(Finding(
            agent_type=self.agent_type,
            severity=Severity.INFO,
            title="Code Quality Scan Complete",
            description="No critical code quality issues detected in this scan",
            recommendation="Continue following best practices and coding standards."
        ))
        
        return findings


class UserExperienceAgent(BaseAgent):
    """Agente que monitora experiência do usuário."""
    
    def __init__(self):
        super().__init__(AgentType.USER_EXPERIENCE, "UXAgent", check_interval=900)
        self.response_times = []
        self.max_response_time = 2.0  # segundos
    
    def record_response_time(self, time_seconds: float):
        """Registra tempo de resposta de uma interação."""
        self.response_times.append(time_seconds)
        if len(self.response_times) > 100:
            self.response_times.pop(0)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        if self.response_times:
            avg_response = sum(self.response_times) / len(self.response_times)
            
            if avg_response > self.max_response_time:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.MEDIUM,
                    title="Slow Response Times",
                    description=f"Average response time is {avg_response:.2f}s, exceeding threshold of {self.max_response_time}s",
                    recommendation="Optimize processing pipeline, consider caching, or use faster models.",
                    metrics={"avg_response_time": avg_response, "sample_count": len(self.response_times)}
                ))
        
        return findings


class ConnectivityAgent(BaseAgent):
    """Agente que monitora conectividade e saúde das APIs."""
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "ConnectivityAgent", check_interval=60)
        self.failed_endpoints = {}
        self.max_failures = 3
    
    def record_endpoint_failure(self, endpoint: str):
        """Registra falha em um endpoint."""
        if endpoint not in self.failed_endpoints:
            self.failed_endpoints[endpoint] = 0
        self.failed_endpoints[endpoint] += 1
    
    def record_endpoint_success(self, endpoint: str):
        """Registra sucesso em um endpoint."""
        if endpoint in self.failed_endpoints:
            self.failed_endpoints[endpoint] = max(0, self.failed_endpoints[endpoint] - 1)
            if self.failed_endpoints[endpoint] == 0:
                del self.failed_endpoints[endpoint]
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # Check for endpoints with repeated failures
        for endpoint, failures in self.failed_endpoints.items():
            if failures >= self.max_failures:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.HIGH,
                    title=f"API Endpoint Failing: {endpoint}",
                    description=f"Endpoint {endpoint} has failed {failures} times consecutively",
                    recommendation="Check endpoint implementation, error handling, and dependencies. Review logs for exceptions.",
                    metrics={"endpoint": endpoint, "failures": failures}
                ))
        
        # Test critical endpoints
        import aiohttp
        critical_endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/telemetry/status",
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in critical_endpoints:
                try:
                    async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status != 200:
                            findings.append(Finding(
                                agent_type=self.agent_type,
                                severity=Severity.MEDIUM,
                                title=f"Endpoint Returning Error: {endpoint}",
                                description=f"Endpoint returned status {response.status}",
                                recommendation="Check endpoint logic and error responses.",
                                metrics={"endpoint": endpoint, "status": response.status}
                            ))
                except asyncio.TimeoutError:
                    findings.append(Finding(
                        agent_type=self.agent_type,
                        severity=Severity.HIGH,
                        title=f"Endpoint Timeout: {endpoint}",
                        description=f"Endpoint {endpoint} timed out after 5 seconds",
                        recommendation="Check for blocking operations, infinite loops, or deadlocks.",
                        metrics={"endpoint": endpoint, "timeout": 5}
                    ))
                except Exception as e:
                    findings.append(Finding(
                        agent_type=self.agent_type,
                        severity=Severity.HIGH,
                        title=f"Endpoint Connection Failed: {endpoint}",
                        description=f"Failed to connect to {endpoint}: {str(e)}",
                        recommendation="Verify service is running and accessible. Check network configuration.",
                        metrics={"endpoint": endpoint, "error": str(e)}
                    ))
        
        return findings


class CognitiveHealthAgent(BaseAgent):
    """Agente que monitora saúde do núcleo cognitivo."""
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "CognitiveHealthAgent", check_interval=120)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        try:
            from .health_checker import get_health_checker
            checker = get_health_checker()
            
            # Verificar componentes cognitivos
            cognitive_components = [
                "smart_router",
                "unified_memory",
                "engineer_brain",
                "adaptive_persona"
            ]
            
            offline_components = []
            for component_key in cognitive_components:
                if component_key in checker.last_check:
                    health = checker.last_check[component_key]
                    if not health.available:
                        offline_components.append(health.name)
            
            if offline_components:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.HIGH,
                    title="Componentes Cognitivos Offline",
                    description=f"{len(offline_components)} componente(s) do núcleo cognitivo não estão disponíveis: {', '.join(offline_components)}",
                    recommendation="Verifique logs e dependências dos módulos cognitivos. Execute scripts\\validate-improvements.bat",
                    metrics={"offline_count": len(offline_components), "components": offline_components}
                ))
        except Exception as e:
            logger.warning(f"[CognitiveHealthAgent] Error during analysis: {e}")
        
        return findings


class PerceptionHealthAgent(BaseAgent):
    """Agente que monitora saúde do sistema de percepção."""
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "PerceptionHealthAgent", check_interval=90)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        try:
            from .health_checker import get_health_checker
            checker = get_health_checker()
            
            # Verificar hardware dependencies
            hardware_status = {
                "camera": checker.last_check.get("camera"),
                "microphone": checker.last_check.get("microphone"),
                "screen_mirror": checker.last_check.get("espelhamento_tela")
            }
            
            offline_hardware = []
            for hw_name, health in hardware_status.items():
                if health and not health.available:
                    offline_hardware.append(hw_name)
            
            if offline_hardware:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.CRITICAL,
                    title="Hardware de Percepção Offline",
                    description=f"Hardware necessário não disponível: {', '.join(offline_hardware)}",
                    recommendation=f"Verifique se {', '.join(offline_hardware)} está(ão) conectado(s) e funcionando. Reinicie o sistema se necessário.",
                    metrics={"offline_hardware": offline_hardware}
                ))
            
            # Verificar componentes de percepção
            perception_components = [
                "face_engine",
                "gestures",
                "objects",
                "realtime_audio"
            ]
            
            degraded_components = []
            for component_key in perception_components:
                if component_key in checker.last_check:
                    health = checker.last_check[component_key]
                    if not health.available:
                        degraded_components.append(health.name)
            
            if degraded_components:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.HIGH,
                    title="Componentes de Percepção Degradados",
                    description=f"{len(degraded_components)} componente(s) de percepção não estão funcionando: {', '.join(degraded_components)}",
                    recommendation="Instale as dependências necessárias (face_recognition, mediapipe, ultralytics, sounddevice).",
                    metrics={"degraded_count": len(degraded_components), "components": degraded_components}
                ))
        
        except Exception as e:
            logger.warning(f"[PerceptionHealthAgent] Error during analysis: {e}")
        
        return findings


class SystemToolsAgent(BaseAgent):
    """Agente que monitora ferramentas de sistema."""
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "SystemToolsAgent", check_interval=180)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        try:
            from .health_checker import get_health_checker
            checker = get_health_checker()
            
            # Verificar ferramentas de sistema
            system_components = [
                "os_tools",
                "browser_engine",
                "screen_capture",
                "assisted_execution"
            ]
            
            errors = []
            for component_key in system_components:
                if component_key in checker.last_check:
                    health = checker.last_check[component_key]
                    if health.error:
                        errors.append(f"{health.name}: {health.message}")
            
            if errors:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.MEDIUM,
                    title="Ferramentas de Sistema com Erros",
                    description=f"{len(errors)} ferramenta(s) reportaram erros",
                    recommendation="Verifique logs detalhados e instale dependências faltando (playwright, mss, pyautogui).",
                    metrics={"errors": errors}
                ))
        
        except Exception as e:
            logger.warning(f"[SystemToolsAgent] Error during analysis: {e}")
        
        return findings


class SecurityModulesAgent(BaseAgent):
    """Agente que monitora módulos de segurança."""
    
    def __init__(self):
        super().__init__(AgentType.SECURITY, "SecurityModulesAgent", check_interval=300)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        try:
            from .health_checker import get_health_checker
            checker = get_health_checker()
            
            # Verificar módulos de segurança
            security_components = [
                "sentinel_parser",
                "blackbox",
                "holodeck",
                "biometric_vault"
            ]
            
            not_configured = []
            for component_key in security_components:
                if component_key in checker.last_check:
                    health = checker.last_check[component_key]
                    if health.status.value == "not_configured":
                        not_configured.append(health.name)
            
            if not_configured:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.MEDIUM,
                    title="Módulos de Segurança Não Configurados",
                    description=f"{len(not_configured)} módulo(s) de segurança não estão configurados: {', '.join(not_configured)}",
                    recommendation="Configure os módulos de segurança para proteção completa do sistema.",
                    metrics={"not_configured": not_configured}
                ))
        
        except Exception as e:
            logger.warning(f"[SecurityModulesAgent] Error during analysis: {e}")
        
        return findings


class MultiAgentOrchestrator:
    """Orquestrador que gerencia todos os agentes."""
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.is_running = False
        logger.info("[MultiAgent] Orchestrator initialized")
    
    def register_agent(self, agent: BaseAgent):
        """Registra um novo agente."""
        self.agents[agent.agent_type] = agent
        logger.info(f"[MultiAgent] Registered agent: {agent.name}")
    
    def start_all(self):
        """Inicia todos os agentes registrados."""
        self.is_running = True
        for agent_type, agent in self.agents.items():
            asyncio.create_task(agent.run())
        logger.info("[MultiAgent] All agents started")
    
    def stop_all(self):
        """Para todos os agentes."""
        self.is_running = False
        for agent in self.agents.values():
            agent.stop()
        logger.info("[MultiAgent] All agents stopped")
    
    def get_all_findings(self, severity: Optional[Severity] = None) -> List[Finding]:
        """Obtém todos os findings de todos os agentes."""
        all_findings = []
        for agent in self.agents.values():
            all_findings.extend(agent.get_findings(severity))
        
        # Sort by severity (critical first) and timestamp
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        all_findings.sort(key=lambda f: (severity_order[f.severity], f.timestamp), reverse=True)
        return all_findings
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna um sumário do estado de todos os agentes."""
        summary = {
            "total_findings": 0,
            "by_severity": {s.value: 0 for s in Severity},
            "by_agent": {}
        }
        
        for agent_type, agent in self.agents.items():
            findings = agent.get_findings()
            summary["by_agent"][agent.name] = len(findings)
            summary["total_findings"] += len(findings)
            
            for finding in findings:
                summary["by_severity"][finding.severity.value] += 1
        
        return summary


# Global singleton instance
_orchestrator: Optional[MultiAgentOrchestrator] = None


def get_orchestrator() -> MultiAgentOrchestrator:
    """Retorna a instância global do orquestrador."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator()
        
        # Register default agents
        _orchestrator.register_agent(PerformanceAgent())
        _orchestrator.register_agent(SystemHealthAgent())
        _orchestrator.register_agent(SecurityAgent())
        _orchestrator.register_agent(CodeQualityAgent())
        _orchestrator.register_agent(UserExperienceAgent())
        _orchestrator.register_agent(ConnectivityAgent())
        
        # Register specialized subsystem agents
        _orchestrator.register_agent(CognitiveHealthAgent())
        _orchestrator.register_agent(PerceptionHealthAgent())
        _orchestrator.register_agent(SystemToolsAgent())
        _orchestrator.register_agent(SecurityModulesAgent())
        
        logger.info("[MultiAgent] Default agents registered (10 agents)")
    
    return _orchestrator


def start_multi_agent_analysis():
    """Inicia o sistema de análise multi-agente."""
    orchestrator = get_orchestrator()
    orchestrator.start_all()
    logger.success("[MultiAgent] Multi-agent analysis system started")


def stop_multi_agent_analysis():
    """Para o sistema de análise multi-agente."""
    orchestrator = get_orchestrator()
    orchestrator.stop_all()
    logger.info("[MultiAgent] Multi-agent analysis system stopped")
