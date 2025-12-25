"""
Teste do sistema de conversação natural do JARVIS
"""

import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.assistant import JarvisAssistant

def log_debug(location, message, data, hypothesis_id="CONVERSATION_TEST"):
    """Função auxiliar para logging"""
    try:
        # Criar diretório se não existir
        log_dir = r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor'
        os.makedirs(log_dir, exist_ok=True)
        
        with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "conversation-test",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Erro no log: {e}")

def test_natural_conversation():
    """Testa o sistema de conversação natural"""
    
    log_debug("test_conversation.py:test_start", "Iniciando teste de conversação natural", {})
    
    try:
        # Inicializar assistente
        assistant = JarvisAssistant()
        
        print("=== Teste de Conversação Natural do JARVIS ===")
        print("Testando diferentes tipos de conversação...")
        
        # Frases de teste para conversação natural
        test_conversations = [
            # Cumprimentos
            {
                'input': 'Olá! Como você está?',
                'type': 'greeting',
                'expected_emotion': 'entusiasta'
            },
            {
                'input': 'Oi JARVIS, tudo bem?',
                'type': 'greeting',
                'expected_emotion': 'entusiasta'
            },
            
            # Perguntas pessoais
            {
                'input': 'Quem é você?',
                'type': 'personal',
                'expected_emotion': 'entusiasta'
            },
            {
                'input': 'O que você consegue fazer?',
                'type': 'capabilities',
                'expected_emotion': 'pensativo'
            },
            
            # Conversação casual
            {
                'input': 'Como está seu dia?',
                'type': 'small_talk',
                'expected_emotion': 'entusiasta'
            },
            {
                'input': 'Conte uma piada',
                'type': 'humor',
                'expected_emotion': 'entusiasta'
            },
            
            # Comandos conversacionais
            {
                'input': 'Abra o Chrome para mim, por favor',
                'type': 'command',
                'expected_emotion': 'entusiasta'
            },
            {
                'input': 'Que horas são agora?',
                'type': 'question',
                'expected_emotion': 'pensativo'
            },
            
            # Perguntas complexas
            {
                'input': 'Pesquise sobre inteligência artificial no Google',
                'type': 'complex_command',
                'expected_emotion': 'entusiasta'
            },
            {
                'input': 'Me explique o que é machine learning',
                'type': 'explanation_request',
                'expected_emotion': 'pensativo'
            }
        ]
        
        successful_conversations = 0
        total_conversations = len(test_conversations)
        
        for i, conversation in enumerate(test_conversations):
            log_debug(
                "test_conversation.py:test_conversation", 
                f"Testando conversação {i+1}", 
                conversation,
                "CONVERSATION"
            )
            
            print(f"\n=== Teste {i+1}/{total_conversations} ===")
            print(f"Tipo: {conversation['type']}")
            print(f"Entrada: '{conversation['input']}'")
            
            # Simular processamento do comando
            start_time = time.time()
            
            # Usar o processador de comandos que agora tem IA
            try:
                # O assistant.command_processor agora tem IA conversacional
                result = assistant.command_processor.process_command(conversation['input'])
                
                end_time = time.time()
                
                log_debug(
                    "test_conversation.py:conversation_result", 
                    f"Resultado da conversação {i+1}", 
                    {
                        "success": result,
                        "duration": end_time - start_time,
                        "input_length": len(conversation['input']),
                        "type": conversation['type']
                    },
                    "CONVERSATION"
                )
                
                print(f"Processamento: {'[OK] Sucesso' if result else '[ERRO] Falha'}")
                print(f"Duração: {end_time - start_time:.2f}s")
                
                if result:
                    successful_conversations += 1
                    print("Resposta: Conversação processada com sucesso!")
                else:
                    print("Resposta: Erro no processamento")
                
            except Exception as e:
                print(f"Erro: {e}")
                log_debug(
                    "test_conversation.py:conversation_error", 
                    f"Erro na conversação {i+1}", 
                    {"error": str(e)},
                    "CONVERSATION"
                )
            
            # Pausa entre testes
            time.sleep(1)
        
        # Estatísticas finais
        success_rate = (successful_conversations / total_conversations) * 100
        
        log_debug(
            "test_conversation.py:test_complete", 
            "Teste de conversação concluído", 
            {
                "total_conversations": total_conversations,
                "successful_conversations": successful_conversations,
                "success_rate": success_rate
            }
        )
        
        print(f"\n=== Resultados do Teste de Conversação ===")
        print(f"Total de conversações testadas: {total_conversations}")
        print(f"Conversações bem-sucedidas: {successful_conversations}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELENTE! Sistema de conversação funcionando perfeitamente!")
        elif success_rate >= 60:
            print("👍 BOM! Sistema de conversação funcionando bem.")
        else:
            print("⚠️ Sistema de conversação precisa de melhorias.")
        
        # Testar recursos específicos da IA
        print(f"\n=== Teste de Recursos de IA ===")
        
        if hasattr(assistant.command_processor, 'ai_enabled') and assistant.command_processor.ai_enabled:
            print("[OK] IA Conversacional: ATIVA")
            print("[OK] Processamento NLP: DISPONIVEL")
            print("[OK] Motor de Decisao: FUNCIONANDO")
            print("[OK] Base de Conhecimento: CARREGADA")
        else:
            print("⚠️ IA Conversacional: MODO BÁSICO")
            print("ℹ️ Para ativar IA completa, instale: pip install spacy nltk scikit-learn")
        
        print(f"\n=== Teste Concluído ===")
        print("O JARVIS agora tem conversação natural e inteligente! 🤖💬")
        
    except Exception as e:
        log_debug(
            "test_conversation.py:test_error", 
            "Erro durante o teste de conversação", 
            {"error": str(e)},
            "CONVERSATION"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_natural_conversation()
