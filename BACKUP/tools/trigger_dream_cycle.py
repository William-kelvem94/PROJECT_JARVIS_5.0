# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.getcwd())

from jarvis.learning.learning_engine import initialize_learning_systems

def force_fullstack_knowledge_evolution():
    print("🚀 [SISTEMA] Iniciando Ciclo de Sonho Forçado...")
    print("📚 [TEMA] Programação Fullstack e Linguagens Modernas")
    
    # Inicializa os sistemas
    project_root = os.getcwd()
    engine = initialize_learning_systems(project_root)
    
    if not engine:
        print("❌ [ERRO] Falha ao inicializar o Learning Engine.")
        return

    # Forçar a execução da sequência de sonho com tópicos prioritários
    priority = [
        "Desenvolvimento Web Fullstack Moderno",
        "Arquitetura de Microserviços em Python",
        "Padrões de Projeto em JavaScript/TypeScript",
        "Otimização de Consultas SQL e NoSQL",
        "Segurança em APIs RESTful"
    ]
    
    print(f"🧠 [EVOLUÇÃO] Analisando lacunas sobre: {', '.join(priority)}")
    
    # Executa manualmente a sequência de sonho
    engine.dream_cycle._execute_dream_sequence(priority_topics=priority)
    
    print("\n✅ [CONCLUÍDO] Pesquisa de programação realizada.")
    print(f"📊 [STATUS] {engine.dream_cycle.research_engine.get_research_status()}")
    print("💤 [DICA] O JARVIS agora tem novos dados para processar em fine-tuning.")

if __name__ == "__main__":
    force_fullstack_knowledge_evolution()
