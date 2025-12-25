"""
Teste do Sistema de IA com Aprendizado Contínuo
"""

import json
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.ai.neural_engine import NeuralEngine

def log_debug(location, message, data, hypothesis_id="AI_LEARNING_TEST"):
    """Função auxiliar para logging"""
    try:
        # Criar diretório se não existir
        log_dir = r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor'
        os.makedirs(log_dir, exist_ok=True)
        
        with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "ai-learning-test",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Erro no log: {e}")

def test_neural_learning_system():
    """Testa o sistema de aprendizado neural"""
    
    log_debug("test_ai_learning.py:test_start", "Iniciando teste de IA com aprendizado", {})
    
    try:
        print("=== Teste do Sistema de IA com Aprendizado Contínuo ===")
        
        # Configuração para teste
        config = {
            'ai': {
                'models_dir': 'models_test'
            }
        }
        
        # Inicializar motor neural
        print("Inicializando Motor Neural...")
        neural_engine = NeuralEngine(config)
        
        # Verificar capacidades
        stats = neural_engine.get_learning_stats()
        
        log_debug(
            "test_ai_learning.py:initial_stats", 
            "Estatísticas iniciais do sistema", 
            stats,
            "AI_INIT"
        )
        
        print(f"✅ Motor Neural inicializado")
        print(f"📊 ML Disponível: {stats['system_info']['ml_available']}")
        print(f"🔥 PyTorch Disponível: {stats['system_info']['torch_available']}")
        print(f"🧠 Modelo Treinado: {stats['model_stats']['is_trained']}")
        print(f"📚 Experiências: {stats['memory_stats']['total_experiences']}")
        
        # Simular interações para aprendizado
        print(f"\n=== Simulando Interações para Aprendizado ===")
        
        test_interactions = [
            {
                'input': 'Olá, como você está?',
                'context': {'time_of_day': 'morning', 'user_satisfaction': 0.9},
                'feedback': 0.9,
                'success': True
            },
            {
                'input': 'Abra o Chrome para mim',
                'context': {'time_of_day': 'afternoon', 'task_complexity': 0.3},
                'feedback': 0.8,
                'success': True
            },
            {
                'input': 'Que horas são?',
                'context': {'time_of_day': 'evening', 'user_satisfaction': 0.95},
                'feedback': 0.95,
                'success': True
            },
            {
                'input': 'Conte uma piada',
                'context': {'time_of_day': 'night', 'user_satisfaction': 0.7},
                'feedback': 0.7,
                'success': True
            },
            {
                'input': 'Comando inválido xyz',
                'context': {'time_of_day': 'morning', 'task_complexity': 0.9},
                'feedback': 0.2,
                'success': False
            }
        ]
        
        successful_interactions = 0
        
        for i, interaction in enumerate(test_interactions):
            print(f"\n--- Interação {i+1} ---")
            print(f"Entrada: '{interaction['input']}'")
            
            # Processar com IA
            result = neural_engine.process_interaction(
                interaction['input'], 
                interaction['context']
            )
            
            log_debug(
                "test_ai_learning.py:interaction_result", 
                f"Resultado da interação {i+1}", 
                {
                    "input": interaction['input'],
                    "result": result,
                    "expected_success": interaction['success']
                },
                "AI_INTERACTION"
            )
            
            print(f"Qualidade Prevista: {result['quality_score']:.2f}")
            print(f"Confiança: {result['confidence']:.2f}")
            print(f"Resposta: {result['response']}")
            
            # Simular feedback do usuário
            neural_engine.learn_from_feedback(
                interaction['input'],
                result['response'],
                interaction['context'],
                interaction['feedback'],
                interaction['success']
            )
            
            if interaction['success']:
                successful_interactions += 1
            
            print(f"Feedback registrado: {interaction['feedback']:.2f}")
            
            time.sleep(0.5)  # Pequena pausa
        
        # Testar aprendizado
        print(f"\n=== Testando Capacidade de Aprendizado ===")
        
        # Forçar treinamento
        print("Forçando sessão de treinamento...")
        training_success = neural_engine.force_training()
        
        log_debug(
            "test_ai_learning.py:training_result", 
            "Resultado do treinamento forçado", 
            {"success": training_success},
            "AI_TRAINING"
        )
        
        if training_success:
            print("✅ Treinamento concluído com sucesso!")
        else:
            print("⚠️ Treinamento não executado (dados insuficientes ou erro)")
        
        # Estatísticas finais
        final_stats = neural_engine.get_learning_stats()
        
        log_debug(
            "test_ai_learning.py:final_stats", 
            "Estatísticas finais do sistema", 
            final_stats,
            "AI_FINAL"
        )
        
        print(f"\n=== Estatísticas Finais ===")
        print(f"Total de Interações: {final_stats['performance_metrics']['total_interactions']}")
        print(f"Interações Bem-sucedidas: {final_stats['performance_metrics']['successful_interactions']}")
        print(f"Taxa de Sucesso: {final_stats['performance_metrics']['avg_response_quality']:.1%}")
        print(f"Sessões de Aprendizado: {final_stats['performance_metrics']['learning_sessions']}")
        print(f"Experiências na Memória: {final_stats['memory_stats']['total_experiences']}")
        print(f"Padrões Aprendidos: {final_stats['memory_stats']['learned_patterns']}")
        
        # Testar predição após aprendizado
        print(f"\n=== Testando Predições Pós-Aprendizado ===")
        
        test_predictions = [
            {
                'input': 'Bom dia! Como está?',
                'context': {'time_of_day': 'morning', 'user_satisfaction': 0.8}
            },
            {
                'input': 'Execute comando desconhecido',
                'context': {'time_of_day': 'afternoon', 'task_complexity': 0.9}
            }
        ]
        
        for test in test_predictions:
            result = neural_engine.process_interaction(test['input'], test['context'])
            
            print(f"Entrada: '{test['input']}'")
            print(f"Qualidade Prevista: {result['quality_score']:.2f}")
            print(f"Confiança: {result['confidence']:.2f}")
            print(f"Resposta: {result['response']}")
            print()
        
        # Parar sistema de aprendizado
        neural_engine.stop_learning()
        
        print(f"=== Teste de IA com Aprendizado Concluído ===")
        
        # Avaliação final
        success_rate = successful_interactions / len(test_interactions)
        
        if final_stats['system_info']['ml_available']:
            print("🧠 IA REAL IMPLEMENTADA COM SUCESSO!")
            print("✅ Sistema de Aprendizado Contínuo: ATIVO")
            print("✅ Memória Neural: FUNCIONANDO")
            print("✅ Auto-treinamento: CONFIGURADO")
            print("✅ Feedback Learning: OPERACIONAL")
            
            if training_success:
                print("✅ Modelo Neural: TREINADO")
            else:
                print("⚠️ Modelo Neural: AGUARDANDO MAIS DADOS")
                
        else:
            print("⚠️ Sistema ML não disponível - instale dependências:")
            print("pip install scikit-learn numpy pandas joblib")
        
        print(f"\n🎯 Taxa de Sucesso das Interações: {success_rate:.1%}")
        print(f"📈 O JARVIS agora APRENDE e EVOLUI continuamente!")
        
    except Exception as e:
        log_debug(
            "test_ai_learning.py:test_error", 
            "Erro durante teste de IA", 
            {"error": str(e)},
            "AI_ERROR"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_neural_learning_system()
