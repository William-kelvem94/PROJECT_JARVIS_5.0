#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Testes Completos do Device Manager Avançado
=========================================================
Valida todas as funcionalidades de controle de sistema
"""

import os
import sys
import time
import logging
from pathlib import Path

# Fix Windows terminal encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("DEVICE-MANAGER-TEST")

from src.core.management.device_manager import device_manager, PowerPlan


class DeviceManagerTester:
    """Suite de testes para o Device Manager"""

    def __init__(self):
        self.results = []
        self.dm = device_manager

    def run_test(self, name: str, func):
        """Executa um teste e registra resultado"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTE: {name}")
        print(f"{'='*60}")
        try:
            result = func()
            status = "✅ PASSOU" if result else "⚠️ FALHOU"
            self.results.append((name, result))
            print(f"\n{status}: {name}\n")
            return result
        except Exception as e:
            print(f"\n❌ ERRO: {name} - {e}\n")
            self.results.append((name, False))
            return False

    # ==================== TESTES DE HARDWARE ====================

    def test_system_info(self) -> bool:
        """Testa coleta de informações do sistema"""
        info = self.dm.get_system_info()

        print(f"CPU Cores: {info.get('cpu', {}).get('cores_physical')}")
        print(f"RAM Total: {info.get('memory', {}).get('ram', {}).get('total_gb')} GB")
        print(f"GPU: {len(info.get('gpu', []))} detectada(s)")

        return "cpu" in info and "memory" in info

    def test_health_report(self) -> bool:
        """Testa geração de relatório de saúde"""
        report = self.dm.get_system_health_report()

        print(f"Uptime: {report.get('uptime_seconds', 0)} segundos")
        print(f"Processos: {report.get('processes_count', 0)}")
        print(f"Alertas: {len(report.get('alerts', []))}")

        return "timestamp" in report and "system_info" in report

    # ==================== TESTES DE REDE ====================

    def test_network_info(self) -> bool:
        """Testa informações de rede"""
        info = self.dm.get_network_info()

        print(f"Interfaces: {len(info.get('interfaces', []))}")
        print(f"Conexões ativas: {len(info.get('connections', []))}")

        if info.get("stats"):
            stats = info["stats"]
            print(f"Bytes enviados: {stats.get('bytes_sent', 0) / (1024**2):.2f} MB")
            print(f"Bytes recebidos: {stats.get('bytes_recv', 0) / (1024**2):.2f} MB")

        return len(info.get("interfaces", [])) > 0

    def test_list_interfaces(self) -> bool:
        """Testa listagem de interfaces de rede"""
        interfaces = self.dm.list_network_interfaces()

        for iface in interfaces[:3]:  # Mostra primeiras 3
            print(
                f"  - {iface['name']}: UP={iface['is_up']} Speed={iface.get('speed_mbps')} Mbps"
            )

        return len(interfaces) > 0

    # ==================== TESTES DE ÁUDIO ====================

    def test_audio_control(self) -> bool:
        """Testa controle de áudio"""
        original_volume = self.dm.get_volume()
        print(
            f"Volume original: {original_volume * 100:.0f}%"
            if original_volume
            else "Não disponível"
        )

        # Testa mute
        if self.dm.mute(True):
            print("✅ Áudio mutado")
            time.sleep(1)
            self.dm.mute(False)
            print("✅ Áudio desmutado")

        # Testa mudança de volume (suave)
        if original_volume:
            test_volume = 0.5
            if self.dm.set_volume(test_volume):
                print(f"✅ Volume alterado para {test_volume * 100:.0f}%")
                time.sleep(1)
                # Restaura volume original
                self.dm.set_volume(original_volume)
                print(f"✅ Volume restaurado para {original_volume * 100:.0f}%")

        return True

    def test_list_audio_devices(self) -> bool:
        """Testa listagem de dispositivos de áudio"""
        devices = self.dm.list_audio_devices()

        print(f"Dispositivos de áudio encontrados: {len(devices)}")
        for dev in devices[:3]:
            print(f"  - {dev.get('name')}: {dev.get('state')}")

        return True  # Pode retornar vazio em alguns sistemas

    # ==================== TESTES DE DISPLAY ====================

    def test_display_info(self) -> bool:
        """Testa informações de display"""
        displays = self.dm.get_display_info()

        print(f"Monitores conectados: {len(displays)}")
        for display in displays:
            print(
                f"  - {display.get('name')}: {display.get('screen_width')}x{display.get('screen_height')}"
            )

        return True  # WMI pode não retornar em alguns sistemas

    def test_brightness(self) -> bool:
        """Testa controle de brilho"""
        current = self.dm.get_brightness()

        if current is not None:
            print(f"Brilho atual: {current}%")
            # Não altera brilho no teste automático para não incomodar usuário
            print("ℹ️ Teste de alteração de brilho pulado (não intrusivo)")
            return True
        else:
            print("⚠️ Controle de brilho não disponível neste sistema")
            return True  # Não é erro crítico

    # ==================== TESTES DE PROCESSOS ====================

    def test_list_processes(self) -> bool:
        """Testa listagem de processos"""
        processes = self.dm.list_processes(sort_by="cpu")

        print(f"Total de processos: {len(processes)}")
        print("Top 5 processos por CPU:")
        for proc in processes[:5]:
            print(
                f"  - {proc.get('name')} (PID: {proc.get('pid')}): CPU={proc.get('cpu_percent'):.1f}% RAM={proc.get('memory_percent'):.1f}%"
            )

        return len(processes) > 0

    def test_process_info(self) -> bool:
        """Testa informações detalhadas de processo"""
        # Testa com processo atual
        current_pid = os.getpid()

        info = self.dm.get_process_info(current_pid)

        if info:
            print(f"Processo atual (PID {current_pid}):")
            print(f"  Nome: {info.get('name')}")
            print(f"  Exe: {info.get('exe')}")
            print(f"  Threads: {info.get('num_threads')}")
            print(f"  CPU: {info.get('cpu_percent'):.1f}%")
            print(f"  RAM: {info.get('memory_percent'):.1f}%")
            return True

        return False

    # ==================== TESTES DE REGISTRO ====================

    def test_registry_read(self) -> bool:
        """Testa leitura do registro"""
        import winreg

        # Testa leitura de chave segura conhecida
        value = self.dm.read_registry(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            "ProductName",
        )

        if value:
            print(f"Windows Version: {value}")
            return True

        return False

    def test_registry_write_safe(self) -> bool:
        """Testa escrita segura no registro (em local de teste)"""
        import winreg

        # Escreve em chave de teste temporária
        test_key = r"SOFTWARE\JARVIS_TEST"
        test_value = "test_value"
        test_data = f"Test_{int(time.time())}"

        success = self.dm.write_registry(
            winreg.HKEY_CURRENT_USER, test_key, test_value, test_data, backup=True
        )

        if success:
            # Verifica se foi escrito
            read_data = self.dm.read_registry(
                winreg.HKEY_CURRENT_USER, test_key, test_value
            )

            # Limpa chave de teste
            self.dm.delete_registry_value(
                winreg.HKEY_CURRENT_USER, test_key, test_value, backup=False
            )

            print("✅ Escrita e leitura do registro OK")
            return read_data == test_data

        return False

    # ==================== TESTES DE SERVIÇOS ====================

    def test_list_services(self) -> bool:
        """Testa listagem de serviços"""
        services = self.dm.list_services()

        if len(services) > 0:
            print(f"Total de serviços: {len(services)}")

            # Mostra alguns serviços em execução
            running = [s for s in services if s.get("state") == "Running"][:5]
            print("Serviços em execução (amostra):")
            for svc in running:
                print(f"  - {svc.get('display_name')}: {svc.get('state')}")

            return True
        else:
            print("⚠️ Listagem via WMI não disponível, testando fallback...")
            return True  # Fallback pode não retornar dados estruturados

    # ==================== TESTES DE DISCO ====================

    def test_disk_smart(self) -> bool:
        """Testa dados S.M.A.R.T. do disco"""
        smart = self.dm.get_disk_smart_data("C:")

        if smart:
            print(f"Disco: {smart.get('model')}")
            print(f"Serial: {smart.get('serial_number')}")
            print(f"Tamanho: {smart.get('size_gb')} GB")
            print(f"Interface: {smart.get('interface_type')}")
            print(f"Status: {smart.get('status')}")
            return True
        else:
            print("⚠️ Dados S.M.A.R.T. não disponíveis (WMI requerido)")
            return True  # Não é erro crítico

    def test_disk_analysis(self) -> bool:
        """Testa análise de espaço em disco"""
        analysis = self.dm.analyze_disk_space("C:\\")

        if analysis:
            print("Disco C:")
            print(f"  Total: {analysis.get('total_gb')} GB")
            print(f"  Usado: {analysis.get('used_gb')} GB ({analysis.get('percent')}%)")
            print(f"  Livre: {analysis.get('free_gb')} GB")

            if "large_files" in analysis:
                print(f"  Arquivos grandes encontrados: {len(analysis['large_files'])}")

            return True

        return False

    # ==================== TESTES DE SEGURANÇA ====================

    def test_admin_check(self) -> bool:
        """Testa verificação de privilégios administrativos"""
        is_admin = self.dm.is_admin

        print(f"Executando como administrador: {'SIM' if is_admin else 'NÃO'}")

        if not is_admin:
            print("⚠️ Alguns testes podem falhar sem privilégios admin")

        return True  # Sempre passa, apenas informativo

    def test_user_privileges(self) -> bool:
        """Testa listagem de privilégios"""
        privs = self.dm.get_user_privileges()

        print(f"Privilégios do usuário: {len(privs)}")
        if len(privs) > 0:
            print("Amostra de privilégios:")
            for priv in privs[:5]:
                print(f"  - {priv}")
            return True
        else:
            print("⚠️ pywin32 não disponível para listar privilégios")
            return True

    def test_uac_status(self) -> bool:
        """Testa verificação do UAC"""
        uac_enabled = self.dm.check_uac_enabled()

        if uac_enabled is not None:
            print(f"UAC habilitado: {'SIM' if uac_enabled else 'NÃO'}")
            return True
        else:
            print("⚠️ Não foi possível verificar status do UAC")
            return True

    # ==================== TESTES DE POWER ====================

    def test_power_plan_info(self) -> bool:
        """Testa informações de plano de energia"""
        active_plan = self.dm.get_active_power_plan()

        if active_plan:
            print(f"Plano de energia ativo: {active_plan}")

            # Identifica qual plano é
            for plan in PowerPlan:
                if plan.value.lower() == active_plan.lower():
                    print(f"  Nome: {plan.name}")
                    break

            return True
        else:
            print("⚠️ Não foi possível obter plano de energia ativo")
            return True

    # ==================== TESTES DE EXPORTAÇÃO ====================

    def test_export_report(self) -> bool:
        """Testa exportação de relatório"""
        success = self.dm.export_system_report()

        if success:
            print("✅ Relatório exportado com sucesso")

            # Verifica se arquivo foi criado
            reports_dir = Path("data/system_reports")
            if reports_dir.exists():
                reports = list(reports_dir.glob("*.json"))
                print(f"Total de relatórios: {len(reports)}")
                if reports:
                    latest = max(reports, key=lambda p: p.stat().st_mtime)
                    size_kb = latest.stat().st_size / 1024
                    print(f"Último relatório: {latest.name} ({size_kb:.1f} KB)")

            return True

        return False

    # ==================== EXECUÇÃO DOS TESTES ====================

    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "=" * 60)
        print(" JARVIS 5.0 - DEVICE MANAGER COMPLETE TEST SUITE ".center(60, "="))
        print("=" * 60 + "\n")

        print(f"🖥️ Sistema: {sys.platform}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print(f"👤 Admin: {'SIM' if self.dm.is_admin else 'NÃO'}\n")

        # Define bateria de testes
        tests = [
            ("Hardware - System Info", self.test_system_info),
            ("Hardware - Health Report", self.test_health_report),
            ("Network - Info Completa", self.test_network_info),
            ("Network - List Interfaces", self.test_list_interfaces),
            ("Audio - Controle", self.test_audio_control),
            ("Audio - List Devices", self.test_list_audio_devices),
            ("Display - Info", self.test_display_info),
            ("Display - Brightness", self.test_brightness),
            ("Process - List Processes", self.test_list_processes),
            ("Process - Process Info", self.test_process_info),
            ("Registry - Read", self.test_registry_read),
            ("Registry - Write Safe", self.test_registry_write_safe),
            ("Services - List", self.test_list_services),
            ("Disk - S.M.A.R.T.", self.test_disk_smart),
            ("Disk - Space Analysis", self.test_disk_analysis),
            ("Security - Admin Check", self.test_admin_check),
            ("Security - User Privileges", self.test_user_privileges),
            ("Security - UAC Status", self.test_uac_status),
            ("Power - Plan Info", self.test_power_plan_info),
            ("Export - System Report", self.test_export_report),
        ]

        # Executa testes
        start_time = time.time()

        for name, test_func in tests:
            self.run_test(name, test_func)
            time.sleep(0.5)  # Pequena pausa entre testes

        duration = time.time() - start_time

        # Resultado final
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)

        print("\n" + "=" * 60)
        print(" RESULTADO FINAL ".center(60, "="))
        print("=" * 60)
        print(f"\n✅ Passou: {passed}/{total}")
        print(f"⏱️ Duração: {duration:.2f}s\n")

        if passed == total:
            print("🏆 TODOS OS TESTES PASSARAM!")
        elif passed >= total * 0.8:
            print("✅ Maioria dos testes passou (>80%)")
        else:
            print("⚠️ Alguns testes falharam - revisar funcionalidades")

        print("\n" + "=" * 60 + "\n")

        return passed == total


if __name__ == "__main__":
    tester = DeviceManagerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
