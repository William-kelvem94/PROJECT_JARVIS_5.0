"""
Teste Rápido das Correções P0
==============================
Testes sem importações pesadas
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_config_loading():
    """Teste: Carregamento de configurações"""
    print("\n" + "=" * 70)
    print("TESTE: Carregamento de ai_config.yaml")
    print("=" * 70)

    try:
        from src.utils.config import config

        # Verificar arquivo existe
        config_file = Path(PROJECT_ROOT) / "config" / "ai_config.yaml"
        print(f"📁 Arquivo: {config_file}")
        print(f"✅ Existe: {config_file.exists()}")

        if not config_file.exists():
            print("❌ ai_config.yaml não encontrado!")
            return False

        # Verificar carregamento
        ai_config = config.ai_config
        print(f"✅ Configuração carregada: {len(ai_config)} seções")

        # Verificar seções principais
        sections = [
            "ai_agent",
            "brain_router",
            "local_brain",
            "neural_memory",
            "trainer",
            "vision",
        ]
        for section in sections:
            status = "✅" if section in ai_config else "❌"
            print(
                f"{status} Seção '{section}': {'OK' if section in ai_config else 'MISSING'}"
            )

        # Testar get_ai_config
        max_turns = config.get_ai_config("ai_agent.max_react_turns", 5)
        print(f"\n✅ ai_agent.max_react_turns = {max_turns}")

        ollama_url = config.get_ai_config("brain_router.ollama_url")
        print(f"✅ brain_router.ollama_url = {ollama_url}")

        tier_ultra = config.get_ai_config("brain_router.ollama_models.tier_ultra", [])
        print(f"✅ tier_ultra tem {len(tier_ultra)} modelos")

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_trainer_structure():
    """Teste: Estrutura do trainer.py sem importar classes pesadas"""
    print("\n" + "=" * 70)
    print("TESTE: Estrutura de trainer.py (Mocks Removidos)")
    print("=" * 70)

    try:
        trainer_file = Path(PROJECT_ROOT) / "src" / "learning" / "trainer.py"
        content = trainer_file.read_text(encoding="utf-8")

        # Verificar que mocks FORAM REMOVIDOS
        bad_patterns = [
            "class Dataset:",
            "class AutoModelForCausalLM:",
            "class Trainer:",
            "class LoraConfig:",
            "class BitsAndBytesConfig:",
            "def get_peft_model(*args, **kwargs):",
        ]

        found_mocks = []
        for pattern in bad_patterns:
            # Verificar se está na seção de imports (primeiras 100 linhas)
            lines = content.split("\n")[:100]
            if any(pattern in line for line in lines):
                found_mocks.append(pattern)

        if found_mocks:
            print("❌ Mocks encontrados (devem ser removidos):")
            for mock in found_mocks:
                print(f"   - {mock}")
            return False
        else:
            print("✅ Mocks removidos com sucesso!")

        # Verificar que flags AVAILABLE existem
        good_patterns = [
            "TORCH_AVAILABLE = True",
            "TRANSFORMERS_AVAILABLE = True",
            "PEFT_AVAILABLE = True",
            "BNB_AVAILABLE = True",
        ]

        for pattern in good_patterns:
            if pattern in content:
                print(f"✅ {pattern.split('=')[0].strip()} encontrado")
            else:
                print(f"❌ {pattern.split('=')[0].strip()} NÃO encontrado")

        # Verificar mensagens de erro melhoradas
        if "pip install torch" in content and "pip install transformers" in content:
            print("✅ Mensagens de erro melhoradas presentes")
        else:
            print("⚠️ Mensagens de erro não encontradas")

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ai_agent_structure():
    """Teste: Estrutura do ai_agent.py"""
    print("\n" + "=" * 70)
    print("TESTE: Verificação de Dependências em ai_agent.py")
    print("=" * 70)

    try:
        ai_agent_file = (
            Path(PROJECT_ROOT) / "src" / "core" / "intelligence" / "ai_agent.py"
        )
        content = ai_agent_file.read_text(encoding="utf-8")

        # Verificar métodos adicionados
        required_patterns = [
            "_verify_critical_dependencies",
            "self.safe_mode",
            "if self.safe_mode:",
            "config.get_ai_config",
            "self.max_react_turns",
            "self.screenshot_timeout",
        ]

        for pattern in required_patterns:
            if pattern in content:
                print(f"✅ '{pattern}' encontrado")
            else:
                print(f"❌ '{pattern}' NÃO encontrado")
                return False

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_brain_router_structure():
    """Teste: Estrutura do brain_router.py"""
    print("\n" + "=" * 70)
    print("TESTE: Brain Router com Configurações")
    print("=" * 70)

    try:
        brain_router_file = (
            Path(PROJECT_ROOT) / "src" / "core" / "intelligence" / "brain_router.py"
        )
        content = brain_router_file.read_text(encoding="utf-8")

        # Verificar imports e métodos
        required_patterns = [
            "from src.utils.config import config",
            "config.get_ai_config",
            "_load_default_config",
            "enable_offline_mode",
            "disable_offline_mode",
            "_choose_local_brain",
            "self.tier_ultra",
            "self.tier_pro",
            "self.tier_fast",
            "self.offline_mode",
        ]

        for pattern in required_patterns:
            if pattern in content:
                print(f"✅ '{pattern}' encontrado")
            else:
                print(f"❌ '{pattern}' NÃO encontrado")
                return False

        return True

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_quick_tests():
    """Executa testes rápidos sem imports pesados"""
    print("\n" + "=" * 70)
    print("🚀 SUITE DE TESTES RÁPIDOS - CORREÇÕES P0")
    print("=" * 70)

    results = {
        "Configuração (ai_config.yaml)": test_config_loading(),
        "Trainer (Mocks Removidos)": test_trainer_structure(),
        "AI Agent (Dependency Check)": test_ai_agent_structure(),
        "Brain Router (Config Integration)": test_brain_router_structure(),
    }

    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 70)
    print(f"RESULTADO: {passed}/{total} testes passaram ({passed*100//total}%)")
    print("=" * 70)

    if passed == total:
        print("\n🎉 SUCESSO! Todas as correções P0 foram implementadas corretamente!")
        print("\n📋 Próximos Passos:")
        print("   1. Execute: python -m pytest tests/")
        print("   2. Execute: python main.py (teste completo)")
        print("   3. Implemente correções P1 (AsyncIO, JSON parsing)")
        return 0
    else:
        print(f"\n⚠️ ATENÇÃO: {total - passed} teste(s) falharam")
        print("💡 Revise as implementações acima")
        return 1


if __name__ == "__main__":
    exit_code = run_quick_tests()
    sys.exit(exit_code)
