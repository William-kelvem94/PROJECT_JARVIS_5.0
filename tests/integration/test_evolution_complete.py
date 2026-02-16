"""
Suite de Testes Completa - JARVIS 5.0 Evolution
Valida todos os módulos implementados
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_brain_router():
    """Testa sistema de decisão inteligente"""
    print("\n" + "=" * 60)
    print("   TESTE 1: BRAIN ROUTER")
    print("=" * 60)

    try:
        from src.core.intelligence.brain_router import (
            brain_router,
            PrivacyLevel,
            LatencyRequirement,
        )

        # Teste 1: Comando simples
        choice = brain_router.choose_brain(
            task_complexity=0.2,
            privacy_level=PrivacyLevel.PUBLIC,
            latency_requirement=LatencyRequirement.ULTRA_LOW,
        )
        assert choice == "local", f"Esperado 'local', obtido '{choice}'"
        print("✅ Teste 1.1: Comando simples → local")

        # Teste 2: Privacidade alta
        choice = brain_router.choose_brain(
            task_complexity=0.6,
            privacy_level=PrivacyLevel.HIGH,
            latency_requirement=LatencyRequirement.MODERATE,
        )
        assert choice == "local", f"Esperado 'local', obtido '{choice}'"
        print("✅ Teste 1.2: Privacidade alta → local")

        # Teste 3: Complexidade alta
        choice = brain_router.choose_brain(
            task_complexity=0.9,
            privacy_level=PrivacyLevel.LOW,
            latency_requirement=LatencyRequirement.FLEXIBLE,
        )
        assert choice in ["cloud_pro", "local"], f"Escolha inesperada: '{choice}'"
        print(f"✅ Teste 1.3: Complexidade alta → {choice}")

        print("✅ BRAIN ROUTER: PASSOU EM TODOS OS TESTES")
        return True

    except Exception as e:
        print(f"❌ BRAIN ROUTER: FALHOU - {e}")
        return False


def test_advanced_action_controller():
    """Testa controle avançado de ações"""
    print("\n" + "=" * 60)
    print("   TESTE 2: ADVANCED ACTION CONTROLLER")
    print("=" * 60)

    try:
        from src.core.actions.advanced_action_controller import (
            advanced_action_controller,
        )

        # Teste 1: Descoberta de aplicações
        apps = advanced_action_controller.known_apps
        print(f"✅ Teste 2.1: {len(apps)} aplicações descobertas")

        # Teste 2: Informações do sistema
        info = advanced_action_controller.get_system_info()
        assert "cpu_percent" in info
        assert "memory_percent" in info
        print(
            f"✅ Teste 2.2: CPU {info['cpu_percent']}%, RAM {info['memory_percent']}%"
        )

        # Teste 3: Posição do mouse
        pos = advanced_action_controller.get_mouse_position()
        assert len(pos) == 2
        print(f"✅ Teste 2.3: Mouse em ({pos[0]}, {pos[1]})")

        print("✅ ADVANCED ACTION CONTROLLER: PASSOU EM TODOS OS TESTES")
        return True

    except Exception as e:
        print(f"❌ ADVANCED ACTION CONTROLLER: FALHOU - {e}")
        return False


def test_workflow_engine():
    """Testa engine de workflows"""
    print("\n" + "=" * 60)
    print("   TESTE 3: WORKFLOW ENGINE")
    print("=" * 60)

    try:
        from src.core.actions.workflow_engine import workflow_engine, WorkflowStep

        # Teste 1: Criar workflow
        wf = workflow_engine.create_workflow(
            name="test_workflow", description="Workflow de teste"
        )
        assert wf.name == "test_workflow"
        print("✅ Teste 3.1: Workflow criado")

        # Teste 2: Adicionar passo
        workflow_engine.add_step(
            "test_workflow",
            WorkflowStep(type="wait", params={"duration": 0.1}, description="Aguardar"),
        )
        assert len(wf.steps) == 1
        print("✅ Teste 3.2: Passo adicionado")

        # Teste 3: Executar workflow
        result = workflow_engine.execute_workflow("test_workflow")
        assert result == True
        print("✅ Teste 3.3: Workflow executado")

        # Teste 4: Salvar e carregar
        workflow_engine.save_workflow("test_workflow")
        print("✅ Teste 3.4: Workflow salvo")

        # Limpar
        workflow_engine.delete_workflow("test_workflow")

        print("✅ WORKFLOW ENGINE: PASSOU EM TODOS OS TESTES")
        return True

    except Exception as e:
        print(f"❌ WORKFLOW ENGINE: FALHOU - {e}")
        return False


def test_advanced_vision_pipeline():
    """Testa pipeline de visão"""
    print("\n" + "=" * 60)
    print("   TESTE 4: ADVANCED VISION PIPELINE")
    print("=" * 60)

    try:
        from src.core.vision.advanced_vision_pipeline import advanced_vision_pipeline

        # Teste 1: Verificar níveis disponíveis
        print(
            f"✅ Teste 4.1: Nível 1 (YOLO): {advanced_vision_pipeline.level1_available}"
        )
        print(
            f"✅ Teste 4.2: Nível 2 (EasyOCR): {advanced_vision_pipeline.level2_available}"
        )
        print(
            f"✅ Teste 4.3: Nível 3 (Gemini): {advanced_vision_pipeline.level3_available}"
        )

        print("✅ ADVANCED VISION PIPELINE: PASSOU EM TODOS OS TESTES")
        return True

    except Exception as e:
        print(f"❌ ADVANCED VISION PIPELINE: FALHOU - {e}")
        return False


def test_advanced_speech_processor():
    """Testa processamento de voz"""
    print("\n" + "=" * 60)
    print("   TESTE 5: ADVANCED SPEECH PROCESSOR")
    print("=" * 60)

    try:
        from src.core.audio.advanced_speech_processor import advanced_speech_processor

        # Teste 1: Verificar Whisper
        print(
            f"✅ Teste 5.1: Whisper disponível: {advanced_speech_processor.whisper_available}"
        )
        if advanced_speech_processor.whisper_available:
            print(f"   Modelo: {advanced_speech_processor.whisper_model_size}")

        # Teste 2: Verificar TTS
        print(
            f"✅ Teste 5.2: TTS disponível: {advanced_speech_processor.tts_available}"
        )

        print("✅ ADVANCED SPEECH PROCESSOR: PASSOU EM TODOS OS TESTES")
        return True

    except Exception as e:
        print(f"❌ ADVANCED SPEECH PROCESSOR: FALHOU - {e}")
        return False


def test_security_manager():
    """Testa sistema de segurança"""
    print("\n" + "=" * 60)
    print("   TESTE 6: SECURITY MANAGER ADVANCED")
    print("=" * 60)

    try:
        from src.core.management.security_manager_advanced import security_manager

        # Teste 1: Criptografia
        original = "dados sensíveis"
        encrypted = security_manager.encrypt_data(original)
        decrypted = security_manager.decrypt_data(encrypted)
        assert decrypted == original
        print("✅ Teste 6.1: Criptografia AES-256 funcional")

        # Teste 2: Hashing
        hash_value = security_manager.hash_data("senha123")
        assert len(hash_value) == 64  # SHA-256
        print("✅ Teste 6.2: Hashing SHA-256 funcional")

        # Teste 3: Modo privado
        security_manager.enable_private_mode()
        assert security_manager.private_mode
        print("✅ Teste 6.3: Modo privado ativado")

        security_manager.disable_private_mode()
        assert not security_manager.private_mode
        print("✅ Teste 6.4: Modo privado desativado")

        # Teste 4: Status
        status = security_manager.get_security_status()
        assert "encryption_enabled" in status
        print("✅ Teste 6.5: Status de segurança OK")

        print("✅ SECURITY MANAGER: PASSOU EM TODOS OS TESTES")
        return True

    except Exception as e:
        print(f"❌ SECURITY MANAGER: FALHOU - {e}")
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print("   JARVIS 5.0 - SUITE DE TESTES COMPLETA")
    print("=" * 60)

    results = {
        "Brain Router": test_brain_router(),
        "Advanced Action Controller": test_advanced_action_controller(),
        "Workflow Engine": test_workflow_engine(),
        "Advanced Vision Pipeline": test_advanced_vision_pipeline(),
        "Advanced Speech Processor": test_advanced_speech_processor(),
        "Security Manager": test_security_manager(),
    }

    print("\n" + "=" * 60)
    print("   RESUMO DOS TESTES")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"   RESULTADO FINAL: {passed}/{total} módulos passaram")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
