# test_face_recognition.py
import face_recognition
import numpy as np

print("👤 Testando Face Recognition Logic...")

# Cria uma imagem dummy para teste (preto, 100x100)
image = np.zeros((100, 100, 3), dtype=np.uint8)

try:
    # Testa a função básica de localização (não deve encontrar nada, mas não deve dar erro)
    face_locations = face_recognition.face_locations(image)
    print(f"✅ face_recognition funcionando! Módulo carregado e executando.")
    print(f"   Faces encontradas na imagem teste: {len(face_locations)}")
except Exception as e:
    print(f"❌ face_recognition falhou na execução: {e}")
    import traceback
    traceback.print_exc()
