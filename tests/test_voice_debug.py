"""
Teste de voz com instrumentação para debug
"""

import json
import time
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.assistant import JarvisAssistant

def log_debug(location, message, data, hypothesis_id="TEST"):
    """Função auxiliar para logging"""
    try:
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

def test_voice_naturalness():
    """Testa a naturalidade da voz com diferentes configurações"""
    
    log_debug("test_voice_debug.py:test_start", "Iniciando teste de voz", {})
    
    try:
        # Inicializar assistente
        log_debug("test_voice_debug.py:init_assistant", "Inicializando assistente", {})
        assistant = JarvisAssistant()
        
        # Testar diferentes tipos de texto
        test_texts = [
            ("Olá! Como você está hoje?", "entusiasta"),
            ("Hmm, deixe-me pensar sobre isso...", "pensativo"),
            ("Desculpe, não consegui entender o que você disse.", "preocupado"),
            ("Perfeito! Consegui executar o comando com sucesso.", "aliviado"),
            ("Este é um texto mais longo para testar como a voz se comporta com frases maiores e mais complexas, incluindo pausas naturais e variações de entonação.", None)
        ]
        
        for i, (text, emotion) in enumerate(test_texts):
            log_debug(
                "test_voice_debug.py:test_text", 
                f"Testando texto {i+1}", 
                {"text": text, "emotion": emotion},
                "A,B,C"
            )
            
            print(f"\n=== Teste {i+1} ===")
            print(f"Texto: {text}")
            print(f"Emoção: {emotion}")
            print("Falando...")
            
            # Testar fala
            start_time = time.time()
            success = assistant.speech_engine.speak(text, emotion)
            end_time = time.time()
            
            log_debug(
                "test_voice_debug.py:speech_result", 
                f"Resultado da fala {i+1}", 
                {
                    "success": success, 
                    "duration": end_time - start_time,
                    "text_length": len(text)
                },
                "A,B,C,E"
            )
            
            print(f"Sucesso: {success}")
            print(f"Duração: {end_time - start_time:.2f}s")
            
            # Pausa entre testes
            time.sleep(2)
        
        log_debug("test_voice_debug.py:test_complete", "Teste concluído", {})
        print("\n=== Teste concluído ===")
        
    except Exception as e:
        log_debug(
            "test_voice_debug.py:test_error", 
            "Erro durante o teste", 
            {"error": str(e)},
            "A,B,C,D,E"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_voice_naturalness()
