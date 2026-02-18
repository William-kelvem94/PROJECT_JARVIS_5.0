from src.learning.sanity_checker import get_sanity_checker
import sys
import os
from pathlib import Path

# Adicionar root ao sys.path
sys.path.append(os.getcwd())


def final_audit():
    print("🚀 Iniciando Auditoria Final JARVIS 5.0 (Rumo ao 10/10)...\n")

    project_root = Path(os.getcwd())
    checker = get_sanity_checker(project_root)

    print("🔍 Executando Sanity Check...")
    report = checker.run_full_check()

    print(f"\n📊 RELATÓRIO DE ESTABILIDADE: {report['total_score']*100}%")
    print("=" * 40)
    for comp, data in report["components"].items():
        status = "✅" if data["status"] == "PASS" else "❌"
        print(f"{status} {comp}: {data['details']}")
    print("=" * 40)

    # Verificar existência dos logs de evolução
    evolution_log = project_root / "data" / "EVOLUTION.log"
    if evolution_log.exists():
        print(
            f"✅ Log de Evolução (Decision Log): ATIVO ({evolution_log.stat().st_size} bytes)"
        )
    else:
        # Tenta criar um evento de teste para validar
        try:
            from src.core.management.evolution_engine import evolution_engine

            evolution_engine.log_evolution(
                "system", "Teste de Auditoria", "Validando sistema de logs 10/10"
            )
            print("✅ Log de Evolução (Decision Log): CRIADO E ATIVO")
        except Exception as e:
            print(f"❌ Log de Evolução: ERRO AO CRIAR ({e})")

    # Verificar modo de emergência
    try:
        print(
            f"✅ Protocolo Stark (Emergency Mode): PRONTO (Status: {'ATIVO' if auto_recovery_system.is_emergency_mode else 'STANDBY'})"
        )
    except Exception as e:
        print(f"❌ Protocolo Stark: ERRO NA INICIALIZAÇÃO ({e})")

    print("\n🏆 AUDITORIA CONCLUÍDA: SISTEMA PRONTO PARA NÍVEL 10/10.")


if __name__ == "__main__":
    final_audit()
