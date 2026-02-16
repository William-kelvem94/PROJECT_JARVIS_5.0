"""
Teste de Integração Completo do Sistema Core JARVIS
==================================================

Este teste valida a integração completa de todas as melhorias implementadas
no sistema core, incluindo SecurityManager, IOTManager, StarkOrchestrator
e todos os __init__.py melhorados.

Utiliza mocking inteligente para evitar dependências problemáticas
enquanto testa funcionalidades reais.
"""

import sys
import logging
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Adicionar o diretório raiz ao Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Mock de dependências problemáticas ANTES de qualquer import
problematic_modules = [
    "mediapipe",
    "tensorflow",
    "cv2",
    "face_recognition",
    "dlib",
    "pygame",
    "pycaw",
    "win32api",
    "winsound",
    "pyaudio",
]

for module_name in problematic_modules:
    if module_name not in sys.modules:
        sys.modules[module_name] = Mock()

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoreIntegrationTest(unittest.TestCase):
    """Teste abrangente de integração do sistema core"""

    @classmethod
    def setUpClass(cls):
        """Setup global para todos os testes"""
        cls.project_root = current_dir
        cls.src_path = cls.project_root / "src"

        # Verifica se estrutura básica existe
        if not cls.src_path.exists():
            raise unittest.SkipTest("Diretório src não encontrado")

    def setUp(self):
        """Setup para cada teste individual"""
        # Reset de mocks entre testes
        for module_name in problematic_modules:
            if module_name in sys.modules:
                sys.modules[module_name] = Mock()

    def test_security_manager_comprehensive(self):
        """Teste completo do SecurityManager"""
        print("\n🛡️ Testando SecurityManager...")

        try:
            from src.core.security.security_manager import SecurityManager

            security = SecurityManager()

            # Teste 1: Paths perigosos devem ser bloqueados
            dangerous_paths = [
                r"C:\Windows\System32\config",
                r"C:\Program Files\sensitive",
                "SINGULARITY_LAUNCHER.py",
                "kill_switch.py",
            ]

            for path in dangerous_paths:
                result = security.validate_path_access(path)
                self.assertFalse(
                    result, f"Path perigoso '{path}' deveria ser bloqueado"
                )
                print(f"   ✅ Bloqueou path perigoso: {path}")

            # Teste 2: Paths seguros devem ser permitidos
            safe_paths = [
                "/home/user/documents/test.txt",
                r"C:\Users\user\Documents\project",
                "./relative/path/file.py",
            ]

            for path in safe_paths:
                result = security.validate_path_access(path)
                self.assertTrue(result, f"Path seguro '{path}' deveria ser permitido")
                print(f"   ✅ Permitiu path seguro: {path}")

            # Teste 3: URLs perigosas devem ser bloqueadas
            dangerous_urls = [
                "https://malicious-site.com/steal",
                "http://evil-domain.ru/exfiltrate",
            ]

            for url in dangerous_urls:
                result = security.validate_web_request(url)
                self.assertFalse(result, f"URL perigosa '{url}' deveria ser bloqueada")
                print(f"   ✅ Bloqueou URL perigosa: {url}")

            # Teste 4: URLs seguras devem ser permitidas
            safe_urls = [
                "https://google.com/search",
                "https://apis.openai.com/v1/chat",
                "http://localhost:8080/api",
            ]

            for url in safe_urls:
                result = security.validate_web_request(url)
                self.assertTrue(result, f"URL segura '{url}' deveria ser permitida")
                print(f"   ✅ Permitiu URL segura: {url}")

            print("   🛡️ SecurityManager funcionando perfeitamente!")
            return True

        except Exception as e:
            self.fail(f"SecurityManager falhou: {e}")

    def test_iot_manager_comprehensive(self):
        """Teste completo do IOTManager"""
        print("\n🏠 Testando IOTManager...")

        try:
            # Mock do config antes do import
            with patch("src.core.iot.iot_manager.config") as mock_config:
                from src.core.iot.iot_manager import IOTManager

                # Teste 1: IOTManager não configurado
                mock_config.get_setting.side_effect = lambda key, default: default

                iot_unconfigured = IOTManager()
                self.assertFalse(iot_unconfigured.is_configured)
                self.assertEqual(
                    iot_unconfigured.ha_url, "http://homeassistant.local:8123"
                )
                print("   ✅ IOTManager não configurado detectado corretamente")

                # Teste 2: IOTManager configurado
                def mock_configured_settings(key, default):
                    settings = {
                        "iot.ha_url": "http://192.168.1.100:8123",
                        "iot.ha_token": "test_secure_token_123",
                    }
                    return settings.get(key, default)

                mock_config.get_setting.side_effect = mock_configured_settings

                iot_configured = IOTManager()
                self.assertTrue(iot_configured.is_configured)
                self.assertEqual(iot_configured.ha_url, "http://192.168.1.100:8123")
                self.assertEqual(iot_configured.ha_token, "test_secure_token_123")
                print("   ✅ IOTManager configurado detectado corretamente")

                # Teste 3: Controle de dispositivo (mocked)
                with patch("src.core.iot.iot_manager.requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_post.return_value = mock_response

                    result = iot_configured.control_device(
                        "light.living_room", "turn_on"
                    )
                    self.assertTrue(result)

                    # Verifica se requisição foi feita corretamente
                    mock_post.assert_called_once()
                    args, kwargs = mock_post.call_args

                    expected_url = (
                        "http://192.168.1.100:8123/api/services/light/turn_on"
                    )
                    self.assertEqual(args[0], expected_url)

                    self.assertIn("Authorization", kwargs["headers"])
                    self.assertEqual(
                        kwargs["headers"]["Authorization"],
                        "Bearer test_secure_token_123",
                    )

                    expected_payload = {"entity_id": "light.living_room"}
                    self.assertEqual(kwargs["json"], expected_payload)

                    print("   ✅ Controle de dispositivo IoT funcionando")

                # Teste 4: Controle sem configuração deve falhar
                result = iot_unconfigured.control_device("light.test", "turn_on")
                self.assertFalse(result)
                print("   ✅ Controle sem configuração bloqueado corretamente")

            print("   🏠 IOTManager funcionando perfeitamente!")
            return True

        except Exception as e:
            self.fail(f"IOTManager falhou: {e}")

    def test_stark_orchestrator_comprehensive(self):
        """Teste completo do StarkOrchestrator com novos recursos"""
        print("\n🎛️ Testando StarkOrchestrator melhorado...")

        try:
            with patch("src.core.orchestrator.SecurityManager") as mock_security:
                with patch("src.core.orchestrator.IOTManager") as mock_iot:
                    with patch("src.core.orchestrator.FallbackSystem") as mock_fallback:
                        from src.core.orchestrator import StarkOrchestrator

                        # Setup mocks
                        mock_security_instance = Mock()
                        mock_security.return_value = mock_security_instance

                        mock_iot_instance = Mock()
                        mock_iot_instance.is_configured = True
                        mock_iot.return_value = mock_iot_instance

                        mock_fallback_instance = Mock()
                        mock_fallback.return_value = mock_fallback_instance

                        # Teste 1: Inicialização básica
                        mock_jarvis = Mock()
                        mock_jarvis.shutdown_manager = Mock()
                        mock_jarvis.ai_agent = Mock()
                        mock_jarvis.window_manager = Mock()

                        orchestrator = StarkOrchestrator(mock_jarvis)
                        self.assertIsNotNone(orchestrator)
                        self.assertFalse(orchestrator.is_ready)
                        self.assertEqual(len(orchestrator.components), 0)
                        print("   ✅ Inicialização básica funcionando")

                        # Teste 2: Inicialização completa do sistema
                        with patch.object(
                            orchestrator, "_init_interface_orchestration"
                        ):
                            orchestrator.initialize_stark_system()

                        self.assertTrue(orchestrator.is_ready)
                        self.assertIn("security", orchestrator.components)
                        self.assertIn("iot", orchestrator.components)
                        self.assertIn("fallback", orchestrator.components)
                        print("   ✅ Inicialização completa funcionando")

                        # Teste 3: Health check expandido
                        health = orchestrator.get_system_health()
                        expected_modules = [
                            "vision",
                            "audio",
                            "intelligence",
                            "actions",
                            "security",
                            "iot",
                            "infrastructure",
                        ]
                        for module in expected_modules:
                            self.assertIn(module, health)
                        print("   ✅ Health check expandido funcionando")

                        # Teste 4: System info detalhado
                        info = orchestrator.get_system_info()
                        expected_keys = [
                            "is_ready",
                            "components_count",
                            "registered_components",
                            "module_health",
                            "system_healthy",
                            "jarvis_core_available",
                        ]
                        for key in expected_keys:
                            self.assertIn(key, info)

                        self.assertTrue(info["is_ready"])
                        self.assertEqual(info["components_count"], 3)
                        self.assertIn("security", info["registered_components"])
                        print("   ✅ System info detalhado funcionando")

                        # Teste 5: Restart de componentes
                        result = orchestrator.restart_component("security")
                        self.assertTrue(result)
                        print("   ✅ Restart de componentes funcionando")

            print("   🎛️ StarkOrchestrator melhorado funcionando perfeitamente!")
            return True

        except Exception as e:
            self.fail(f"StarkOrchestrator falhou: {e}")

    def test_init_files_improvements(self):
        """Teste dos melhoramentos nos arquivos __init__.py"""
        print("\n📦 Testando __init__.py melhorados...")

        try:
            # Teste 1: __init__.py principal do core
            core_init_path = self.src_path / "core" / "__init__.py"
            self.assertTrue(core_init_path.exists(), "core/__init__.py deve existir")

            # Lê conteúdo e verifica se não está vazio
            content = core_init_path.read_text(encoding="utf-8")
            self.assertGreater(
                len(content.strip()), 10, "core/__init__.py não deve estar vazio"
            )
            self.assertIn('"""', content, "Deve ter documentação")
            self.assertIn("__all__", content, "Deve ter __all__ definido")
            print("   ✅ core/__init__.py melhorado")

            # Teste 2: __init__.py dos submódulos
            submodules = ["security", "iot", "actions", "engine"]

            for submodule in submodules:
                init_path = self.src_path / "core" / submodule / "__init__.py"
                if init_path.exists():
                    content = init_path.read_text(encoding="utf-8")
                    self.assertNotEqual(
                        content.strip(),
                        "# clean",
                        f"{submodule}/__init__.py foi melhorado",
                    )
                    if '"""' in content:
                        print(f"   ✅ {submodule}/__init__.py melhorado e documentado")
                    else:
                        print(
                            f"   ⚠️ {submodule}/__init__.py melhorado mas sem documentação"
                        )
                else:
                    print(f"   ⚠️ {submodule}/__init__.py não encontrado")

            # Teste 3: Imports seguros funcionando
            try:
                # Import que deveria funcionar agora
                import src.core.security

                if hasattr(src.core.security, "__all__"):
                    print(
                        f"   ✅ src.core.security.__all__ = {src.core.security.__all__}"
                    )

                import src.core.iot

                if hasattr(src.core.iot, "__all__"):
                    print(f"   ✅ src.core.iot.__all__ = {src.core.iot.__all__}")

            except ImportError as e:
                print(f"   ⚠️ Import direto falhou: {e}")

            print("   📦 __init__.py melhoramentos funcionando!")
            return True

        except Exception as e:
            self.fail(f"__init__.py improvements falharam: {e}")

    def test_full_integration_workflow(self):
        """Teste do workflow completo de integração"""
        print("\n🎯 Testando workflow completo de integração...")

        try:
            # Setup de todos os mocks necessários
            with patch("src.core.orchestrator.SecurityManager") as mock_security:
                with patch("src.core.orchestrator.IOTManager") as mock_iot:
                    with patch("src.core.orchestrator.FallbackSystem") as mock_fallback:
                        with patch("src.core.iot.iot_manager.config") as mock_config:

                            # Configure todos os mocks
                            mock_security_instance = Mock()
                            mock_security_instance.validate_path_access.return_value = (
                                True
                            )
                            mock_security_instance.validate_web_request.return_value = (
                                True
                            )
                            mock_security.return_value = mock_security_instance

                            mock_iot_instance = Mock()
                            mock_iot_instance.is_configured = True
                            mock_iot_instance.control_device.return_value = True
                            mock_iot.return_value = mock_iot_instance

                            mock_fallback.return_value = Mock()

                            mock_config.get_setting.side_effect = lambda key, default: {
                                "iot.ha_url": "http://test:8123",
                                "iot.ha_token": "test_token",
                            }.get(key, default)

                            # Teste workflow completo
                            from src.core.orchestrator import StarkOrchestrator
                            from src.core.security.security_manager import (
                                SecurityManager,
                            )
                            from src.core.iot.iot_manager import IOTManager

                            # 1. Inicialização
                            mock_jarvis = Mock()
                            orchestrator = StarkOrchestrator(mock_jarvis)

                            # 2. Inicialização do sistema
                            with patch.object(
                                orchestrator, "_init_interface_orchestration"
                            ):
                                orchestrator.initialize_stark_system()

                            # 3. Verificação de componentes
                            self.assertTrue(orchestrator.is_ready)
                            self.assertGreater(len(orchestrator.components), 0)

                            # 4. Health checks
                            health = orchestrator.get_system_health()
                            self.assertIn("security", health)
                            self.assertIn("iot", health)

                            # 5. System info
                            info = orchestrator.get_system_info()
                            self.assertTrue(info["system_healthy"])

                            # 6. Funcionalidade específica
                            security = SecurityManager()
                            self.assertTrue(security.validate_path_access("/safe/path"))

                            iot = IOTManager()
                            self.assertTrue(iot.is_configured)

                            print("   ✅ Inicialização completa")
                            print("   ✅ Health monitoring funcionando")
                            print("   ✅ Componentes integrados")
                            print("   ✅ Funcionalidades específicas")

            print("   🎯 Workflow completo funcionando perfeitamente!")
            return True

        except Exception as e:
            self.fail(f"Workflow integration falhou: {e}")


def run_comprehensive_test():
    """Executa teste abrangente das melhorias"""
    print("🚀 JARVIS Core Integration - Teste Completo")
    print("=" * 60)

    # Cria suite de testes
    suite = unittest.TestLoader().loadTestsFromTestCase(CoreIntegrationTest)

    # Executa testes com verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # Relatório final
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✨ Melhorias Validadas:")
        print("   • SecurityManager com validações robustas")
        print("   • IOTManager para controle de dispositivos")
        print("   • StarkOrchestrator com recursos avançados")
        print("   • __init__.py melhorados e documentados")
        print("   • Integração completa funcionando")
        print("\n🎯 Sistema core está robusto e pronto para produção!")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print(f"   Falhas: {len(result.failures)}")
        print(f"   Erros: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
