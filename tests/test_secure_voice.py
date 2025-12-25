"""
Teste de voz com engines seguros em nuvem
"""

import json
import time
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.assistant import JarvisAssistant

def log_debug(location, message, data, hypothesis_id="SECURE_TEST"):
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

def test_secure_cloud_engines():
    """Testa engines TTS seguros em nuvem"""
    
    log_debug("test_secure_voice.py:test_start", "Iniciando teste de engines seguros em nuvem", {})
    
    try:
        # Inicializar assistente
        log_debug("test_secure_voice.py:init_assistant", "Inicializando assistente", {})
        assistant = JarvisAssistant()
        
        # Verificar engines seguros disponíveis
        if hasattr(assistant.speech_engine, 'secure_cloud_tts') and assistant.speech_engine.secure_cloud_tts:
            cloud_engines = assistant.speech_engine.secure_cloud_tts.get_available_engines()
            usage_stats = assistant.speech_engine.secure_cloud_tts.get_usage_stats()
            
            log_debug(
                "test_secure_voice.py:secure_engines_info", 
                "Informações dos engines seguros", 
                {"available_engines": cloud_engines, "usage_stats": usage_stats},
                "F"
            )
            print(f"Engines seguros disponíveis: {cloud_engines}")
            print(f"Estatísticas de uso: {usage_stats}")
        else:
            log_debug(
                "test_secure_voice.py:no_secure_engines", 
                "Nenhum engine seguro disponível", 
                {},
                "F"
            )
            print("Nenhum engine TTS seguro disponível")
        
        # Teste de naturalidade com segurança
        test_texts = [
            ("Olá! Agora estou usando engines de voz seguros e gratuitos da internet.", "entusiasta"),
            ("A qualidade da voz deve estar muito melhor com os serviços em nuvem.", "pensativo"),
            ("Todos os dados são transmitidos de forma segura usando HTTPS.", "aliviado"),
            ("Este é um teste mais longo para verificar como a voz se comporta com frases maiores usando engines seguros em nuvem, mantendo a naturalidade e a segurança.", None)
        ]
        
        for i, (text, emotion) in enumerate(test_texts):
            log_debug(
                "test_secure_voice.py:test_text", 
                f"Testando texto seguro {i+1}", 
                {"text": text, "emotion": emotion},
                "A,B,C,F"
            )
            
            print(f"\n=== Teste Seguro {i+1} ===")
            print(f"Texto: {text}")
            print(f"Emoção: {emotion}")
            print("Falando com segurança...")
            
            # Testar fala segura
            start_time = time.time()
            success = assistant.speech_engine.speak(text, emotion)
            end_time = time.time()
            
            log_debug(
                "test_secure_voice.py:secure_speech_result", 
                f"Resultado da fala segura {i+1}", 
                {
                    "success": success, 
                    "duration": end_time - start_time,
                    "text_length": len(text)
                },
                "A,B,C,F"
            )
            
            print(f"Sucesso: {success}")
            print(f"Duração: {end_time - start_time:.2f}s")
            
            # Pausa entre testes
            time.sleep(2)
        
        # Verificar estatísticas finais
        if hasattr(assistant.speech_engine, 'secure_cloud_tts') and assistant.speech_engine.secure_cloud_tts:
            final_stats = assistant.speech_engine.secure_cloud_tts.get_usage_stats()
            log_debug(
                "test_secure_voice.py:final_stats", 
                "Estatísticas finais de uso", 
                final_stats,
                "F"
            )
            print(f"\nEstatísticas finais: {final_stats}")
        
        log_debug("test_secure_voice.py:test_complete", "Teste de engines seguros concluído", {})
        print("\n=== Teste de engines seguros concluído ===")
        
    except Exception as e:
        log_debug(
            "test_secure_voice.py:test_error", 
            "Erro durante o teste de engines seguros", 
            {"error": str(e)},
            "A,B,C,D,E,F"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_secure_cloud_engines()
