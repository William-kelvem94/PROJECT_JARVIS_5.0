
import asyncio
import logging
import sys
import os

# Garantir que o root do projeto está no path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurar logs para ignorar avisos de imports
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("TEST-AI")

async def test_jarvis():
    try:
        print("--- INICIANDO TESTE DE CONEXÃO JARVIS 5.0 ---")
        
        # Importação tardia para evitar erros de inicialização global
        from src.core.intelligence.ai_agent import ai_agent
        
        # Teste 1: Camada de Instinto (Sempre deve funcionar)
        print("\n[Teste 1] Camada de Instinto (Resposta Imediata):")
        res1 = await ai_agent.process_command("Olá Jarvis")
        print(f"JARVIS: {res1}")
        
        # Teste 2: Camada Cognitiva (LLM)
        # Se o Ollama falhar, o código tem fallback para LocalBrain (Micro-LLM)
        print("\n[Teste 2] Camada Cognitiva (Adaptabilidade e Fallback):")
        print("(Este passo pode demorar 30s se precisar carregar o modelo ou fazer fallback)")
        res2 = await ai_agent.process_command("Qual a sua missão principal?")
        print(f"JARVIS: {res2}")
        
        print("\n--- TESTE FINALIZADO ---")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[ERRO NO TESTE] Falha ao conectar: {e}")

if __name__ == "__main__":
    # Rodar o loop de eventos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_jarvis())
