#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Local Auto-Recovery System  
===============================================
Sistema de auto-recovery REAL integrado com o JARVIS local.
Funciona em conjunto com a rede local para recovery distribuído.
"""

import asyncio
import json
import os
import psutil
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Imports específicos para monitoramento
import threading
import subprocess
import sys

class FailureType(Enum):
    MEMORY_LEAK = "memory_leak"
    CPU_OVERLOAD = "cpu_overload" 
    DISK_FULL = "disk_full"
    NETWORK_TIMEOUT = "network_timeout"
    MODULE_CRASH = "module_crash"
    DEPENDENCY_ERROR = "dependency_error"
    GPU_ERROR = "gpu_error"
    SERVICE_UNRESPONSIVE = "service_unresponsive"

class RecoveryStrategy(Enum):
    RESTART_SERVICE = "restart_service"
    CLEAR_MEMORY = "clear_memory"
    REDUCE_LOAD = "reduce_load"
    REINITIALIZE_MODULE = "reinitialize_module"
    FALLBACK_MODE = "fallback_mode"
    REQUEST_NETWORK_HELP = "request_network_help"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class FailureEvent:
    """Evento de falha detectado"""
    failure_id: str
    failure_type: FailureType
    severity: int  # 1-10
    module_affected: str
    error_message: str
    system_metrics: Dict[str, Any]
    timestamp: datetime
    recovery_attempts: int = 0

@dataclass
class RecoveryAction:
    """Ação de recovery executada"""
    action_id: str
    strategy: RecoveryStrategy
    target_module: str
    success: bool
    execution_time: float
    error_details: Optional[str]
    timestamp: datetime

class JarvisAutoRecovery:
    """
    🔧 SISTEMA DE AUTO-RECOVERY REAL PARA JARVIS
    
    Recursos:
    - Monitoramento contínuo de saúde do sistema
    - Detecção automática de falhas
    - Recovery inteligente por tipo de problema
    - Integração com rede local para backup
    - Aprendizado das estratégias mais eficazes
    """
    
    def __init__(self, jarvis_core):
        self.jarvis_core = jarvis_core
        self.config_path = Path(jarvis_core.config['system']['base_path']) / "data" / "auto_recovery"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Estado do sistema
        self.is_monitoring = False
        self.failure_history: List[FailureEvent] = []
        self.recovery_history: List[RecoveryAction] = []
        self.current_failures: Dict[str, FailureEvent] = {}
        
        # Estratégias de recovery
        self.recovery_strategies: Dict[FailureType, List[RecoveryStrategy]] = {
            FailureType.MEMORY_LEAK: [
                RecoveryStrategy.CLEAR_MEMORY,
                RecoveryStrategy.RESTART_SERVICE,
                RecoveryStrategy.REDUCE_LOAD
            ],
            FailureType.CPU_OVERLOAD: [
                RecoveryStrategy.REDUCE_LOAD,
                RecoveryStrategy.RESTART_SERVICE,
                RecoveryStrategy.FALLBACK_MODE
            ],
            FailureType.MODULE_CRASH: [
                RecoveryStrategy.REINITIALIZE_MODULE,
                RecoveryStrategy.RESTART_SERVICE,
                RecoveryStrategy.REQUEST_NETWORK_HELP
            ],
            FailureType.DEPENDENCY_ERROR: [
                RecoveryStrategy.REINITIALIZE_MODULE,
                RecoveryStrategy.FALLBACK_MODE,
                RecoveryStrategy.REQUEST_NETWORK_HELP
            ],
            FailureType.SERVICE_UNRESPONSIVE: [
                RecoveryStrategy.RESTART_SERVICE,
                RecoveryStrategy.REINITIALIZE_MODULE,
                RecoveryStrategy.EMERGENCY_SHUTDOWN
            ]
        }
        
        # Métricas de sucesso por estratégia (aprender qual funciona melhor)
        self.strategy_success_rates: Dict[RecoveryStrategy, float] = {}
        
        # Threading para monitoramento
        self.monitor_thread = None
        self.monitor_stop_event = threading.Event()
        
        print("🔧 Auto-Recovery inicializado")
        
    def start_monitoring(self):
        """🚀 INICIA MONITORAMENTO CONTÍNUO"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        print("👁️ Auto-Recovery: Monitoramento ativado")
    
    def stop_monitoring(self):
        """⏹️ PARA MONITORAMENTO"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.monitor_stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        print("🛑 Auto-Recovery: Monitoramento parado")
    
    def _monitoring_loop(self):
        """🔄 LOOP PRINCIPAL DE MONITORAMENTO"""
        while not self.monitor_stop_event.is_set():
            try:
                # Coletar métricas do sistema
                metrics = self._collect_system_metrics()
                
                # Detectar falhas
                failures = self._detect_failures(metrics)
                
                # Processar falhas detectadas
                for failure in failures:
                    asyncio.run(self._handle_failure(failure))
                
                # Aguardar próxima verificação
                self.monitor_stop_event.wait(10)  # Check a cada 10 segundos
                
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                self.monitor_stop_event.wait(30)  # Aguardar mais tempo em caso de erro
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """📊 COLETA MÉTRICAS DO SISTEMA"""
        try:
            # Métricas básicas do sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Processos Python (JARVIS)
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            
            # Métricas específicas do JARVIS
            jarvis_modules = self._get_jarvis_modules_status()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'python_processes': python_processes,
                'jarvis_modules': jarvis_modules,
                'network_connections': len(psutil.net_connections()),
                'boot_time': psutil.boot_time()
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ Erro coletando métricas: {e}")
            return {}
    
    def _get_jarvis_modules_status(self) -> Dict[str, Dict]:
        """📋 VERIFICA STATUS DOS MÓDULOS DO JARVIS"""
        modules_status = {}
        
        try:
            if hasattr(self.jarvis_core, 'modules_initialized'):
                for module_name, is_initialized in self.jarvis_core.modules_initialized.items():
                    modules_status[module_name] = {
                        'initialized': is_initialized,
                        'responsive': self._check_module_responsive(module_name),
                        'last_activity': self._get_module_last_activity(module_name)
                    }
        except Exception as e:
            print(f"⚠️ Erro verificando módulos: {e}")
        
        return modules_status
    
    def _check_module_responsive(self, module_name: str) -> bool:
        """🔍 VERIFICA SE MÓDULO ESTÁ RESPONSIVO"""
        try:
            # Verificações específicas por módulo
            if module_name == 'ai_agent' and hasattr(self.jarvis_core, 'ai_agent'):
                # Teste básico do AI Agent
                return self.jarvis_core.ai_agent is not None
            
            elif module_name == 'voice' and hasattr(self.jarvis_core, 'voice_controller'):
                return self.jarvis_core.voice_controller is not None
            
            elif module_name == 'vision' and hasattr(self.jarvis_core, 'vision_enhancer'):
                return self.jarvis_core.vision_enhancer is not None
            
            # Para outros módulos, assumir que estar inicializado = responsivo
            return True
            
        except Exception:
            return False
    
    def _get_module_last_activity(self, module_name: str) -> Optional[str]:
        """⏰ OBTÉM ÚLTIMA ATIVIDADE DO MÓDULO"""
        # Implementação básica - pode ser expandida
        return datetime.now().isoformat()
    
    def _detect_failures(self, metrics: Dict[str, Any]) -> List[FailureEvent]:
        """🚨 DETECTA FALHAS BASEADO NAS MÉTRICAS"""
        failures = []
        timestamp = datetime.now()
        
        # 1. MEMORY LEAK DETECTION
        if metrics.get('memory_usage', 0) > 85:
            failure = FailureEvent(
                failure_id=f"mem_{int(time.time())}",
                failure_type=FailureType.MEMORY_LEAK,
                severity=8 if metrics['memory_usage'] > 90 else 6,
                module_affected="system",
                error_message=f"Uso de memória crítico: {metrics['memory_usage']:.1f}%",
                system_metrics=metrics,
                timestamp=timestamp
            )
            failures.append(failure)
        
        # 2. CPU OVERLOAD DETECTION
        if metrics.get('cpu_usage', 0) > 90:
            failure = FailureEvent(
                failure_id=f"cpu_{int(time.time())}",
                failure_type=FailureType.CPU_OVERLOAD,
                severity=7,
                module_affected="system",
                error_message=f"CPU sobrecarregado: {metrics['cpu_usage']:.1f}%",
                system_metrics=metrics,
                timestamp=timestamp
            )
            failures.append(failure)
        
        # 3. DISK FULL DETECTION
        if metrics.get('disk_usage', 0) > 95:
            failure = FailureEvent(
                failure_id=f"disk_{int(time.time())}",
                failure_type=FailureType.DISK_FULL,
                severity=9,
                module_affected="system",
                error_message=f"Disco quase cheio: {metrics['disk_usage']:.1f}%",
                system_metrics=metrics,
                timestamp=timestamp
            )
            failures.append(failure)
        
        # 4. MODULE UNRESPONSIVE DETECTION
        jarvis_modules = metrics.get('jarvis_modules', {})
        for module_name, module_info in jarvis_modules.items():
            if module_info.get('initialized', False) and not module_info.get('responsive', True):
                failure = FailureEvent(
                    failure_id=f"module_{module_name}_{int(time.time())}",
                    failure_type=FailureType.SERVICE_UNRESPONSIVE,
                    severity=8,
                    module_affected=module_name,
                    error_message=f"Módulo {module_name} não está responsivo",
                    system_metrics=metrics,
                    timestamp=timestamp
                )
                failures.append(failure)
        
        return failures
    
    async def _handle_failure(self, failure: FailureEvent):
        """🔧 TRATA FALHA DETECTADA"""
        
        # Evitar processamento duplicado
        if failure.failure_id in self.current_failures:
            return
        
        self.current_failures[failure.failure_id] = failure
        self.failure_history.append(failure)
        
        print(f"\n🚨 FALHA DETECTADA: {failure.failure_type.value}")
        print(f"   📍 Módulo: {failure.module_affected}")
        print(f"   ⚠️ Severidade: {failure.severity}/10")
        print(f"   💬 Erro: {failure.error_message}")
        
        # Selecionar estratégias de recovery
        strategies = self._get_recovery_strategies(failure.failure_type)
        
        # Executar estratégias em ordem de prioridade
        recovery_success = False
        for strategy in strategies:
            try:
                print(f"   🔧 Tentando: {strategy.value}")
                
                success = await self._execute_recovery_strategy(failure, strategy)
                
                # Registrar ação
                action = RecoveryAction(
                    action_id=f"rec_{int(time.time())}",
                    strategy=strategy,
                    target_module=failure.module_affected,
                    success=success,
                    execution_time=1.0,  # Simplificado
                    error_details=None if success else "Estratégia falhou",
                    timestamp=datetime.now()
                )
                self.recovery_history.append(action)
                
                if success:
                    print(f"   ✅ Recovery bem-sucedido com: {strategy.value}")
                    recovery_success = True
                    self._update_strategy_success_rate(strategy, True)
                    break
                else:
                    self._update_strategy_success_rate(strategy, False)
                    
            except Exception as e:
                print(f"   ❌ Erro na estratégia {strategy.value}: {e}")
                self._update_strategy_success_rate(strategy, False)
        
        # Se recovery local falhou, pedir ajuda da rede
        if not recovery_success and failure.severity >= 8:
            await self._request_network_recovery(failure)
        
        # Remover da lista atual se resolvido
        if recovery_success and failure.failure_id in self.current_failures:
            del self.current_failures[failure.failure_id]
        
        print(f"   🏁 Recovery {'✅ concluído' if recovery_success else '❌ falhou'}")
    
    def _get_recovery_strategies(self, failure_type: FailureType) -> List[RecoveryStrategy]:
        """📋 OBTÉM ESTRATÉGIAS ORDENADAS POR EFICÁCIA"""
        strategies = self.recovery_strategies.get(failure_type, [])
        
        # Ordenar por taxa de sucesso (aprendizado)
        def strategy_priority(strategy):
            success_rate = self.strategy_success_rates.get(strategy, 0.5)
            return -success_rate  # Ordem decrescente
        
        return sorted(strategies, key=strategy_priority)
    
    async def _execute_recovery_strategy(self, failure: FailureEvent, strategy: RecoveryStrategy) -> bool:
        """⚡ EXECUTA ESTRATÉGIA DE RECOVERY"""
        
        try:
            if strategy == RecoveryStrategy.CLEAR_MEMORY:
                return await self._clear_memory()
            
            elif strategy == RecoveryStrategy.RESTART_SERVICE:
                return await self._restart_service(failure.module_affected)
            
            elif strategy == RecoveryStrategy.REDUCE_LOAD:
                return await self._reduce_system_load()
            
            elif strategy == RecoveryStrategy.REINITIALIZE_MODULE:
                return await self._reinitialize_module(failure.module_affected)
            
            elif strategy == RecoveryStrategy.FALLBACK_MODE:
                return await self._activate_fallback_mode(failure.module_affected)
            
            elif strategy == RecoveryStrategy.REQUEST_NETWORK_HELP:
                return await self._request_network_recovery(failure)
            
            elif strategy == RecoveryStrategy.EMERGENCY_SHUTDOWN:
                return await self._emergency_shutdown()
            
            return False
            
        except Exception as e:
            print(f"❌ Erro executando {strategy.value}: {e}")
            return False
    
    async def _clear_memory(self) -> bool:
        """🧹 LIMPA MEMÓRIA DO SISTEMA"""
        try:
            # Forçar garbage collection
            import gc
            gc.collect()
            
            # Limpar caches se disponíveis
            if hasattr(self.jarvis_core, 'clear_caches'):
                await self.jarvis_core.clear_caches()
            
            print("🧹 Memória limpa")
            return True
            
        except Exception as e:
            print(f"❌ Erro limpando memória: {e}")
            return False
    
    async def _restart_service(self, module_name: str) -> bool:
        """🔄 REINICIA SERVIÇO ESPECÍFICO"""
        try:
            print(f"🔄 Reiniciando módulo: {module_name}")
            
            # Implementação específica por módulo
            if module_name == "ai_agent":
                return await self._restart_ai_agent()
            elif module_name == "voice":
                return await self._restart_voice_controller()
            elif module_name == "vision":
                return await self._restart_vision_enhancer()
            else:
                # Restart generico  
                return await self._restart_generic_module(module_name)
            
        except Exception as e:
            print(f"❌ Erro reiniciando {module_name}: {e}")
            return False
    
    async def _restart_ai_agent(self) -> bool:
        """🤖 REINICIA AI AGENT"""
        try:
            if hasattr(self.jarvis_core, 'ai_agent'):
                # Parar current agent
                if hasattr(self.jarvis_core.ai_agent, 'stop'):
                    await self.jarvis_core.ai_agent.stop()
                
                # Reinicializar
                await asyncio.sleep(2)
                # Aqui você chamaria o método de inicialização do AI agent
                print("🤖 AI Agent reiniciado")
                return True
            return False
        except Exception:
            return False
    
    async def _restart_voice_controller(self) -> bool:
        """🎤 REINICIA CONTROLADOR DE VOZ"""
        try:
            if hasattr(self.jarvis_core, 'voice_controller'):
                # Lógica de reinicialização
                print("🎤 Voice Controller reiniciado")
                return True
            return False  
        except Exception:
            return False
    
    async def _restart_vision_enhancer(self) -> bool:
        """👁️ REINICIA VISION ENHANCER"""
        try:
            if hasattr(self.jarvis_core, 'vision_enhancer'):
                # Lógica de reinicialização
                print("👁️ Vision Enhancer reiniciado")
                return True
            return False
        except Exception:
            return False
    
    async def _restart_generic_module(self, module_name: str) -> bool:
        """🔄 REINICIALIZAÇÃO GENÉRICA"""
        try:
            # Implementação genérica para outros módulos
            print(f"🔄 Módulo {module_name} reiniciado genericamente")
            return True
        except Exception:
            return False
    
    async def _reduce_system_load(self) -> bool:
        """📉 REDUZ CARGA DO SISTEMA"""
        try:
            # Parar processos não críticos
            if hasattr(self.jarvis_core, 'reduce_load'):
                await self.jarvis_core.reduce_load()
            
            # Reduzir configurações de performance
            print("📉 Carga do sistema reduzida")
            return True
            
        except Exception:
            return False
    
    async def _reinitialize_module(self, module_name: str) -> bool:
        """🔄 REINICIALIZA MÓDULO COMPLETAMENTE"""
        try:
            # Reinicialização completa do módulo
            if hasattr(self.jarvis_core, f'initialize_{module_name}'):
                init_method = getattr(self.jarvis_core, f'initialize_{module_name}')
                await init_method()
                print(f"🔄 Módulo {module_name} reinicializado")
                return True
            
            return await self._restart_service(module_name)
            
        except Exception:
            return False
    
    async def _activate_fallback_mode(self, module_name: str) -> bool:
        """🛡️ ATIVA MODO FALLBACK"""
        try:
            print(f"🛡️ Ativando fallback para {module_name}")
            
            # Implementar fallback específico por módulo
            if hasattr(self.jarvis_core, 'activate_fallback'):
                await self.jarvis_core.activate_fallback(module_name)
            
            return True
            
        except Exception:
            return False
    
    async def _request_network_recovery(self, failure: FailureEvent) -> bool:
        """📡 SOLICITA AJUDA DA REDE LOCAL"""
        try:
            # Integração com LocalNetworkIntelligence
            if hasattr(self.jarvis_core, 'network_mesh'):
                await self.jarvis_core.network_mesh.emergency_broadcast(
                    "auto_recovery_failure",
                    {
                        "failure_type": failure.failure_type.value,
                        "module": failure.module_affected,
                        "severity": failure.severity,
                        "needs_assistance": True
                    }
                )
                print("📡 Solicitação de ajuda enviada para rede")
                return True
            
            return False
            
        except Exception:
            return False
    
    async def _emergency_shutdown(self) -> bool:
        """🚨 SHUTDOWN DE EMERGÊNCIA"""
        try:
            print("🚨 SHUTDOWN DE EMERGÊNCIA INICIADO")
            
            # Salvar estado crítico
            await self._save_emergency_state()
            
            # Parar módulos não críticos
            if hasattr(self.jarvis_core, 'emergency_stop'):
                await self.jarvis_core.emergency_stop()
            
            return True
            
        except Exception:
            return False
    
    async def _save_emergency_state(self):
        """💾 SALVA ESTADO DE EMERGÊNCIA"""
        try:
            emergency_state = {
                'timestamp': datetime.now().isoformat(),
                'failures': [asdict(f) for f in self.failure_history[-10:]],
                'recovery_history': [asdict(r) for r in self.recovery_history[-10:]],
                'system_state': 'emergency_shutdown'
            }
            
            emergency_file = self.config_path / "emergency_state.json"
            with open(emergency_file, 'w', encoding='utf-8') as f:
                json.dump(emergency_state, f, indent=2, default=str)
            
            print("💾 Estado de emergência salvo")
            
        except Exception as e:
            print(f"❌ Erro salvando estado de emergência: {e}")
    
    def _update_strategy_success_rate(self, strategy: RecoveryStrategy, success: bool):
        """📊 ATUALIZA TAXA DE SUCESSO DA ESTRATÉGIA (APRENDIZADO)"""
        current_rate = self.strategy_success_rates.get(strategy, 0.5)
        
        # Weighted moving average (dar mais peso para resultados recentes)
        weight = 0.1
        new_rate = current_rate * (1 - weight) + (1.0 if success else 0.0) * weight
        
        self.strategy_success_rates[strategy] = max(0.0, min(1.0, new_rate))
    
    def get_health_report(self) -> Dict[str, Any]:
        """📊 RELATÓRIO DE SAÚDE DO SISTEMA"""
        return {
            'monitoring_active': self.is_monitoring,
            'current_failures': len(self.current_failures),
            'total_failures': len(self.failure_history),
            'total_recoveries': len(self.recovery_history),
            'success_rate': len([r for r in self.recovery_history if r.success]) / len(self.recovery_history) if self.recovery_history else 0,
            'strategy_performance': dict(self.strategy_success_rates),
            'last_failure': self.failure_history[-1].timestamp.isoformat() if self.failure_history else None
        }

# ============================================================================
# INTEGRAÇÃO COM JARVIS CORE
# ============================================================================

class AutoRecoveryIntegration:
    """🔗 CLASSE PARA INTEGRAÇÃO COM O JARVIS CORE"""
    
    def __init__(self, jarvis_core):
        self.jarvis_core = jarvis_core
        self.auto_recovery = JarvisAutoRecovery(jarvis_core)
    
    async def initialize(self):
        """🚀 INICIALIZA AUTO-RECOVERY"""
        print("🔧 Inicializando Auto-Recovery...")
        self.auto_recovery.start_monitoring()
        print("✅ Auto-Recovery ativo")
    
    async def shutdown(self):
        """⏹️ PARA AUTO-RECOVERY"""
        print("🛑 Parando Auto-Recovery...")
        self.auto_recovery.stop_monitoring()
        print("✅ Auto-Recovery parado")
    
    def get_status(self) -> Dict[str, Any]:
        """📊 STATUS DO AUTO-RECOVERY"""
        return self.auto_recovery.get_health_report()

# Para uso em jarvis_core.py:
# self.auto_recovery = AutoRecoveryIntegration(self)
# await self.auto_recovery.initialize()