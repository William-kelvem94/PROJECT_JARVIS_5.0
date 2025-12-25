"""
Teste específico para engines TTS locais e gratuitos
"""

import json
import time
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.assistant import JarvisAssistant

def log_debug(location, message, data, hypothesis_id="LOCAL_TEST"):
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

def test_local_engines():
    """Testa engines TTS locais especificamente"""
    
    log_debug("test_local_voice.py:test_start", "Iniciando teste de engines locais", {})
    
    try:
        # Inicializar assistente
        log_debug("test_local_voice.py:init_assistant", "Inicializando assistente", {})
        assistant = JarvisAssistant()
        
        # Verificar engines locais disponíveis
        if hasattr(assistant.speech_engine, 'local_tts') and assistant.speech_engine.local_tts:
            local_info = assistant.speech_engine.local_tts.get_engine_info()
            log_debug(
                "test_local_voice.py:local_engines_info", 
                "Informações dos engines locais", 
                local_info,
                "D"
            )
            print(f"Engines locais disponíveis: {local_info}")
        else:
            log_debug(
                "test_local_voice.py:no_local_engines", 
                "Nenhum engine local disponível", 
                {},
                "D"
            )
            print("Nenhum engine TTS local disponível")
        
        # Teste simples de naturalidade
        test_text = "Olá! Esta é uma frase de teste para verificar a naturalidade da voz local."
        
        log_debug(
            "test_local_voice.py:testing_naturalness", 
            "Testando naturalidade com engines locais", 
            {"text": test_text},
            "A,B,C,D"
        )
        
        print(f"\nTestando: {test_text}")
        print("Falando...")
        
        start_time = time.time()
        success = assistant.speech_engine.speak(test_text, emotion="entusiasta")
        end_time = time.time()
        
        log_debug(
            "test_local_voice.py:naturalness_result", 
            "Resultado do teste de naturalidade", 
            {
                "success": success, 
                "duration": end_time - start_time,
                "text_length": len(test_text)
            },
            "A,B,C,D,E"
        )
        
        print(f"Sucesso: {success}")
        print(f"Duração: {end_time - start_time:.2f}s")
        
        # Teste de diferentes emoções
        emotions_test = [
            ("Que ótimo! Funcionou perfeitamente.", "entusiasta"),
            ("Hmm, preciso pensar melhor sobre isso.", "pensativo"),
            ("Desculpe, algo deu errado aqui.", "preocupado"),
            ("Ah, agora sim! Problema resolvido.", "aliviado")
        ]
        
        for text, emotion in emotions_test:
            print(f"\nTestando emoção '{emotion}': {text}")
            success = assistant.speech_engine.speak(text, emotion=emotion)
            log_debug(
                "test_local_voice.py:emotion_test", 
                f"Teste de emoção {emotion}", 
                {"text": text, "emotion": emotion, "success": success},
                "B,C"
            )
            time.sleep(1)
        
        log_debug("test_local_voice.py:test_complete", "Teste de engines locais concluído", {})
        print("\n=== Teste de engines locais concluído ===")
        
    except Exception as e:
        log_debug(
            "test_local_voice.py:test_error", 
            "Erro durante o teste de engines locais", 
            {"error": str(e)},
            "A,B,C,D,E"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_local_engines()
