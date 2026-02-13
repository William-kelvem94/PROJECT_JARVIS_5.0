#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Democratic Auto-Recovery System
===================================================
Sistema de auto-recovery que funciona em rede democrÃ¡tica.
Quando um PC tem problema crÃ­tico, outros assumem suas tarefas automaticamente.
"""

import asyncio
import json
import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Imports do sistema democrÃ¡tico
from src.core.network_mesh.democratic_intelligence import (
    DemocraticNetworkIntelligence, TaskType, DeviceCapability, ElectionStatus
)

class CriticalityLevel(Enum):
    """NÃ­veis de criticidade para problemas"""
    LOW = 1        # Aviso apenas
    MEDIUM = 2     # Problema detectado
    HIGH = 3       # Problema sÃ©rio 
    CRITICAL = 4   # Falha crÃ­tica
    EMERGENCY = 5  # EmergÃªncia total

class RecoveryScope(Enum):
    """Escopo da recuperaÃ§Ã£o necessÃ¡ria"""
    LOCAL = "local"           # Resolver localmente
    PEER_ASSIST = "peer_assist"  # Pedir ajuda de um peer
    NETWORK_TAKEOVER = "network_takeover"  # Rede assume controle
    EMERGENCY_BACKUP = "emergency_backup"  # Backup total de emergÃªncia

class SystemModule(Enum):
    """MÃ³dulos crÃ­ticos do JARVIS que podem falhar"""
    AI_AGENT = "ai_agent"
    VOICE_CONTROLLER = "voice_controller"
    VISION_SYSTEM = "vision_system" 
    HARDWARE_MANAGER = "hardware_manager"
    MEMORY_SYSTEM = "memory_system"
    NETWORK_MESH = "network_mesh"
    INTERFACE = "interface"

@dataclass
class CriticalFailure:
    """Falha crÃ­tica que requer aÃ§Ã£o da rede"""
    failure_id: str
    device_id: str
    device_name: str
    module_affected: SystemModule
    criticality: CriticalityLevel
    recovery_scope: RecoveryScope
    error_details: str
    system_state: Dict[str, Any]
    occurred_at: datetime
    requires_immediate_takeover: bool
    estimated_downtime_min: int

@dataclass
class RecoveryAssignment:
    """AtribuiÃ§Ã£o de recuperaÃ§Ã£o distribuÃ­da"""
    assignment_id: str
    failure_id: str
    assigned_device_id: str
    assigned_device_name: str
    recovery_strategy: str
    modules_to_takeover: List[SystemModule] 
    priority: int
    estimated_duration_min: int
    assigned_at: datetime

class DemocraticAutoRecovery:
    """
    ðŸ›ï¸ SISTEMA DE AUTO-RECOVERY DEMOCRÃTICO
    
    Funcionalidades:
    - Monitoramento distribuÃ­do de saÃºde
    - EleiÃ§Ã£o automÃ¡tica para recovery quando PC falha
    - Takeover de mÃ³dulos crÃ­ticos por outros dispositivos
    - ConsolidaÃ§Ã£o de estado durante recovery
    - Backup automÃ¡tico de dados crÃ­ticos
    """
    
    def __init__(self, jarvis_core, democratic_network: DemocraticNetworkIntelligence):
        self.jarvis_core = jarvis_core
        self.democratic_network = democratic_network
        self.config_path = Path(jarvis_core.config['system']['base_path']) / "data" / "democratic_recovery"
        self.config_path.mkdir(parents=True, exist_ok=True) 
        
        # Estado do sistema
        self.is_monitoring = False
        self.critical_failures: Dict[str, CriticalFailure] = {}
        self.active_assignments: Dict[str, RecoveryAssignment] = {}
        self.takeover_modules: Set[SystemModule] = set()  # MÃ³dulos que assumimos de outros PCs
        
        # ConfiguraÃ§Ãµes de recovery
        self.health_check_interval = 15  # segundos
        self.failure_threshold = 3  # falhas consecutivas para considerar crÃ­tico
        self.emergency_threshold = 300  # 5 minutos sem heartbeat = emergÃªncia
        
        # Estado de outros dispositivos (heartbeat)  
        self.peer_heartbeats: Dict[str, datetime] = {}
        self.peer_failures: Dict[str, int] = {}  # contador de falhas consecutivas
        
        # Threading
        self.monitor_thread = None
        self.network_monitor_thread = None
        self.stop_event = threading.Event()
        
        # Callbacks para integraÃ§Ã£o
        self.on_module_takeover: Optional[callable] = None
        self.on_module_restore: Optional[callable] = None
        
        print("ðŸ›ï¸ Democratic Auto-Recovery inicializado")
    
    def start_monitoring(self):
        """ðŸš€ INICIA MONITORAMENTO DEMOCRÃTICO"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.stop_event.clear()
        
        # Thread para monitoramento local
        self.monitor_thread = threading.Thread(target=self._local_monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Thread para monitoramento da rede
        self.network_monitor_thread = threading.Thread(target=self._network_monitoring_loop, daemon=True)
        self.network_monitor_thread.start()
        
        print("ðŸ‘ï¸ Democratic Auto-Recovery: Monitoramento ativado")
    
    def stop_monitoring(self):
        """â¹ï¸ PARA MONITORAMENTO"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.stop_event.set()
        
        for thread in [self.monitor_thread, self.network_monitor_thread]:
            if thread and thread.is_alive():
                thread.join(timeout=5)
        
        print("ðŸ›‘ Democratic Auto-Recovery: Monitoramento parado")
    
    def _local_monitoring_loop(self):
        """ðŸ“Š LOOP DE MONITORAMENTO LOCAL"""
        consecutive_failures = 0
        
        while not self.stop_event.wait(self.health_check_interval):
            try:
                # Verificar saÃºde local
                health_issues = self._check_local_health()
                
                if health_issues:
                    consecutive_failures += 1
                    print(f"âš ï¸ Problemas detectados ({consecutive_failures}/{self.failure_threshold}): {health_issues}")
                    
                    # Se atingiu threshold, considerar crÃ­tico
                    if consecutive_failures >= self.failure_threshold:
                        await asyncio.run(self._handle_critical_local_failure(health_issues))
                        consecutive_failures = 0  # Reset apÃ³s tratar
                else:
                    consecutive_failures = 0  # Reset se tudo ok
                
                # Enviar heartbeat para rede
                await asyncio.run(self._send_health_heartbeat())
                
            except Exception as e:
                print(f"âŒ Erro no monitoramento local: {e}")
                consecutive_failures += 1
    
    def _network_monitoring_loop(self):
        """ðŸŒ LOOP DE MONITORAMENTO DA REDE"""
        while not self.stop_event.wait(10):  # Check a cada 10s
            try:
                # Verificar heartbeats de outros dispositivos
                now = datetime.now()
                
                for device_id, last_heartbeat in list(self.peer_heartbeats.items()):
                    time_since_heartbeat = now - last_heartbeat
                    
                    if time_since_heartbeat.total_seconds() > self.emergency_threshold:
                        # Dispositivo pode ter falhado completamente
                        asyncio.run(self._handle_peer_emergency_failure(device_id))
                    elif time_since_heartbeat.total_seconds() > 60:  # 1 minuto sem heartbeat
                        # Incrementar contador de falhas suspeitas
                        self.peer_failures[device_id] = self.peer_failures.get(device_id, 0) + 1
                        
                        if self.peer_failures[device_id] >= 3:  # 3 minutos consecutivos
                            asyncio.run(self._handle_peer_suspected_failure(device_id))
                
            except Exception as e:
                print(f"âŒ Erro no monitoramento de rede: {e}")
    
    def _check_local_health(self) -> List[str]:
        """ðŸ” VERIFICA SAÃšDE LOCAL DO SISTEMA"""
        issues = []
        
        try:
            # 1. VERIFICAR MEMÃ“RIA
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                issues.append(f"MemÃ³ria crÃ­tica: {memory.percent:.1f}%")
            
            # 2. VERIFICAR CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                issues.append(f"CPU sobrecarregado: {cpu_percent:.1f}%")
            
            # 3. VERIFICAR DISCO
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                issues.append(f"Disco cheio: {disk.percent:.1f}%")
            
            # 4. VERIFICAR MÃ“DULOS DO JARVIS
            jarvis_issues = self._check_jarvis_modules_health()
            issues.extend(jarvis_issues)
            
            return issues
            
        except Exception as e:
            return [f"Erro ao verificar saÃºde: {e}"]
    
    def _check_jarvis_modules_health(self) -> List[str]:
        """ðŸ¤– VERIFICA SAÃšDE DOS MÃ“DULOS DO JARVIS"""
        issues = []
        
        try:
            # AI Agent
            if hasattr(self.jarvis_core, 'ai_agent') and self.jarvis_core.ai_agent:
                if not self._test_module_responsiveness('ai_agent'):
                    issues.append("AI Agent nÃ£o responsivo")
            
            # Voice Controller  
            if hasattr(self.jarvis_core, 'voice_controller') and self.jarvis_core.voice_controller:
                if not self._test_module_responsiveness('voice_controller'):
                    issues.append("Voice Controller nÃ£o responsivo")
            
            # Vision System
            if hasattr(self.jarvis_core, 'vision_system') and self.jarvis_core.vision_system:
                if not self._test_module_responsiveness('vision_system'):
                    issues.append("Vision System nÃ£o responsivo")
            
            # Hardware Manager
            if hasattr(self.jarvis_core, 'hardware_manager') and self.jarvis_core.hardware_manager:
                if not self._test_module_responsiveness('hardware_manager'):
                    issues.append("Hardware Manager nÃ£o responsivo")
            
            return issues
            
        except Exception as e:
            return [f"Erro verificando mÃ³dulos JARVIS: {e}"]
    
    def _test_module_responsiveness(self, module_name: str) -> bool:
        """ðŸ§ª TESTA SE MÃ“DULO ESTÃ RESPONSIVO"""
        try:
            module = getattr(self.jarvis_core, module_name)
            
            # Teste bÃ¡sico de responsividade
            if hasattr(module, 'is_ready'):
                return module.is_ready()
            elif hasattr(module, 'health_check'):
                return module.health_check()
            else:
                return module is not None  # Se existe, assumir que estÃ¡ ok
                
        except Exception:
            return False
    
    async def _handle_critical_local_failure(self, issues: List[str]):
        """ðŸš¨ TRATA FALHA CRÃTICA LOCAL"""
        
        failure = CriticalFailure(
            failure_id=f"local_{int(time.time())}",
            device_id=self.democratic_network.device_id,
            device_name=self.democratic_network.local_specs.__dict__.get('device_name', 'local'),
            module_affected=self._determine_affected_module(issues),
            criticality=CriticalityLevel.CRITICAL,
            recovery_scope=self._determine_recovery_scope(issues),
            error_details='; '.join(issues),
            system_state=self._capture_system_state(),
            occurred_at=datetime.now(),
            requires_immediate_takeover=self._requires_immediate_takeover(issues),
            estimated_downtime_min=self._estimate_downtime(issues)
        )
        
        self.critical_failures[failure.failure_id] = failure
        
        print(f"\nðŸš¨ FALHA CRÃTICA LOCAL DETECTADA:")
        print(f"   ðŸŽ¯ MÃ³dulo: {failure.module_affected.value}")
        print(f"   âš ï¸ Criticidade: {failure.criticality.value}")
        print(f"   ðŸ”§ Escopo: {failure.recovery_scope.value}")
        print(f"   ðŸ’¥ Detalhes: {failure.error_details}")
        
        # Solicitar ajuda da rede democrÃ¡tica se necessÃ¡rio
        if failure.recovery_scope in [RecoveryScope.PEER_ASSIST, RecoveryScope.NETWORK_TAKEOVER]:
            await self._request_democratic_recovery(failure)
        else:
            # Tentar recovery local
            await self._attempt_local_recovery(failure)
    
    async def _handle_peer_emergency_failure(self, failed_device_id: str):
        """âš°ï¸ TRATA FALHA TOTAL DE DISPOSITIVO PEER"""
        
        print(f"\nâš°ï¸ EMERGÃŠNCIA: Dispositivo {failed_device_id} nÃ£o responde hÃ¡ {self.emergency_threshold}s")
        
        # Se estamos em uma rede democrÃ¡tica, participar da eleiÃ§Ã£o para assumir mÃ³dulos Ã³rfÃ£os
        if self.democratic_network.is_running:
            await self._volunteer_for_emergency_takeover(failed_device_id)
    
    async def _handle_peer_suspected_failure(self, suspected_device_id: str):
        """ðŸ¤” TRATA SUSPEITA DE FALHA DE DISPOSITIVO PEER"""
        
        print(f"ðŸ¤” Suspeita de falha: Dispositivo {suspected_device_id} com heartbeat irregular")
        
        # Tentar comunicaÃ§Ã£o direta para confirmar
        is_responsive = await self._ping_device_directly(suspected_device_id)
        
        if not is_responsive:
            print(f"ðŸ“‰ Confirmado: Dispositivo {suspected_device_id} nÃ£o responsivo")
            # Escalonar para emergÃªncia se confirmar
            await self._handle_peer_emergency_failure(suspected_device_id)
        else:
            # Reset contador de falhas se respondeu
            self.peer_failures[suspected_device_id] = 0
    
    async def _request_democratic_recovery(self, failure: CriticalFailure):
        """ðŸ—³ï¸ SOLICITA RECOVERY DEMOCRÃTICO PARA FALHA"""
        
        print(f"ðŸ—³ï¸ Solicitando recovery democrÃ¡tico para falha: {failure.failure_id}")
        
        # Determinar tipo de tarefa baseado na falha
        task_type = self._failure_to_task_type(failure.module_affected)
        
        # Solicitar tarefa distribuÃ­da para recovery
        task_id = await self.democratic_network.request_distributed_task(
            task_type=task_type,
            duration_min=failure.estimated_downtime_min,
            priority=10,  # MÃ¡xima prioridade para recovery
            data_size_mb=100.0,
            can_be_distributed=True,
            min_devices=1
        )
        
        # Aguardar eleiÃ§Ã£o e recovery
        await self._monitor_recovery_progress(failure.failure_id, task_id)
    
    def _failure_to_task_type(self, module: SystemModule) -> TaskType:
        """ðŸ”„ MAPEIA MÃ“DULO FALHADO PARA TIPO DE TAREFA"""
        
        mapping = {
            SystemModule.AI_AGENT: TaskType.HEAVY_INFERENCE,
            SystemModule.VOICE_CONTROLLER: TaskType.VOICE_TRAINING,
            SystemModule.VISION_SYSTEM: TaskType.DATA_PROCESSING,
            SystemModule.MEMORY_SYSTEM: TaskType.MEMORY_CONSOLIDATION,
            SystemModule.HARDWARE_MANAGER: TaskType.DATA_PROCESSING
        }
        
        return mapping.get(module, TaskType.DATA_PROCESSING)
    
    async def _volunteer_for_emergency_takeover(self, failed_device_id: str):
        """ðŸ™‹â€â™‚ï¸ SE VOLUNTARIA PARA ASSUMIR MÃ“DULOS Ã“RFÃƒOS"""
        
        print(f"ðŸ™‹â€â™‚ï¸ Voluntariando para assumir mÃ³dulos Ã³rfÃ£os de {failed_device_id}")
        
        # Avaliar nossa capacidade atual
        current_specs = self.democratic_network._analyze_local_specs()
        
        # Se temos capacidade boa, nos voluntariar
        if (current_specs.current_load < 0.7 and  # CPU < 70%
            current_specs.available_ram_gb > 4.0 and  # RAM > 4GB livre
            current_specs.power_state == "ac_power"):  # Conectado na tomada
            
            # Criar assignment para nÃ³s mesmos
            assignment = RecoveryAssignment(
                assignment_id=f"takeover_{int(time.time())}",
                failure_id=f"emergency_{failed_device_id}",
                assigned_device_id=self.democratic_network.device_id,
                assigned_device_name=self.democratic_network.local_specs.__dict__.get('device_name', 'local'),
                recovery_strategy="emergency_takeover",
                modules_to_takeover=[SystemModule.AI_AGENT, SystemModule.VOICE_CONTROLLER],  # MÃ³dulos crÃ­ticos
                priority=10,
                estimated_duration_min=60,  # Assumir por 1 hora inicialmente
                assigned_at=datetime.now()
            )
            
            self.active_assignments[assignment.assignment_id] = assignment
            
            # Executar takeover
            await self._execute_module_takeover(assignment)
        else:
            print(f"   ðŸ“‰ Capacidade insuficiente para takeover no momento")
    
    async def _execute_module_takeover(self, assignment: RecoveryAssignment):
        """ðŸ”€ EXECUTA TAKEOVER DE MÃ“DULOS"""
        
        print(f"ðŸ”€ Executando takeover de mÃ³dulos:")
        
        for module in assignment.modules_to_takeover:
            try:
                success = await self._takeover_module(module)
                if success:
                    self.takeover_modules.add(module)
                    print(f"   âœ… {module.value} assumido com sucesso")
                else:
                    print(f"   âŒ Falha ao assumir {module.value}")
                    
            except Exception as e:
                print(f"   âŒ Erro assumindo {module.value}: {e}")
        
        # Notificar callback se definido
        if self.on_module_takeover:
            self.on_module_takeover(assignment.modules_to_takeover)
    
    async def _takeover_module(self, module: SystemModule) -> bool:
        """ðŸŽ¯ ASSUME CONTROLE DE UM MÃ“DULO ESPECÃFICO"""
        
        if module == SystemModule.AI_AGENT:
            # Aumentar capacidade de inferÃªncia para compensar
            if hasattr(self.jarvis_core, 'ai_agent'):
                # Configurar para modo high-availability
                return True
                
        elif module == SystemModule.VOICE_CONTROLLER:
            # Assumir processamento de voz adicional
            if hasattr(self.jarvis_core, 'voice_controller'):
                # Configurar para processar mÃºltiplas streams
                return True
                
        elif module == SystemModule.VISION_SYSTEM:
            # Assumir processamento de visÃ£o adicional
            if hasattr(self.jarvis_core, 'vision_system'):
                return True
        
        return False
    
    # ===== MÃ‰TODOS DE UTILIDADE =====
    
    def _determine_affected_module(self, issues: List[str]) -> SystemModule:
        """ðŸ“ DETERMINA MÃ“DULO MAIS AFETADO"""
        # LÃ³gica simplificada
        for issue in issues:
            if 'ai' in issue.lower() or 'agent' in issue.lower():
                return SystemModule.AI_AGENT
            elif 'voice' in issue.lower():
                return SystemModule.VOICE_CONTROLLER
            elif 'vision' in issue.lower() or 'camera' in issue.lower():
                return SystemModule.VISION_SYSTEM
            elif 'hardware' in issue.lower():
                return SystemModule.HARDWARE_MANAGER
        
        return SystemModule.AI_AGENT  # Default
    
    def _determine_recovery_scope(self, issues: List[str]) -> RecoveryScope:
        """ðŸŽ¯ DETERMINA ESCOPO NECESSÃRIO DE RECOVERY"""
        critical_count = len([issue for issue in issues if 'crÃ­tico' in issue.lower()])
        
        if critical_count >= 3:
            return RecoveryScope.NETWORK_TAKEOVER
        elif critical_count >= 2:
            return RecoveryScope.PEER_ASSIST
        else:
            return RecoveryScope.LOCAL
    
    def _requires_immediate_takeover(self, issues: List[str]) -> bool:
        """âš¡ VERIFICA SE REQUER TAKEOVER IMEDIATO"""
        critical_keywords = ['nÃ£o responsivo', 'crÃ­tica', 'emergÃªncia', 'falhou completamente']
        return any(keyword in ' '.join(issues).lower() for keyword in critical_keywords)
    
    def _estimate_downtime(self, issues: List[str]) -> int:
        """â±ï¸ ESTIMA TEMPO DE DOWNTIME EM MINUTOS"""
        if len(issues) >= 3:
            return 30  # Problemas mÃºltiplos = 30 min
        elif len(issues) >= 2:
            return 15  # Problemas mÃ©dios = 15 min
        else:
            return 5   # Problema simples = 5 min
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """ðŸ“¸ CAPTURA ESTADO ATUAL DO SISTEMA"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat(),
            'active_takeovers': len(self.takeover_modules)
        }
    
    # ===== MÃ‰TODOS PLACEHOLDER =====
    
    async def _send_health_heartbeat(self):
        """ðŸ’“ Envia heartbeat de saÃºde"""
        pass
    
    async def _attempt_local_recovery(self, failure: CriticalFailure):
        """ðŸ”§ Tenta recovery local"""
        pass
    
    async def _ping_device_directly(self, device_id: str) -> bool:
        """ðŸ“¡ Ping direto para dispositivo"""
        return False  # Implementar ping real
    
    async def _monitor_recovery_progress(self, failure_id: str, task_id: str):
        """ðŸ“Š Monitora progresso do recovery"""
        pass
    
    # ===== MÃ‰TODOS PÃšBLICOS =====
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """ðŸ“Š RETORNA STATUS DO RECOVERY DEMOCRÃTICO"""
        return {
            'monitoring_active': self.is_monitoring,
            'critical_failures': len(self.critical_failures),
            'active_assignments': len(self.active_assignments),
            'takeover_modules': [mod.value for mod in self.takeover_modules],
            'peer_devices_monitored': len(self.peer_heartbeats),
            'network_connected': self.democratic_network.is_running if self.democratic_network else False
        }

# ===== INTEGRAÃ‡ÃƒO COM JARVIS CORE =====

class DemocraticRecoveryIntegration:
    """ðŸ”— INTEGRAÃ‡ÃƒO PARA USAR NO JARVIS CORE"""
    
    def __init__(self, jarvis_core):
        self.jarvis_core = jarvis_core
        self.democratic_network = None
        self.auto_recovery = None
    
    async def initialize(self, target_account: str = "williamkelvem64@gmail.com"):
        """ðŸš€ INICIALIZA SISTEMA DEMOCRÃTICO COMPLETO"""
        
        print("ðŸ›ï¸ Inicializando sistema democrÃ¡tico...")
        
        # Inicializar rede democrÃ¡tica
        self.democratic_network = DemocraticNetworkIntelligence(
            str(Path(self.jarvis_core.config['system']['base_path'])),
            target_account
        )
        
        if not self.democratic_network.is_authorized:
            print("âŒ Dispositivo nÃ£o autorizado para rede democrÃ¡tica")
            return False
        
        # Inicializar auto-recovery democrÃ¡tico
        self.auto_recovery = DemocraticAutoRecovery(self.jarvis_core, self.democratic_network)
        
        # Iniciar sistemas
        await self.democratic_network.start_democratic_network()
        self.auto_recovery.start_monitoring()
        
        print("âœ… Sistema democrÃ¡tico ativo")
        return True
    
    async def shutdown(self):
        """â¹ï¸ PARA SISTEMA DEMOCRÃTICO"""
        print("ðŸ›‘ Parando sistema democrÃ¡tico...")
        
        if self.auto_recovery:
            self.auto_recovery.stop_monitoring()
        
        if self.democratic_network:
            await self.democratic_network.stop_democratic_network()
        
        print("âœ… Sistema democrÃ¡tico parado")
    
    def get_status(self) -> Dict[str, Any]:
        """ðŸ“Š STATUS COMPLETO DO SISTEMA DEMOCRÃTICO"""
        status = {
            'democratic_network': None,
            'auto_recovery': None
        }
        
        if self.democratic_network:
            status['democratic_network'] = self.democratic_network.get_network_status()
        
        if self.auto_recovery:
            status['auto_recovery'] = self.auto_recovery.get_recovery_status()
        
        return status

# Para uso no jarvis_core.py:
# self.democratic_system = DemocraticRecoveryIntegration(self)
# await self.democratic_system.initialize("williamkelvem64@gmail.com")
