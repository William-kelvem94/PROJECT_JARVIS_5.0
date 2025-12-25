"""
Teste da correção do problema "pausa anderline midia"
"""

import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.assistant import JarvisAssistant

def log_debug(location, message, data, hypothesis_id="FIXED_TEST"):
    """Função auxiliar para logging"""
    try:
        # Criar diretório se não existir
        log_dir = r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor'
        os.makedirs(log_dir, exist_ok=True)
        
        with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "voice-debug",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Erro no log: {e}")

def test_fixed_voice():
    """Testa a correção do problema dos marcadores"""
    
    log_debug("test_fixed_voice.py:test_start", "Iniciando teste da correção", {})
    
    try:
        # Inicializar assistente
        assistant = JarvisAssistant()
        
        print("=== Teste da Correção dos Marcadores ===")
        
        # Frases que anteriormente causavam o problema
        test_phrases = [
            "Olá! Como você está?",
            "A qualidade da voz deve estar melhor agora.",
            "Vamos testar se não há mais marcadores estranhos.",
            "Este é um teste final para confirmar a correção."
        ]
        
        for i, phrase in enumerate(test_phrases):
            log_debug(
                "test_fixed_voice.py:test_phrase", 
                f"Testando frase corrigida {i+1}", 
                {"phrase": phrase},
                "A"
            )
            
            print(f"\n=== Teste {i+1} ===")
            print(f"Frase: {phrase}")
            print("Falando sem marcadores estranhos...")
            
            # Testar fala corrigida
            start_time = time.time()
            success = assistant.speech_engine.speak(phrase)
            end_time = time.time()
            
            log_debug(
                "test_fixed_voice.py:speech_result", 
                f"Resultado da fala corrigida {i+1}", 
                {
                    "success": success, 
                    "duration": end_time - start_time,
                    "phrase_length": len(phrase)
                },
                "A"
            )
            
            print(f"Sucesso: {success}")
            print(f"Duração: {end_time - start_time:.2f}s")
            
            # Pausa entre testes
            time.sleep(1)
        
        log_debug("test_fixed_voice.py:test_complete", "Teste da correção concluído", {})
        print("\n=== Teste da Correção Concluído ===")
        print("Agora a voz deve estar limpa, sem marcadores estranhos!")
        
    except Exception as e:
        log_debug(
            "test_fixed_voice.py:test_error", 
            "Erro durante o teste da correção", 
            {"error": str(e)},
            "A"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_fixed_voice()
