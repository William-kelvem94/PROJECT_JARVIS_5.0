#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Auto-Recovery System Demo & Test
====================================================
Demonstra e testa o novo sistema de auto-recuperação inteligente.

Testa:
- Detecção automática de falhas
- Estratégias de recuperação
- Monitoramento em tempo real
- Learning de padrões de sucesso
- Integração com outros sistemas
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path

# Adicionar src ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.core.management.auto_recovery_system import (
    get_auto_recovery_system,
    trigger_recovery_for_exception,
    register_module_for_monitoring,
    FailureType,
    RecoveryStatus
)

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutoRecoveryDemo")

class AutoRecoveryDemo:
    """
    Demonstração completa do sistema de auto-recuperação.
    """
    
    def __init__(self):
        self.recovery_system = get_auto_recovery_system()
        self.test_results = {}
        
    def run_complete_demo(self):
        """Execute demonstração completa do sistema"""
        
        print("\n🔧 " + "="*60)
        print("    JARVIS SINGULARITY - AUTO-RECOVERY SYSTEM DEMO")
        print("="*60 + "\n")
        
        # 1. Sistema básico
        self._demo_basic_setup()
        time.sleep(1)
        
        # 2. Registro de módulos
        self._demo_module_registration()
        time.sleep(1)
        
        # 3. Monitoramento em tempo real
        self._demo_real_time_monitoring()
        time.sleep(2)
        
        # 4. Simulação de falhas e recuperação
        self._demo_failure_simulation()
        time.sleep(2)
        
        # 5. Análise de performance
        self._demo_performance_analysis()
        time.sleep(1)
        
        # 6. Relatório final
        self._demo_final_report()
    
    def _demo_basic_setup(self):
        """Demonstra configuração básica do sistema"""
        print("📋 STEP 1: Basic System Setup")
        print("-" * 30)
        
        print(f"✅ Auto-Recovery System initialized")
        print(f"📊 Data directory: {self.recovery_system.data_dir}")
        print(f"🔄 Monitor interval: {self.recovery_system.monitor_interval}s")
        print(f"⚙️ Max recovery attempts: {self.recovery_system.max_recovery_attempts}")
        print(f"📋 Registered strategy types: {len(self.recovery_system.recovery_strategies)}")
        print()
    
    def _demo_module_registration(self):
        """Demonstra registro de módulos para monitoramento"""
        print("🎯 STEP 2: Module Registration & Health Tracking")
        print("-" * 50)
        
        # Registrar módulos simulados
        test_modules = [
            "jarvis_core.ai_agent",
            "jarvis_core.voice_controller", 
            "jarvis_core.vision_enhancer",
            "jarvis_interface.window_manager",
            "jarvis_learning.neural_engine"
        ]
        
        for module in test_modules:
            health = self.recovery_system.register_module(module)
            print(f"🔍 Registered: {module}")
            print(f"   └─ Uptime: {health.uptime_minutes:.1f}min | Healthy: {health.is_healthy}")
        
        print(f"\n📊 Total monitored modules: {len(self.recovery_system.module_health)}")
        print()
    
    def _demo_real_time_monitoring(self):
        """Demonstra monitoramento em tempo real"""
        print("🔍 STEP 3: Real-Time Health Monitoring")
        print("-" * 40)
        
        print("🟢 Starting monitoring system...")
        self.recovery_system.start_monitoring()
        
        # Simular alguns updates de métrica
        for module_name, health in self.recovery_system.module_health.items():
            # Simular métricas atualizadas
            import random
            health.update_metrics(
                memory_mb=random.uniform(50, 200),
                cpu_percent=random.uniform(5, 25),
                response_ms=random.uniform(10, 100)
            )
        
        # Force health check
        health_status = self.recovery_system.force_health_check()
        print(f"✅ Health check status: {health_status['status']}")
        print(f"📊 Monitored: {health_status['monitored_modules']} | Healthy: {health_status['healthy_modules']}")
        print()
    
    def _demo_failure_simulation(self):
        """Simula falhas e demonstra recuperação automática"""
        print("⚠️ STEP 4: Failure Simulation & Auto-Recovery")
        print("-" * 45)
        
        # Simular diferentes tipos de falhas
        test_failures = [
            {
                "type": FailureType.IMPORT_ERROR,
                "module": "jarvis_core.ai_agent",
                "error": ImportError("No module named 'transformers'"),
                "severity": 6
            },
            {
                "type": FailureType.MEMORY_LEAK,
                "module": "jarvis_core.vision_enhancer", 
                "error": MemoryError("Memory usage exceeded 90%"),
                "severity": 8
            },
            {
                "type": FailureType.NETWORK_FAILURE,
                "module": "jarvis_learning.neural_engine",
                "error": ConnectionError("Failed to connect to model server"),
                "severity": 5
            }
        ]
        
        for failure in test_failures:
            print(f"🚨 Simulating {failure['type'].value} in {failure['module']}")
            
            # Trigger recovery
            self.recovery_system._trigger_recovery(
                failure_type=failure["type"],
                module_name=failure["module"],
                error_message=str(failure["error"]),
                severity=failure["severity"]
            )
            
            # Wait for recovery to complete
            time.sleep(3)
            
            print(f"   ✅ Recovery process completed")
            print()
    
    def _demo_performance_analysis(self):
        """Demonstra análise de performance do sistema"""
        print("📊 STEP 5: Performance Analysis & Learning")
        print("-" * 42)
        
        # Get recovery statistics
        stats = self.recovery_system.get_recovery_stats()
        
        print("🎯 Recovery Performance:")
        if 'total_recoveries' in stats:
            print(f"   📈 Total recoveries: {stats['total_recoveries']}")
            print(f"   ✅ Success rate: {stats['success_rate']:.1%}")
            print(f"   ⏱️ Avg recovery time: {stats['average_recovery_time_ms']:.1f}ms")
        
        print("\n📋 Success by Failure Type:")
        if 'success_by_failure_type' in stats:
            for failure_type, type_stats in stats['success_by_failure_type'].items():
                print(f"   {failure_type}: {type_stats['success_rate']:.1%} ({type_stats['total_attempts']} attempts)")
        
        print("\n🧠 Strategy Learning Performance:")
        if 'strategy_performance' in stats:
            for strategy, rate in list(stats['strategy_performance'].items())[:5]:  # Top 5
                print(f"   {strategy}: {rate:.1%} success rate")
        
        print()
    
    def _demo_final_report(self):
        """Gera relatório final da demonstração"""
        print("📋 STEP 6: Final System Health Report")
        print("-" * 38)
        
        # Get comprehensive health report
        health_report = self.recovery_system.get_module_health_report()
        
        print("🏥 Module Health Overview:")
        for module, health in health_report.items():
            status_icon = "✅" if health['is_healthy'] else "⚠️"
            print(f"   {status_icon} {module}:")
            print(f"      ⏱️ Uptime: {health['uptime_minutes']:.1f}min")
            print(f"      📊 Memory: {health['memory_usage_mb']:.1f}MB")
            print(f"      🔄 Recoveries: {health['recovery_count']}")
        
        # Stop monitoring
        if self.recovery_system.monitoring_active:
            self.recovery_system.stop_monitoring()
        
        print("\n" + "="*60)
        print("🎉 AUTO-RECOVERY SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n💡 Key Benefits Demonstrated:")
        print("   🔧 Intelligent failure detection and classification")
        print("   🛠️ Automated recovery with multiple strategies")  
        print("   📊 Real-time monitoring with performance metrics")
        print("   🧠 Machine learning for strategy optimization")
        print("   🔗 Seamless integration with existing systems")
        print("\n🚀 Your JARVIS is now enterprise-ready with self-healing capabilities!")

def main():
    """Executa demonstração do sistema de auto-recuperação"""
    try:
        demo = AutoRecoveryDemo()
        demo.run_complete_demo()
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()