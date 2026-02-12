#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Auto-Recovery System Quick Demo
===================================================
Demonstra o sistema de auto-recuperação sem dependências complexas.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def quick_demo():
    """Demo rápido do auto-recovery system"""
    
    print("\n🔧 " + "="*60)
    print("    JARVIS AUTO-RECOVERY SYSTEM - QUICK DEMO")
    print("="*60 + "\n")
    
    try:
        # Adicionar src ao path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root / "src"))
        
        # Import básico
        from src.core.management.auto_recovery_system import (
            get_auto_recovery_system,
            FailureType,
            RecoveryStatus
        )
        
        print("✅ Auto-Recovery System importado com sucesso!")
        
        # Instanciar sistema
        recovery_system = get_auto_recovery_system()
        print(f"✅ Sistema inicializado - Diretório: {recovery_system.data_dir}")
        
        # Mostrar estratégias disponíveis
        print(f"\n📋 Estratégias de Recuperação Disponíveis:")
        for failure_type, strategies in recovery_system.recovery_strategies.items():
            print(f"   🔧 {failure_type.value}: {len(strategies)} estratégias")
        
        # Registrar alguns módulos
        print(f"\n🎯 Registrando módulos para monitoramento:")
        test_modules = ["ai_agent", "voice_controller", "vision_enhancer"]
        
        for module in test_modules:
            health = recovery_system.register_module(f"jarvis.{module}")
            print(f"   📊 {module}: Healthy={health.is_healthy}, Uptime={health.uptime_minutes:.1f}min")
        
        # Simular trigger de recovery
        print(f"\n⚠️ Simulando recuperação de falha...")
        recovery_system._trigger_recovery(
            failure_type=FailureType.IMPORT_ERROR,
            module_name="test_module", 
            error_message="Simulated import error for demo",
            severity=5
        )
        
        # Aguardar processamento
        time.sleep(2)
        
        # Mostrar estatísticas
        stats = recovery_system.get_recovery_stats()
        print(f"\n📊 Estatísticas de Recuperação:")
        if 'total_recoveries' in stats:
            print(f"   📈 Total: {stats['total_recoveries']}")
            print(f"   ✅ Taxa de sucesso: {stats.get('success_rate', 0):.1%}")
        else:
            print("   📊 Nenhuma estatística disponível ainda")
        
        print(f"\n🏥 Health Report:")
        health_report = recovery_system.get_module_health_report()
        for module, health in health_report.items():
            status = "✅" if health['is_healthy'] else "⚠️"
            print(f"   {status} {module}: {health['uptime_minutes']:.1f}min uptime")
            
        print("\n" + "="*60)
        print("🎉 AUTO-RECOVERY DEMO CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\n💡 Sistema pronto para:")
        print("   🔧 Detecção automática de falhas")
        print("   🛠️ Recuperação inteligente com 12 tipos de estratégias")
        print("   📊 Monitoramento em tempo real")
        print("   🧠 Aprendizado de padrões de sucesso")
        print("   🔗 Integração com fallback_system e orchestrator")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se que está na raiz do projeto JARVIS")
        return False
        
    except Exception as e:
        print(f"❌ Erro durante demo: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            if 'recovery_system' in locals():
                if recovery_system.monitoring_active:
                    recovery_system.stop_monitoring()
        except:
            pass

if __name__ == "__main__":
    quick_demo()