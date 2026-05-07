"""
JARVIS 5.0 — Auto-Fix Agent System
====================================
Agentes especializados que não apenas detectam problemas,
mas CORRIGEM automaticamente quando possível.
"""

import asyncio
import subprocess
import os
from typing import List, Dict, Any
from loguru import logger
from .multi_agent_analysis import BaseAgent, Finding, Severity, AgentType


class AutoFixAgent(BaseAgent):
    """
    Agente que tenta corrigir automaticamente problemas detectados.
    Atua após outros agentes detectarem issues.
    """
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "AutoFixAgent", check_interval=300)
        self.fixes_applied = []
        self.auto_fix_enabled = os.getenv("JARVIS_AUTO_FIX", "1") == "1"
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        if not self.auto_fix_enabled:
            return findings
        
        try:
            from .multi_agent_analysis import get_orchestrator
            orchestrator = get_orchestrator()
            
            # Pegar findings HIGH e CRITICAL de outros agentes
            critical = orchestrator.get_all_findings(severity=Severity.CRITICAL)
            high = orchestrator.get_all_findings(severity=Severity.HIGH)
            
            for finding in critical + high:
                fix_result = await self._try_auto_fix(finding)
                
                if fix_result["fixed"]:
                    findings.append(Finding(
                        agent_type=self.agent_type,
                        severity=Severity.INFO,
                        title=f"Auto-Fix Applied: {finding.title}",
                        description=f"Correção automática aplicada: {fix_result['action']}",
                        recommendation="Verifique se a correção funcionou corretamente.",
                        metrics={
                            "original_finding": finding.title,
                            "fix_action": fix_result['action'],
                            "timestamp": fix_result['timestamp']
                        }
                    ))
                    self.fixes_applied.append(fix_result)
        
        except Exception as e:
            logger.warning(f"[AutoFixAgent] Error during analysis: {e}")
        
        return findings
    
    async def _try_auto_fix(self, finding: Finding) -> Dict[str, Any]:
        """Tenta aplicar correção automática baseado no tipo de problema."""
        
        result = {
            "fixed": False,
            "action": None,
            "timestamp": None
        }
        
        # Auto-fix para hardware offline
        if "Hardware de Percepção Offline" in finding.title:
            # Não podemos corrigir hardware desconectado, mas podemos resetar
            result["action"] = "Hardware offline detection - manual intervention required"
            logger.info(f"[AutoFixAgent] Hardware issue detected but cannot auto-fix: {finding.description}")
        
        # Auto-fix para componentes não configurados
        elif "Não Configurados" in finding.title:
            result["action"] = await self._create_missing_directories(finding)
            if result["action"]:
                result["fixed"] = True
        
        # Auto-fix para dependências faltando
        elif "não instalado" in finding.description.lower():
            result["action"] = await self._install_missing_dependencies(finding)
            if result["action"]:
                result["fixed"] = True
        
        return result
    
    async def _create_missing_directories(self, finding: Finding) -> str:
        """Cria diretórios faltando para componentes."""
        try:
            # Extrair diretórios do finding
            if "holodeck" in finding.description.lower():
                os.makedirs("data/holodeck", exist_ok=True)
                logger.success("[AutoFixAgent] Created data/holodeck directory")
                return "Created data/holodeck directory"
            
            if "blackbox" in finding.description.lower():
                os.makedirs("data", exist_ok=True)
                logger.success("[AutoFixAgent] Created data directory for blackbox")
                return "Created data directory"
        
        except Exception as e:
            logger.error(f"[AutoFixAgent] Failed to create directories: {e}")
        
        return None
    
    async def _install_missing_dependencies(self, finding: Finding) -> str:
        """Tenta instalar dependências faltando (com cautela)."""
        # Por segurança, apenas loga - não instala automaticamente
        logger.warning(f"[AutoFixAgent] Dependency missing detected: {finding.description}")
        logger.warning("[AutoFixAgent] Auto-install disabled for safety. Run: validate-improvements.bat")
        return None


class DependencyHealthAgent(BaseAgent):
    """
    Agente que monitora e reporta status de dependências críticas.
    Detecta face_recognition, pygame, deepfilternet, etc.
    """
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "DependencyHealthAgent", check_interval=600)
        self.critical_dependencies = [
            "face_recognition",
            "pygame",
            "deepfilternet",
            "sounddevice",
            "pycaw",
            "mediapipe",
            "ultralytics"
        ]
    
    async def analyze(self) -> List[Finding]:
        findings = []
        missing = []
        available = []
        
        for dep in self.critical_dependencies:
            try:
                __import__(dep)
                available.append(dep)
            except ImportError:
                missing.append(dep)
        
        if missing:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.HIGH,
                title="Dependências Críticas Ausentes",
                description=f"{len(missing)} dependência(s) crítica(s) não instalada(s): {', '.join(missing)}",
                recommendation=f"Execute: .venv\\Scripts\\pip.exe install {' '.join(missing)}\nOu execute: scripts\\setup-venv.bat",
                metrics={
                    "missing": missing,
                    "available": available,
                    "total_critical": len(self.critical_dependencies)
                }
            ))
        else:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.INFO,
                title="Todas as Dependências Críticas Disponíveis",
                description=f"Todas as {len(self.critical_dependencies)} dependências críticas estão instaladas.",
                recommendation="Sistema pronto para uso completo.",
                metrics={
                    "available": available,
                    "total": len(self.critical_dependencies)
                }
            ))
        
        return findings


class EndpointRecoveryAgent(BaseAgent):
    """
    Agente que monitora falhas de endpoints e tenta recuperação automática.
    Detecta ECONNRESET, socket hang up, etc.
    """
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "EndpointRecoveryAgent", check_interval=30)
        self.failed_requests = []
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        try:
            import aiohttp
            
            # Testar endpoints críticos
            critical_endpoints = [
                "http://localhost:8000/health",
                "http://localhost:8000/telemetry/status",
                "http://localhost:8000/system/capabilities"
            ]
            
            for endpoint in critical_endpoints:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status != 200:
                                await self._try_endpoint_recovery(endpoint, findings)
                
                except asyncio.TimeoutError:
                    findings.append(Finding(
                        agent_type=self.agent_type,
                        severity=Severity.HIGH,
                        title=f"Endpoint Timeout: {endpoint}",
                        description=f"Endpoint {endpoint} não respondeu em 5s",
                        recommendation="Verifique se há operações bloqueantes. Considere otimizar queries.",
                        metrics={"endpoint": endpoint, "timeout": 5}
                    ))
                
                except Exception as e:
                    error_msg = str(e)
                    
                    # Detectar socket hang up / ECONNRESET
                    if "ECONNRESET" in error_msg or "socket hang up" in error_msg:
                        findings.append(Finding(
                            agent_type=self.agent_type,
                            severity=Severity.CRITICAL,
                            title=f"Socket Error: {endpoint}",
                            description=f"Conexão resetada abruptamente. Erro: {error_msg}",
                            recommendation="Verifique se há imports falhando no endpoint. Adicione try/except em cada componente.",
                            metrics={
                                "endpoint": endpoint,
                                "error": error_msg,
                                "recovery_attempted": self.recovery_attempts.get(endpoint, 0)
                            }
                        ))
                        
                        await self._try_endpoint_recovery(endpoint, findings)
        
        except ImportError:
            logger.warning("[EndpointRecoveryAgent] aiohttp not available")
        except Exception as e:
            logger.warning(f"[EndpointRecoveryAgent] Error during analysis: {e}")
        
        return findings
    
    async def _try_endpoint_recovery(self, endpoint: str, findings: List[Finding]):
        """Tenta recuperar endpoint com falha."""
        
        attempts = self.recovery_attempts.get(endpoint, 0)
        
        if attempts >= self.max_recovery_attempts:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.CRITICAL,
                title=f"Endpoint Recovery Failed: {endpoint}",
                description=f"Tentativas de recuperação excedidas ({attempts}/{self.max_recovery_attempts})",
                recommendation="Reinicie o backend manualmente. Execute: restart-jarvis.bat",
                metrics={"endpoint": endpoint, "attempts": attempts}
            ))
            return
        
        self.recovery_attempts[endpoint] = attempts + 1
        logger.warning(f"[EndpointRecoveryAgent] Recovery attempt {attempts + 1} for {endpoint}")
        
        # Aguardar um pouco antes de tentar novamente
        await asyncio.sleep(2)


class AudioSystemRepairAgent(BaseAgent):
    """
    Agente especializado em detectar e corrigir problemas de áudio.
    """
    
    def __init__(self):
        super().__init__(AgentType.SYSTEM_HEALTH, "AudioSystemRepairAgent", check_interval=180)
    
    async def analyze(self) -> List[Finding]:
        findings = []
        
        # Verificar pycaw
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            
            if devices:
                findings.append(Finding(
                    agent_type=self.agent_type,
                    severity=Severity.INFO,
                    title="Sistema de Áudio Disponível",
                    description="pycaw detectou dispositivos de áudio",
                    recommendation="Sistema de controle de volume funcional",
                    metrics={"library": "pycaw"}
                ))
        except ImportError:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.HIGH,
                title="pycaw Não Instalado",
                description="Biblioteca de controle de áudio não disponível",
                recommendation="Execute: pip install pycaw comtypes",
                metrics={"missing": ["pycaw", "comtypes"]}
            ))
        except Exception as e:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.MEDIUM,
                title="Erro ao Acessar Dispositivos de Áudio",
                description=f"Erro ao inicializar pycaw: {str(e)}",
                recommendation="Verifique se há dispositivos de áudio conectados. Reinicie o sistema se necessário.",
                metrics={"error": str(e)}
            ))
        
        # Verificar pygame
        try:
            import pygame
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.INFO,
                title="Pygame Disponível",
                description="Biblioteca pygame instalada para playback de áudio",
                recommendation="Sistema de TTS funcional",
                metrics={"library": "pygame"}
            ))
        except ImportError:
            findings.append(Finding(
                agent_type=self.agent_type,
                severity=Severity.HIGH,
                title="Pygame Não Instalado",
                description="Playback de áudio local não disponível",
                recommendation="Execute: pip install pygame",
                metrics={"missing": ["pygame"]}
            ))
        
        return findings


# Singleton para gerenciar agentes de auto-correção
_autofix_agents_registered = False


def register_autofix_agents():
    """Registra agentes de auto-correção no orquestrador."""
    global _autofix_agents_registered
    
    if _autofix_agents_registered:
        return
    
    try:
        from .multi_agent_analysis import get_orchestrator
        orchestrator = get_orchestrator()
        
        # Registrar agentes de auto-correção
        orchestrator.register_agent(AutoFixAgent())
        orchestrator.register_agent(DependencyHealthAgent())
        orchestrator.register_agent(EndpointRecoveryAgent())
        orchestrator.register_agent(AudioSystemRepairAgent())
        
        _autofix_agents_registered = True
        logger.success("[AutoFix] Auto-correction agents registered (4 additional agents)")
    
    except Exception as e:
        logger.error(f"[AutoFix] Failed to register agents: {e}")
