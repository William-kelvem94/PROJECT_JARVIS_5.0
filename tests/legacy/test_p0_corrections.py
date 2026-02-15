"""
Teste das Correções P0 (Prioridade Máxima)
==========================================
1. Verificação de Mocks Removidos (trainer.py)
2. Carregamento de Configurações (ai_config.yaml)
3. Verificação de Dependências (ai_agent.py)
4. Brain Router com Config (brain_router.py)
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_1_trainer_no_mocks():
    """Teste 1: Verificar que mocks foram removidos"""
    print("\n" + "="*60)
    print("TESTE 1: Mocks Removidos em trainer.py")
    print("="*60)
    
    try:
        from src.learning.trainer import (
            TORCH_AVAILABLE,
            TRANSFORMERS_AVAILABLE,
            PEFT_AVAILABLE,
            BNB_AVAILABLE,
            Dataset,
            AutoModelForCausalLM,
            LoraConfig,
            BitsAndBytesConfig
        )
        
        print(f"✅ TORCH_AVAILABLE: {TORCH_AVAILABLE}")
        print(f"✅ TRANSFORMERS_AVAILABLE: {TRANSFORMERS_AVAILABLE}")
        print(f"✅ PEFT_AVAILABLE: {PEFT_AVAILABLE}")
        print(f"✅ BNB_AVAILABLE: {BNB_AVAILABLE}")
        
        # Verificar que são None se não disponíveis (não mocks)
        if not TORCH_AVAILABLE:
            assert Dataset is None, "Dataset deveria ser None, não mock"
            print("✅ Dataset = None (correto, não é mock)")
        
        if not TRANSFORMERS_AVAILABLE:
            assert AutoModelForCausalLM is None, "AutoModelForCausalLM deveria ser None"
            print("✅ AutoModelForCausalLM = None (correto)")
        
        if not PEFT_AVAILABLE:
            assert LoraConfig is None, "LoraConfig deveria ser None"
            print("✅ LoraConfig = None (correto)")
        
        if not BNB_AVAILABLE:
            assert BitsAndBytesConfig is None, "BitsAndBytesConfig deveria ser None"
            print("✅ BitsAndBytesConfig = None (correto)")
        
        print("\n✅ TESTE 1 PASSOU: Mocks removidos com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 1 FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_ai_config_loading():
    """Teste 2: Verificar carregamento de ai_config.yaml"""
    print("\n" + "="*60)
    print("TESTE 2: Carregamento de ai_config.yaml")
    print("="*60)
    
    try:
        from src.utils.config import config
        
        # Verificar que ai_config foi carregado
        ai_config = config.ai_config
        print(f"✅ ai_config carregado: {len(ai_config)} seções")
        
        # Verificar seções principais
        required_sections = [
            'ai_agent',
            'brain_router',
            'local_brain',
            'neural_memory',
            'trainer',
            'vision'
        ]
        
        for section in required_sections:
            if section in ai_config:
                print(f"✅ Seção '{section}' encontrada")
            else:
                print(f"⚠️ Seção '{section}' não encontrada")
        
        # Testar get_ai_config com notação de ponto
        max_turns = config.get_ai_config('ai_agent.max_react_turns', 5)
        print(f"✅ ai_agent.max_react_turns = {max_turns}")
        
        ollama_url = config.get_ai_config('brain_router.ollama_url', 'http://localhost:11434')
        print(f"✅ brain_router.ollama_url = {ollama_url}")
        
        tier_ultra = config.get_ai_config('brain_router.ollama_models.tier_ultra', [])
        print(f"✅ brain_router.ollama_models.tier_ultra = {tier_ultra}")
        
        print("\n✅ TESTE 2 PASSOU: ai_config.yaml carregado com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 2 FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_dependency_verification():
    """Teste 3: Verificar verificação de dependências no AIAgent"""
    print("\n" + "="*60)
    print("TESTE 3: Verificação de Dependências (ai_agent.py)")
    print("="*60)
    
    try:
        from src.core.intelligence.ai_agent import AIAgent
        
        # Criar instância do AIAgent
        agent = AIAgent()
        
        print(f"✅ AIAgent criado")
        print(f"✅ safe_mode = {agent.safe_mode}")
        
        if agent.safe_mode:
            print("⚠️ Sistema em MODO SEGURO - dependências críticas faltando")
            print("💡 Isso é esperado se screen_capture ou action_controller não estiverem disponíveis")
        else:
            print("✅ Todas as dependências críticas disponíveis")
        
        # Verificar se max_react_turns foi carregado do config
        print(f"✅ max_react_turns = {agent.max_react_turns}")
        print(f"✅ screenshot_timeout = {agent.screenshot_timeout}")
        
        # Testar método _verify_critical_dependencies existe
        assert hasattr(agent, '_verify_critical_dependencies'), \
            "Método _verify_critical_dependencies não encontrado"
        print("✅ Método _verify_critical_dependencies existe")
        
        print("\n✅ TESTE 3 PASSOU: Verificação de dependências implementada!")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 3 FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_brain_router_config():
    """Teste 4: Verificar Brain Router usando config"""
    print("\n" + "="*60)
    print("TESTE 4: Brain Router com Configurações")
    print("="*60)
    
    try:
        from src.core.intelligence.brain_router import brain_router
        
        print(f"✅ BrainRouter carregado")
        print(f"✅ ollama_url = {brain_router.ollama_url}")
        print(f"✅ ollama_timeout = {brain_router.ollama_timeout}")
        print(f"✅ offline_mode = {brain_router.offline_mode}")
        
        # Verificar tiers carregados
        print(f"\n📊 Tiers Configurados:")
        print(f"  TIER ULTRA: {brain_router.tier_ultra}")
        print(f"  TIER PRO: {brain_router.tier_pro}")
        print(f"  TIER FAST: {brain_router.tier_fast}")
        
        # Verificar hardware requirements
        print(f"\n💻 Hardware Requirements:")
        print(f"  ULTRA: {brain_router.hw_tier_ultra}")
        print(f"  PRO: {brain_router.hw_tier_pro}")
        print(f"  FAST: {brain_router.hw_tier_fast}")
        
        # Verificar métodos novos
        assert hasattr(brain_router, 'enable_offline_mode'), \
            "Método enable_offline_mode não encontrado"
        assert hasattr(brain_router, 'disable_offline_mode'), \
            "Método disable_offline_mode não encontrado"
        assert hasattr(brain_router, '_choose_local_brain'), \
            "Método _choose_local_brain não encontrado"
        print("✅ Métodos offline implementados")
        
        # Testar escolha de cérebro
        from src.core.intelligence.brain_router import PrivacyLevel, LatencyRequirement
        brain_choice = brain_router.choose_brain(
            task_complexity=0.5,
            privacy_level=PrivacyLevel.LOW,
            latency_requirement=LatencyRequirement.MODERATE
        )
        print(f"\n✅ Escolha de cérebro (complexity=0.5): {brain_choice}")
        
        # Testar modo offline
        brain_router.enable_offline_mode()
        print(f"✅ Modo offline ativado: {brain_router.offline_mode}")
        
        offline_choice = brain_router.choose_brain(task_complexity=0.9)
        print(f"✅ Escolha em modo offline: {offline_choice}")
        
        brain_router.disable_offline_mode()
        print(f"✅ Modo offline desativado: {brain_router.offline_mode}")
        
        print("\n✅ TESTE 4 PASSOU: Brain Router usando configurações!")
        return True
        
    except Exception as e:
        print(f"\n❌ TESTE 4 FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Executa todos os testes P0"""
    print("\n" + "="*60)
    print("SUITE DE TESTES - CORREÇÕES P0")
    print("="*60)
    print("Testando implementação das correções de prioridade máxima")
    print("="*60)
    
    results = {
        "Teste 1 - Mocks Removidos": test_1_trainer_no_mocks(),
        "Teste 2 - Config Loading": test_2_ai_config_loading(),
        "Teste 3 - Dependency Check": test_3_dependency_verification(),
        "Teste 4 - Brain Router Config": test_4_brain_router_config(),
    }
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*60)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram")
    print("="*60)
    
    if passed == total:
        print("\n🎉 SUCESSO! Todas as correções P0 estão funcionando!")
        return 0
    else:
        print(f"\n⚠️ ATENÇÃO: {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
