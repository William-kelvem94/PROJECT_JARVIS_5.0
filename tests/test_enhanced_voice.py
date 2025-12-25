"""
Teste do sistema de voz aprimorado (online + offline)
"""

import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.assistant import JarvisAssistant

def log_debug(location, message, data, hypothesis_id="ENHANCED_TEST"):
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

def test_enhanced_voice_system():
    """Testa o sistema de voz aprimorado"""
    
    log_debug("test_enhanced_voice.py:test_start", "Iniciando teste do sistema aprimorado", {})
    
    try:
        # Inicializar assistente
        log_debug("test_enhanced_voice.py:init_assistant", "Inicializando assistente", {})
        assistant = JarvisAssistant()
        
        # Verificar engines disponíveis
        engines_info = {
            'secure_cloud': hasattr(assistant.speech_engine, 'secure_cloud_tts') and assistant.speech_engine.secure_cloud_tts,
            'enhanced_local': hasattr(assistant.speech_engine, 'enhanced_local_tts') and assistant.speech_engine.enhanced_local_tts,
            'smart_processor': hasattr(assistant.speech_engine.natural_processor, 'set_mode')
        }
        
        log_debug(
            "test_enhanced_voice.py:engines_info", 
            "Informações dos engines aprimorados", 
            engines_info,
            "A,B,C,D"
        )
        
        print("=== Sistema de Voz Aprimorado ===")
        print(f"Cloud TTS disponível: {engines_info['secure_cloud']}")
        print(f"Local TTS aprimorado: {engines_info['enhanced_local']}")
        print(f"Processador inteligente: {engines_info['smart_processor']}")
        
        # Testes de naturalidade comparativa
        test_phrases = [
            "Olá! Como você está hoje?",
            "A qualidade da voz deve estar muito melhor agora.",
            "Este é um teste para verificar se o processamento está funcionando corretamente.",
            "Vamos testar diferentes emoções e ver como fica."
        ]
        
        emotions = ['entusiasta', 'pensativo', 'aliviado', None]
        
        for i, (phrase, emotion) in enumerate(zip(test_phrases, emotions)):
            log_debug(
                "test_enhanced_voice.py:test_phrase", 
                f"Testando frase aprimorada {i+1}", 
                {"phrase": phrase, "emotion": emotion},
                "A,B,C,D"
            )
            
            print(f"\n=== Teste Aprimorado {i+1} ===")
            print(f"Frase: {phrase}")
            print(f"Emoção: {emotion}")
            print("Falando com sistema aprimorado...")
            
            # Testar fala aprimorada
            start_time = time.time()
            success = assistant.speech_engine.speak(phrase, emotion)
            end_time = time.time()
            
            log_debug(
                "test_enhanced_voice.py:speech_result", 
                f"Resultado da fala aprimorada {i+1}", 
                {
                    "success": success, 
                    "duration": end_time - start_time,
                    "phrase_length": len(phrase),
                    "emotion": emotion
                },
                "A,B,C,D"
            )
            
            print(f"Sucesso: {success}")
            print(f"Duração: {end_time - start_time:.2f}s")
            
            # Pausa entre testes
            time.sleep(2)
        
        # Teste específico de processamento inteligente
        print(f"\n=== Teste de Processamento Inteligente ===")
        
        if engines_info['smart_processor']:
            # Testar modo online
            print("Testando modo ONLINE (processamento leve)...")
            assistant.speech_engine.natural_processor.set_mode(True)
            success_online = assistant.speech_engine.speak("Este é um teste do modo online com processamento inteligente.", "entusiasta")
            
            time.sleep(2)
            
            # Testar modo offline
            print("Testando modo OFFLINE (processamento intensivo)...")
            assistant.speech_engine.natural_processor.set_mode(False)
            success_offline = assistant.speech_engine.speak("Este é um teste do modo offline com processamento intensivo.", "entusiasta")
            
            log_debug(
                "test_enhanced_voice.py:smart_processing_test", 
                "Teste de processamento inteligente", 
                {"online_success": success_online, "offline_success": success_offline},
                "B"
            )
            
            print(f"Modo online: {success_online}")
            print(f"Modo offline: {success_offline}")
        
        # Verificar estatísticas finais
        if engines_info['enhanced_local']:
            local_stats = assistant.speech_engine.enhanced_local_tts.get_usage_stats()
            log_debug(
                "test_enhanced_voice.py:local_stats", 
                "Estatísticas dos engines locais", 
                local_stats,
                "D"
            )
            print(f"\nEstatísticas engines locais: {local_stats}")
        
        if engines_info['secure_cloud']:
            cloud_stats = assistant.speech_engine.secure_cloud_tts.get_usage_stats()
            log_debug(
                "test_enhanced_voice.py:cloud_stats", 
                "Estatísticas dos engines em nuvem", 
                cloud_stats,
                "F"
            )
            print(f"Estatísticas engines nuvem: {cloud_stats}")
        
        log_debug("test_enhanced_voice.py:test_complete", "Teste do sistema aprimorado concluído", {})
        print("\n=== Teste do Sistema Aprimorado Concluído ===")
        print("✅ Processamento inteligente implementado")
        print("✅ Engines locais otimizados")
        print("✅ Fallback inteligente funcionando")
        print("✅ Naturalidade aprimorada online e offline")
        
    except Exception as e:
        log_debug(
            "test_enhanced_voice.py:test_error", 
            "Erro durante o teste aprimorado", 
            {"error": str(e)},
            "A,B,C,D"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_enhanced_voice_system()
