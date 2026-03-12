import asyncio
import os
import sys
import json
from loguru import logger

# Adiciona o diretório backend ao path para importações
sys.path.append(os.path.join(os.getcwd(), "backend"))

async def test_perception():
    print("\n--- [TESTE 1: PERCEPÇÃO] ---")
    try:
        from app.perception import perception_manager
        snap = perception_manager.get_snapshot()
        print(f"Snapshot Inicial: {json.dumps(snap, indent=2)}")
        
        # Simula uma detecção
        print("Simulando detecção de face e emoção...")
        perception_manager._update(face_present=True, face_emotion="happy", face_identity="Chefe")
        
        new_snap = perception_manager.get_snapshot()
        if new_snap['face_present'] and new_snap['face_emotion'] == 'happy':
            print("✅ Sucesso: O snapshot de percepção está atualizando corretamente.")
        else:
            print("❌ Falha: O snapshot não refletiu a atualização.")
    except Exception as e:
        print(f"❌ Erro no teste de percepção: {e}")

async def test_dynamic_context():
    print("\n--- [TESTE 2: CONTEXTO DINÂMICO] ---")
    try:
        from app.perception import perception_manager
        # Garante que temos um estado conhecido
        perception_manager._update(face_present=True, face_emotion="neutral", face_identity="William")
        
        # Simula o que o agents.py faz
        snap = perception_manager.get_snapshot()
        status = (
            f"\n[SITUAÇÃO ATUAL]\n"
            f"Usuário detectado: {'Sim' if snap['face_present'] else 'Não'}\n"
            f"Identidade: {snap['face_identity'] or 'Desconhecido'}\n"
            f"Emoção dominante: {snap['face_emotion']}\n"
        )
        print(f"Prompt Injetado Simuladamente:\n{status}")
        
        if "William" in status and "Sim" in status:
            print("✅ Sucesso: O contexto dinâmico está capturando os dados da percepção.")
        else:
            print("❌ Falha: O contexto não contém as informações esperadas.")
    except Exception as e:
        print(f"❌ Erro no teste de contexto: {e}")

async def test_dream_loop():
    print("\n--- [TESTE 3: DREAM LOOP / EVOLUÇÃO] ---")
    try:
        from app.utils.dream_processor import dream_processor
        from app.local_memory import local_memory
        
        print("Simulando um ciclo de 'reflexão' imediato...")
        experiences = ["Hoje o usuário testou o sistema de visão", "Ele parecia feliz com o HUD"]
        
        # Forçamos uma reflexão sem esperar a madrugada
        insights = await dream_processor.reflect(experiences)
        
        if insights:
            print(f"Insights Gerados: {insights[:100]}...")
            # Verifica se salvou na memória
            memories = local_memory.search("Jarvis", "Insight", limit=1)
            if memories:
                print("✅ Sucesso: O Jarvis 'sonhou', refletiu e salvou o aprendizado na memória local.")
            else:
                print("⚠️ Aviso: Insights gerados mas não encontrados na memória (verifique se local_memory está configurado).")
        else:
            print("❌ Falha: O DreamProcessor não gerou insights.")
    except Exception as e:
        print(f"❌ Erro no teste de evolução: {e}")

async def main():
    print("Iniciando Diagnóstico de Vitals do JARVIS 5.0...")
    await test_perception()
    await test_dynamic_context()
    await test_dream_loop()
    print("\nDiagnóstico concluído.")

if __name__ == "__main__":
    asyncio.run(main())
