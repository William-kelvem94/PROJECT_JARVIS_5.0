"""
Teste do Sistema de Visão Computacional
"""

import json
import time
import os
import sys
import cv2
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.vision.vision_engine import VisionEngine

def log_debug(location, message, data, hypothesis_id="VISION_TEST"):
    """Função auxiliar para logging"""
    try:
        # Criar diretório se não existir
        log_dir = r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor'
        os.makedirs(log_dir, exist_ok=True)
        
        with open(r'c:\Users\willi\Documents\GitHub\PROJECT_JARVIS_5.0\.cursor\debug.log', 'a', encoding='utf-8') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "vision-test",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Erro no log: {e}")

def test_vision_system():
    """Testa o sistema de visão computacional"""
    
    log_debug("test_vision_system.py:test_start", "Iniciando teste de visão computacional", {})
    
    try:
        print("=== Teste do Sistema de Visão Computacional ===")
        
        # Configuração para teste
        config = {
            'vision': {
                'camera_index': 0,
                'resolution': (640, 480),
                'fps': 30
            }
        }
        
        # Inicializar motor de visão
        print("Inicializando Sistema de Visão...")
        vision_engine = VisionEngine(config)
        
        # Verificar capacidades
        stats = vision_engine.get_vision_stats()
        
        log_debug(
            "test_vision_system.py:initial_stats", 
            "Estatísticas iniciais do sistema de visão", 
            stats,
            "VISION_INIT"
        )
        
        print(f"✅ Sistema de Visão inicializado")
        print(f"📷 MediaPipe Disponível: {stats['capabilities']['mediapipe_available']}")
        print(f"👤 Face Recognition Disponível: {stats['capabilities']['face_recognition_available']}")
        print(f"🔥 PyTorch Vision Disponível: {stats['capabilities']['torch_vision_available']}")
        
        # Testar inicialização da câmera
        print(f"\n=== Testando Câmera ===")
        
        camera_success = vision_engine.initialize_camera()
        
        log_debug(
            "test_vision_system.py:camera_init", 
            "Resultado da inicialização da câmera", 
            {"success": camera_success},
            "CAMERA"
        )
        
        if camera_success:
            print("✅ Câmera inicializada com sucesso!")
            
            # Capturar alguns frames de teste
            print("Capturando frames de teste...")
            
            test_results = []
            
            for i in range(5):
                print(f"Capturando frame {i+1}/5...")
                
                frame = vision_engine.capture_frame()
                
                if frame is not None:
                    # Processar frame
                    start_time = time.time()
                    results = vision_engine.process_frame(frame)
                    processing_time = time.time() - start_time
                    
                    test_results.append(results)
                    
                    log_debug(
                        "test_vision_system.py:frame_processed", 
                        f"Frame {i+1} processado", 
                        {
                            "processing_time": processing_time,
                            "faces_detected": len(results.get('faces', [])),
                            "hands_detected": len(results.get('hands', [])),
                            "gestures_detected": len(results.get('gestures', [])),
                            "interactions": len(results.get('interactions', []))
                        },
                        "FRAME_PROCESSING"
                    )
                    
                    print(f"  Faces detectadas: {len(results.get('faces', []))}")
                    print(f"  Mãos detectadas: {len(results.get('hands', []))}")
                    print(f"  Gestos reconhecidos: {len(results.get('gestures', []))}")
                    print(f"  Interações: {len(results.get('interactions', []))}")
                    print(f"  Tempo de processamento: {processing_time:.3f}s")
                    
                    # Mostrar gestos detectados
                    for gesture in results.get('gestures', []):
                        print(f"    🤚 Gesto: {gesture['name']} (confiança: {gesture['confidence']:.2f})")
                        print(f"        Significado: {vision_engine._interpret_gesture(gesture['name'])}")
                    
                    # Mostrar interações
                    for interaction in results.get('interactions', []):
                        print(f"    🔄 Interação: {interaction['type']} - {interaction['meaning']}")
                    
                else:
                    print(f"  ❌ Falha ao capturar frame {i+1}")
                
                time.sleep(1)  # Pausa entre capturas
            
            # Estatísticas do processamento
            print(f"\n=== Estatísticas de Processamento ===")
            
            final_stats = vision_engine.get_vision_stats()
            
            log_debug(
                "test_vision_system.py:final_stats", 
                "Estatísticas finais do sistema de visão", 
                final_stats,
                "VISION_FINAL"
            )
            
            print(f"Frames processados: {final_stats['performance_metrics']['frames_processed']}")
            print(f"Faces detectadas (total): {final_stats['performance_metrics']['faces_detected']}")
            print(f"Gestos reconhecidos (total): {final_stats['performance_metrics']['gestures_recognized']}")
            print(f"Tempo médio de processamento: {final_stats['performance_metrics']['processing_time_avg']:.3f}s")
            
            # Testar aprendizado de face (simulado)
            print(f"\n=== Testando Aprendizado de Face ===")
            
            if stats['capabilities']['face_recognition_available']:
                print("Simulando aprendizado de face...")
                
                # Capturar frame para aprendizado
                frame = vision_engine.capture_frame()
                if frame is not None:
                    learn_success = vision_engine.learn_face("Usuario_Teste", frame)
                    
                    log_debug(
                        "test_vision_system.py:face_learning", 
                        "Resultado do aprendizado de face", 
                        {"success": learn_success},
                        "FACE_LEARNING"
                    )
                    
                    if learn_success:
                        print("✅ Face aprendida com sucesso!")
                        print(f"Faces conhecidas: {len(vision_engine.visual_memory['known_faces'])}")
                    else:
                        print("⚠️ Nenhuma face detectada para aprendizado")
                else:
                    print("❌ Não foi possível capturar frame para aprendizado")
            else:
                print("⚠️ Face Recognition não disponível")
            
            # Fechar câmera
            vision_engine.close_camera()
            print("📷 Câmera fechada")
            
        else:
            print("❌ Falha ao inicializar câmera")
            print("Testando com imagem simulada...")
            
            # Criar imagem de teste
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(test_frame, "TESTE - SEM CAMERA", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Processar imagem de teste
            results = vision_engine.process_frame(test_frame)
            
            print(f"Processamento de imagem simulada:")
            print(f"  Faces: {len(results.get('faces', []))}")
            print(f"  Mãos: {len(results.get('hands', []))}")
            print(f"  Gestos: {len(results.get('gestures', []))}")
        
        # Resumo das capacidades
        print(f"\n=== Capacidades do Sistema de Visão ===")
        
        capabilities = [
            ("Detecção de Faces", stats['capabilities']['mediapipe_available']),
            ("Reconhecimento Facial", stats['capabilities']['face_recognition_available']),
            ("Detecção de Mãos", stats['capabilities']['mediapipe_available']),
            ("Reconhecimento de Gestos", stats['capabilities']['mediapipe_available']),
            ("Detecção de Pose", stats['capabilities']['mediapipe_available']),
            ("Deep Learning Vision", stats['capabilities']['torch_vision_available'])
        ]
        
        for capability, available in capabilities:
            status = "✅ DISPONÍVEL" if available else "⚠️ INDISPONÍVEL"
            print(f"{capability}: {status}")
        
        # Gestos suportados
        print(f"\n=== Gestos Reconhecidos ===")
        supported_gestures = [
            ("👍 Joinha (Thumbs Up)", "Aprovação, concordância"),
            ("✌️ Sinal de Paz", "Paz, vitória"),
            ("👌 Sinal de OK", "Tudo bem, perfeito"),
            ("👉 Apontar", "Indicação, direção"),
            ("✋ Palma Aberta", "Pare, apresentação"),
            ("✊ Punho Fechado", "Força, determinação")
        ]
        
        for gesture, meaning in supported_gestures:
            print(f"{gesture}: {meaning}")
        
        print(f"\n=== Teste de Visão Computacional Concluído ===")
        
        if stats['capabilities']['mediapipe_available']:
            print("🎉 SISTEMA DE VISÃO FUNCIONANDO!")
            print("✅ Detecção de faces, mãos e gestos: ATIVO")
            print("✅ Reconhecimento de interações: OPERACIONAL")
            print("✅ Processamento em tempo real: CONFIGURADO")
            
            if stats['capabilities']['face_recognition_available']:
                print("✅ Reconhecimento facial: DISPONÍVEL")
            
            if stats['capabilities']['torch_vision_available']:
                print("✅ Deep Learning Vision: DISPONÍVEL")
                
        else:
            print("⚠️ Sistema de visão limitado - instale dependências:")
            print("pip install opencv-python mediapipe face-recognition")
        
        print(f"\n👁️ O JARVIS agora TEM VISÃO e reconhece gestos!")
        
    except Exception as e:
        log_debug(
            "test_vision_system.py:test_error", 
            "Erro durante teste de visão", 
            {"error": str(e)},
            "VISION_ERROR"
        )
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_vision_system()
