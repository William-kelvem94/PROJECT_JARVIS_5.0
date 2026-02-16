"""
Testes Completos para o StarkOrchestrator - Sistema Central do JARVIS

Testa inicialização de módulos, verificação de saúde, reinicialização de componentes,
tratamento de erros e integração completa dos novos módulos Security e IoT.
"""

import unittest
from unittest.mock import Mock, patch
import logging
import sys
import os

# Adiciona o diretório raiz ao path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Mock de módulos problemáticos antes do import
sys.modules["mediapipe"] = Mock()
sys.modules["tensorflow"] = Mock()
sys.modules["cv2"] = Mock()
sys.modules["face_recognition"] = Mock()
sys.modules["dlib"] = Mock()

from src.core.orchestrator import StarkOrchestrator


class TestStarkOrchestrator(unittest.TestCase):
    """Testes unitários completos para o StarkOrchestrator"""

    def setUp(self):
        """Configuração inicial para cada teste"""
        self.mock_jarvis = Mock()
        self.mock_jarvis.shutdown_manager = Mock()
        self.mock_jarvis.ai_agent = Mock()
        self.mock_jarvis.window_manager = Mock()

        self.orchestrator = StarkOrchestrator(self.mock_jarvis)

        # Clear any existing components
        self.orchestrator.components.clear()
        self.orchestrator.is_ready = False

    def test_orchestrator_initialization(self):
        """Testa se o orchestrador é inicializado corretamente"""
        self.assertIsNotNone(self.orchestrator)
        self.assertEqual(self.orchestrator.jarvis, self.mock_jarvis)
        self.assertFalse(self.orchestrator.is_ready)
        self.assertEqual(len(self.orchestrator.components), 0)
        self.assertIsInstance(self.orchestrator.components, dict)

    @patch("src.core.orchestrator.SecurityManager")
    @patch("src.core.orchestrator.IOTManager")
    @patch("src.core.orchestrator.FallbackSystem")
    def test_stark_system_initialization_complete_success(
        self, mock_fallback, mock_iot, mock_security
    ):
        """Testa a inicialização completa do sistema Stark com sucesso total"""
        # Mock do IOTManager para simular configuração completa
        mock_iot_instance = Mock()
        mock_iot_instance.is_configured = True
        mock_iot.return_value = mock_iot_instance

        # Mock do SecurityManager
        mock_security_instance = Mock()
        mock_security.return_value = mock_security_instance

        # Mock do FallbackSystem
        mock_fallback_instance = Mock()
        mock_fallback.return_value = mock_fallback_instance

        # Mock da inicialização de interface
        with patch.object(
            self.orchestrator, "_init_interface_orchestration"
        ) as mock_interface:
            self.orchestrator.initialize_stark_system()

        # Verifica se os componentes foram registrados
        self.assertIn("security", self.orchestrator.components)
        self.assertIn("iot", self.orchestrator.components)
        self.assertIn("fallback", self.orchestrator.components)

        # Verifica se o sistema está pronto
        self.assertTrue(self.orchestrator.is_ready)

        # Verifica se todos os mocks foram chamados
        mock_security.assert_called_once()
        mock_iot.assert_called_once()
        mock_fallback.assert_called_once_with(self.mock_jarvis)
        mock_interface.assert_called_once()

    @patch(
        "src.core.orchestrator.SecurityManager",
        side_effect=Exception("Security init failed"),
    )
    @patch("src.core.orchestrator.IOTManager")
    @patch("src.core.orchestrator.FallbackSystem")
    @patch("src.core.orchestrator.logger")
    def test_stark_system_initialization_partial_failure(
        self, mock_logger, mock_fallback, mock_iot, mock_security
    ):
        """Testa inicialização com falhas parciais"""
        # IOT e Fallback funcionam normalmente
        mock_iot_instance = Mock()
        mock_iot_instance.is_configured = False  # IoT não configurado
        mock_iot.return_value = mock_iot_instance

        mock_fallback_instance = Mock()
        mock_fallback.return_value = mock_fallback_instance

        with patch.object(self.orchestrator, "_init_interface_orchestration"):
            self.orchestrator.initialize_stark_system()

        # Security falhou, mas outros funcionaram
        self.assertNotIn("security", self.orchestrator.components)
        self.assertIn("iot", self.orchestrator.components)
        self.assertIn("fallback", self.orchestrator.components)

        # Sistema não está completamente pronto devido falhas
        self.assertFalse(self.orchestrator.is_ready)

        # Verifica se erro foi logado
        mock_logger.error.assert_called()

    def test_module_status_checking_comprehensive(self):
        """Testa verificação completa de status dos módulos"""
        # Testa módulo desconhecido
        status = self.orchestrator.get_module_status("unknown_module")
        self.assertEqual(status, "UNKNOWN")

        # Testa Security online
        self.orchestrator.components["security"] = Mock()
        status = self.orchestrator.get_module_status("security")
        self.assertEqual(status, "ONLINE")

        # Testa IoT configurado (online)
        mock_iot_configured = Mock()
        mock_iot_configured.is_configured = True
        self.orchestrator.components["iot"] = mock_iot_configured
        status = self.orchestrator.get_module_status("iot")
        self.assertEqual(status, "ONLINE")

        # Testa IoT não configurado (degraded)
        mock_iot_not_configured = Mock()
        mock_iot_not_configured.is_configured = False
        self.orchestrator.components["iot"] = mock_iot_not_configured
        status = self.orchestrator.get_module_status("iot")
        self.assertEqual(status, "DEGRADED")

        # Testa Infrastructure com sistema pronto
        self.orchestrator.is_ready = True
        status = self.orchestrator.get_module_status("infrastructure")
        self.assertEqual(status, "ONLINE")

        # Testa Infrastructure com sistema não pronto
        self.orchestrator.is_ready = False
        status = self.orchestrator.get_module_status("infrastructure")
        self.assertEqual(status, "DEGRADED")

    def test_system_health_check_comprehensive(self):
        """Testa verificação completa de saúde do sistema"""
        # Sistema sem componentes - todos offline
        health = self.orchestrator.get_system_health()

        # Verifica se todos os módulos estão no health check
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

        # Sistema não saudável sem componentes
        self.assertFalse(self.orchestrator.is_system_healthy())

        # Adiciona todos os componentes essenciais
        self.orchestrator.components["security"] = Mock()

        mock_iot = Mock()
        mock_iot.is_configured = True
        self.orchestrator.components["iot"] = mock_iot

        self.orchestrator.components["fallback"] = Mock()
        self.orchestrator.is_ready = True

        # Agora deve estar mais saudável
        health = self.orchestrator.get_system_health()
        self.assertTrue(self.orchestrator.is_system_healthy())

        # Verifica status específicos
        self.assertEqual(health["security"], "ONLINE")
        self.assertEqual(health["iot"], "ONLINE")
        self.assertEqual(health["infrastructure"], "ONLINE")

    def test_restart_component_functionality(self):
        """Testa funcionalidade completa de reinicialização de componentes"""
        # Teste componente desconhecido
        result = self.orchestrator.restart_component("unknown_component")
        self.assertFalse(result)

        # Mock dos managers para teste de reinicialização
        with patch("src.core.orchestrator.SecurityManager") as mock_security:
            mock_security_instance = Mock()
            mock_security.return_value = mock_security_instance

            # Adiciona componente existente
            self.orchestrator.components["security"] = Mock()

            # Testa reinicialização bem-sucedida
            result = self.orchestrator.restart_component("security")
            self.assertTrue(result)

            # Verifica se componente foi removido e recriado
            self.assertIn("security", self.orchestrator.components)
            mock_security.assert_called_once()

        # Teste reinicialização com erro
        with patch(
            "src.core.orchestrator.SecurityManager",
            side_effect=Exception("Restart failed"),
        ):
            result = self.orchestrator.restart_component("security")
            self.assertFalse(result)

    def test_get_system_info_comprehensive(self):
        """Testa informações completas do sistema"""
        # Sistema inicial sem componentes
        info = self.orchestrator.get_system_info()

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

        self.assertFalse(info["is_ready"])
        self.assertEqual(info["components_count"], 0)
        self.assertEqual(info["registered_components"], [])
        self.assertFalse(info["system_healthy"])
        self.assertTrue(info["jarvis_core_available"])

        # Adiciona componentes e testa novamente
        self.orchestrator.components["security"] = Mock()
        self.orchestrator.components["iot"] = Mock()
        self.orchestrator.is_ready = True

        info = self.orchestrator.get_system_info()

        self.assertTrue(info["is_ready"])
        self.assertEqual(info["components_count"], 2)
        self.assertIn("security", info["registered_components"])
        self.assertIn("iot", info["registered_components"])

    @patch("src.core.orchestrator.logger")
    def test_initialization_error_handling_detailed(self, mock_logger):
        """Testa tratamento detalhado de erros durante inicialização"""
        # Teste erro no SecurityManager
        with patch(
            "src.core.orchestrator.SecurityManager",
            side_effect=Exception("Security init error"),
        ):
            with self.assertRaises(Exception):
                self.orchestrator._init_security()
            mock_logger.error.assert_called()

        # Reset mock
        mock_logger.reset_mock()

        # Teste erro no IOTManager (não deve interromper)
        with patch(
            "src.core.orchestrator.IOTManager", side_effect=Exception("IoT init error")
        ):
            # IoT não deve lançar exceção, apenas logar
            self.orchestrator._init_iot()
            mock_logger.error.assert_called()

    def test_component_registration_and_management(self):
        """Testa registro e gerenciamento completo de componentes"""
        # Teste registro básico
        mock_component = Mock()
        self.orchestrator.components["test"] = mock_component

        self.assertIn("test", self.orchestrator.components)
        self.assertEqual(self.orchestrator.components["test"], mock_component)

        # Teste múltiplos componentes
        components = {
            "security": Mock(),
            "iot": Mock(),
            "fallback": Mock(),
            "custom": Mock(),
        }

        for name, component in components.items():
            self.orchestrator.components[name] = component

        self.assertEqual(len(self.orchestrator.components), 5)  # test + 4 novos

        for name in components.keys():
            self.assertIn(name, self.orchestrator.components)

    def test_fallback_injection(self):
        """Testa injeção do fallback system no AI Agent"""
        # Mock do AI Agent
        mock_ai_agent = Mock()
        self.mock_jarvis.ai_agent = mock_ai_agent

        # Mock do FallbackSystem
        with patch("src.core.orchestrator.FallbackSystem") as mock_fallback_class:
            mock_fallback_instance = Mock()
            mock_fallback_class.return_value = mock_fallback_instance

            self.orchestrator._init_fallback_system()

            # Verifica se fallback foi criado e registrado
            self.assertIn("fallback", self.orchestrator.components)

            # Verifica se foi injetado no AI Agent
            self.assertEqual(mock_ai_agent.fallback_system, mock_fallback_instance)

    @patch("src.core.orchestrator.logger")
    def test_logging_during_initialization(self, mock_logger):
        """Testa logging detalhado durante inicialização"""
        with patch("src.core.orchestrator.SecurityManager") as mock_security:
            with patch("src.core.orchestrator.IOTManager") as mock_iot:
                with patch("src.core.orchestrator.FallbackSystem") as mock_fallback:
                    with patch.object(
                        self.orchestrator, "_init_interface_orchestration"
                    ):
                        self.orchestrator.initialize_stark_system()

        # Verifica se logging de início e fim foram chamados
        info_calls = [call for call in mock_logger.info.call_args_list if call[0]]
        self.assertTrue(len(info_calls) > 0)

        # Verifica se mensagem de sucesso foi logada
        success_logged = any(
            "Stark 2.0 Inicializado" in str(call) for call in info_calls
        )
        self.assertTrue(success_logged)


class TestStarkOrchestratorIntegration(unittest.TestCase):
    """Testes de integração para situações mais realistas"""

    def setUp(self):
        """Setup para testes de integração"""
        self.mock_jarvis = Mock()
        self.mock_jarvis.shutdown_manager = Mock()
        self.mock_jarvis.ai_agent = Mock()
        self.mock_jarvis.window_manager = Mock()

        self.orchestrator = StarkOrchestrator(self.mock_jarvis)

    def test_complete_workflow_success_scenario(self):
        """Testa fluxo completo de inicialização bem-sucedida"""
        with patch("src.core.orchestrator.SecurityManager") as mock_security:
            with patch("src.core.orchestrator.IOTManager") as mock_iot:
                with patch("src.core.orchestrator.FallbackSystem") as mock_fallback:

                    # Setup mocks para sucesso
                    mock_security.return_value = Mock()

                    mock_iot_instance = Mock()
                    mock_iot_instance.is_configured = True
                    mock_iot.return_value = mock_iot_instance

                    mock_fallback.return_value = Mock()

                    with patch.object(
                        self.orchestrator, "_init_interface_orchestration"
                    ):
                        # Executa inicialização completa
                        self.orchestrator.initialize_stark_system()

                    # Verifica estado final
                    self.assertTrue(self.orchestrator.is_ready)
                    self.assertEqual(len(self.orchestrator.components), 3)

                    # Verifica health
                    health = self.orchestrator.get_system_health()
                    self.assertTrue(self.orchestrator.is_system_healthy())

                    # Verifica system info
                    info = self.orchestrator.get_system_info()
                    self.assertTrue(info["is_ready"])
                    self.assertTrue(info["system_healthy"])

    def test_complete_workflow_partial_failure_scenario(self):
        """Testa fluxo com falhas parciais mas sistema resiliente"""
        with patch(
            "src.core.orchestrator.SecurityManager",
            side_effect=Exception("Security failed"),
        ):
            with patch("src.core.orchestrator.IOTManager") as mock_iot:
                with patch("src.core.orchestrator.FallbackSystem") as mock_fallback:

                    # IoT funciona mas não configurado
                    mock_iot_instance = Mock()
                    mock_iot_instance.is_configured = False
                    mock_iot.return_value = mock_iot_instance

                    # Fallback funciona
                    mock_fallback.return_value = Mock()

                    with patch.object(
                        self.orchestrator, "_init_interface_orchestration"
                    ):
                        # Executa inicialização
                        self.orchestrator.initialize_stark_system()

                    # Sistema não está completamente pronto mas parcialmente funcional
                    self.assertFalse(self.orchestrator.is_ready)

                    # Alguns componentes funcionaram
                    self.assertIn("iot", self.orchestrator.components)
                    self.assertIn("fallback", self.orchestrator.components)
                    self.assertNotIn("security", self.orchestrator.components)

                    # Health reflete estado parcial
                    health = self.orchestrator.get_system_health()
                    self.assertEqual(health["iot"], "DEGRADED")
                    self.assertEqual(health["security"], "OFFLINE")


if __name__ == "__main__":
    # Configura logging para testes
    logging.basicConfig(level=logging.DEBUG)

    # Executa testes
    unittest.main(verbosity=2)
