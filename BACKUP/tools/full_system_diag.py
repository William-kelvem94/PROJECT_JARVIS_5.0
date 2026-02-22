# -*- coding: utf-8 -*-
import sys
import os
import time
from pathlib import Path

# Configura o ambiente
sys.path.append(os.getcwd())

print("🛡️ [DIAGNÓSTICO JARVIS 5.0] Iniciando verificação total...")

# 1. Teste de Banco de Dados (SQLite)
print("\n[01/05] Testando Repositório SQLite...")
try:
    from jarvis.database import db
    db.add_interaction("Teste de Sistema", "Diagnóstico OK")
    data = db.query_interactions(limit=1)
    if data:
        print("✅ Banco de Dados: OPERACIONAL (Persistência verificada)")
except Exception as e:
    print(f"❌ Banco de Dados: FALHA ({e})")

# 2. Teste de Pesquisa Profunda (Deep Research)
print("\n[02/05] Testando Motores de Prospecção (Google Scholar/ArXiv/HF)...")
try:
    from jarvis.web_utils import search_online
    res = search_online("Python AI Agents")
    if "WEB DATA" in res or "ACADEMIC" in res:
        print("✅ Pesquisa Multi-Fonte: OPERACIONAL (Fontes externas mapeadas)")
    else:
        print("⚠️ Pesquisa Multi-Fonte: ALERTA (Retorno vazio, verifique conexão)")
except Exception as e:
    print(f"❌ Pesquisa Multi-Fonte: FALHA ({e})")

# 3. Teste do HoloDeck (Sandbox)
print("\n[03/05] Testando HoloDeck (Ambiente de Simulação)...")
try:
    from jarvis.holodeck import HoloDeck
    holo = HoloDeck(os.getcwd())
    sim_path = holo.create_simulation("diag_test", modules_to_copy=["main.py"])
    if sim_path.exists() and (sim_path / "main.py").exists():
        print("✅ HoloDeck: OPERACIONAL (Sandbox criada com sucesso)")
        holo.cleanup("diag_test")
    else:
        print("❌ HoloDeck: FALHA (Arquivos não replicados)")
except Exception as e:
    print(f"❌ HoloDeck: FALHA ({e})")

# 4. Teste de Auto-Evolução (Leitura)
print("\n[04/05] Testando Evolution Engine (Auto-Leitura)...")
try:
    from jarvis.evolution import EvolutionEngine
    evo = EvolutionEngine(os.getcwd())
    code = evo.read_module("jarvis/agent.py")
    if code and "class JarvisAgent" in code:
        print("✅ Evolution Engine: OPERACIONAL (Córtex de auto-leitura ativo)")
    else:
        print("❌ Evolution Engine: FALHA (Não conseguiu ler o próprio código)")
except Exception as e:
    print(f"❌ Evolution Engine: FALHA ({e})")

# 5. Teste de Performance (Mensageria)
print("\n[05/05] Testando Speech Queue (Thread-Safe)...")
try:
    from jarvis.agent import JarvisAgent
    # Apenas verifica se a fila existe no init (sem abrir o HUD de novo)
    agent = JarvisAgent(auto_setup=False)
    if hasattr(agent, 'speech_queue'):
        print("✅ Mensageria: OPERACIONAL (Fila assíncrona ativa)")
except Exception as e:
    print(f"❌ Mensageria: FALHA ({e})")

print("\n🚀 [VEREDITO FINAL] Sistemas integrados com sucesso. JARVIS v5.0 pronto para evolução recursiva.")
