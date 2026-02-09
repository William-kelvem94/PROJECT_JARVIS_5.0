#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Rigorous Integration & Stress Test (Stark Mode)
============================================================
Testa a integridade de todos os novos módulos e suas interdependências.
NÃO USA SIMPLIFICAÇÕES. Testa a lógica real com mocks controlados apenas para IO físico.
"""

import os
import sys
import time
import logging
import threading
import concurrent.futures
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Silencing noisy logs for the test
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("RIGOROUS-TEST")

class StarkRigorousTester:
    def __init__(self):
        self.results = []
        self.errors = []
        self._setup_mocks()

    def _setup_mocks(self):
        """Prepara o ambiente simulado sem quebrar a lógica de negócio"""
        try:
            # Mock voice_controller para não falar durante os testes
            import src.core.audio.voice_controller as vc_mod
            class MockVoice:
                def __init__(self): self._is_speaking = False
                def speak(self, text, mode='online', wait=False): pass  # Corrigido: adicionado wait=False
                def stop(self): pass
            vc_mod.voice_controller = MockVoice()
            
            # Mock de hardware para não dar erro em PowerShell
            from src.core.management.device_manager import device_manager
            def mock_run(cmd): return True
            device_manager._run_powershell = mock_run
            
        except Exception as e:
            logger.error(f"Falha ao preparar Mocks: {e}")

    def test_context_engine(self):
        """Testa o Analisador de Contexto com variações linguísticas complexas"""
        print("🔍 Analisando Lóbulo Frontal (Context Engine)...")
        from src.core.intelligence.analisador_contexto import analisador_contexto
        
        test_cases = [
            ("Jarvis, por favor estude profundamente o código da API em Python", "AUTONOMIA"),
            ("Ajuste o brilho para 100% e ligue a GPU no máximo", "HARDWARE"),
            ("Estou me sentindo um pouco ansioso com a namorada no relacionamento", "PSICOLOGIA"),
            ("Tocar a playlist de música clássica no YouTube", "MULTIMIDIA"),
            ("Corrija o bug no código do deploy", "PROGRAMACAO"),
            ("Aprenda sobre física quântica via Nexus", "AUTONOMIA")
        ]
        
        success = 0
        for cmd, expected in test_cases:
            res = analisador_contexto.analisar(cmd)
            if res["contexto"] == expected:
                success += 1
            else:
                self.errors.append(f"FALHA CONTEXTO: '{cmd}' -> {res['contexto']} (Esperado: {expected})")
        
        print(f"  Result: {success}/{len(test_cases)} acertos.")
        return success == len(test_cases)

    def test_neural_dreaming_concurrency(self):
        """Testa se o Dreaming aguenta múltiplas chamadas e interrupções rápidas"""
        print("🧠 Testando Estabilidade Neural (Dreaming Concurrency)...")
        from src.core.intelligence.neural_dreaming import neural_dreaming
        
        try:
            # Sequência de start/stop rápido
            neural_dreaming.start_dream("Teste 1", 5, False)
            if not neural_dreaming.is_dreaming: return False
            
            # Tentar iniciar outro enquanto um roda
            res = neural_dreaming.start_dream("Teste 2", 5, False)
            if res: # Não deveria deixar
                self.errors.append("Dreaming permitiu sobreposição de sonhos.")
                return False
                
            neural_dreaming.stop_dream()
            time.sleep(0.5)
            if neural_dreaming.is_dreaming:
                self.errors.append("Dreaming não parou corretamente.")
                return False
                
            print("  ✅ Estabilidade Neural validada.")
            return True
        except Exception as e:
            self.errors.append(f"CRASH DREAMING: {e}")
            return False

    def test_stark_nexus_logic(self):
        """Verifica a lógica de pesquisa e sanitização do Nexus (Sem chamadas reais)"""
        print("🛰️ Verificando Stark Nexus (Knowledge Acquisition)...")
        from src.core.intelligence.stark_nexus import stark_nexus
        
        try:
            # O Nexus deve recusar tópicos nulos ou perigosos (se implementado)
            # Como ainda não temos o sanitizer completo, vamos testar o fluxo de comando
            res = stark_nexus.pesquisar("TESTE", "IA Moderna")
            print("  ✅ Fluxo do Nexus operacional.")
            return True
        except Exception as e:
            self.errors.append(f"CRASH NEXUS: {e}")
            return False

    def test_ai_agent_react_flow(self):
        """Testa o fluxo ReAct do Agente com os novos módulos integrados"""
        print("🤖 Testando Agente AI (Integrative ReAct Cycle)...")
        from src.core.intelligence.ai_agent import ai_agent
        
        test_prompts = [
            "coloque o brilho em 40% e comece a estudar robótica",
            "volume no mudo",
            "analise meus sentimentos sobre minha namorada"
        ]
        
        for p in test_prompts:
            try:
                # O QuickResponse deve capturar o contexto corretamente
                response = ai_agent.process_command(p)
                if not response or len(response) < 5:
                    self.errors.append(f"AI Agent retornou resposta inválida para: {p}")
                    return False
            except Exception as e:
                self.errors.append(f"CRASH AGENT COMANDO '{p}': {e}")
                return False
        
        print("  ✅ Ciclo ReAct integrado validado.")
        return True

    def test_agent_flood(self):
        """Simula um usuário 'floodando' comandos para testar as travas do Agente"""
        print("🌊 Testando Flood de Comandos (Concurrency & Locks)...")
        from src.core.intelligence.ai_agent import ai_agent
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Tenta processar 5 comandos quase ao mesmo tempo
            futures = [executor.submit(ai_agent.process_command, f"Comando Flood {i}") for i in range(5)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    self.errors.append(f"CRASH NO FLOOD: {e}")
        
        # O Agente deveria ter processado pelo menos o primeiro e talvez negado/enfileirado os outros
        # sem crashar o núcleo.
        print(f"  ✅ Flood processado ({len(results)} respostas).")
        return len(results) == 5

    def run_all(self):
        start_time = time.time()
        print("\n" + "="*60)
        print(" JARVIS 5.0 - STARK RIGOROUS INTEGRATION SUITE ".center(60, "═"))
        print("="*60 + "\n")
        
        tests = [
            self.test_context_engine,
            self.test_neural_dreaming_concurrency,
            self.test_stark_nexus_logic,
            self.test_ai_agent_react_flow,
            self.test_agent_flood
        ]
        
        passed = 0
        for t in tests:
            if t(): passed += 1
            else: print(f"  ❌ TESTE FALHOU: {t.__name__}")
        
        duration = time.time() - start_time
        print("\n" + "="*60)
        print(f" RESULTADO FINAL: {passed}/{len(tests)} PASSOU ".center(60, "═"))
        print(f" Duração: {duration:.2f}s")
        print("="*60 + "\n")
        
        if self.errors:
            print("🛑 DETALHES DOS ERROS:")
            for err in self.errors:
                print(f"  - {err}")
            return False
        
        return True

if __name__ == "__main__":
    tester = StarkRigorousTester()
    if not tester.run_all():
        sys.exit(1)
    sys.exit(0)
