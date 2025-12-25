#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - MÓDULO DE VISÃO COMPUTACIONAL LOCAL
Processamento 100% local: Face Recognition, Object Detection, Gesture Recognition
"""

import cv2
import numpy as np
import torch
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import json
import sqlite3

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ face_recognition não disponível. Usando OpenCV básico.")

try:
    from facenet_pytorch import InceptionResnetV1, MTCNN
    FACENET_AVAILABLE = True
except ImportError:
    FACENET_AVAILABLE = False
    print("⚠️ facenet_pytorch não disponível. Usando detecção básica.")


class LocalFaceRecognition:
    """Reconhecimento facial 100% local"""

    def __init__(self, models_dir="./models"):
        self.models_dir = Path(models_dir)
        self.db_path = Path("./data/face_database.db")

        # Inicializar banco de dados local
        self._init_database()

        # Carregar modelos locais
        self._load_models()

        # Cache de faces conhecidas
        self.known_faces = {}
        self.known_names = {}
        self._load_known_faces()

    def _init_database(self):
        """Inicializar banco de dados SQLite local"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                embedding BLOB NOT NULL,
                created_at REAL,
                updated_at REAL
            )
        ''')
        self.conn.commit()

    def _load_models(self):
        """Carregar modelos locais"""
        if FACENET_AVAILABLE:
            # FaceNet PyTorch - mais preciso
            self.facenet = InceptionResnetV1(pretrained='vggface2').eval()
            self.mtcnn = MTCNN(keep_all=True, device='cpu')
            print("✅ FaceNet PyTorch carregado")
        elif FACE_RECOGNITION_AVAILABLE:
            # face_recognition library
            print("✅ face_recognition library carregada")
        else:
            # OpenCV básico
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            print("✅ OpenCV Haar Cascade carregado")

    def _load_known_faces(self):
        """Carregar faces conhecidas do banco local"""
        cursor = self.conn.execute('SELECT name, embedding FROM faces')
        for name, embedding_blob in cursor.fetchall():
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            if name not in self.known_faces:
                self.known_faces[name] = []
                self.known_names[name] = []
            self.known_faces[name].append(embedding)

        print(f"✅ Carregadas {len(self.known_faces)} pessoas do banco local")

    def add_user_face(self, image_path: str, user_name: str) -> bool:
        """Adicionar face de usuário ao banco local"""
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Não foi possível carregar imagem: {image_path}")
                return False

            # Detectar e extrair embedding
            embedding = self._extract_face_embedding(image)
            if embedding is None:
                print("❌ Não foi possível detectar face na imagem")
                return False

            # Salvar no banco local
            embedding_blob = embedding.tobytes()
            timestamp = time.time()

            self.conn.execute('''
                INSERT INTO faces (name, embedding, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (user_name, embedding_blob, timestamp, timestamp))

            self.conn.commit()

            # Atualizar cache
            if user_name not in self.known_faces:
                self.known_faces[user_name] = []
            self.known_faces[user_name].append(embedding)

            print(f"✅ Face de '{user_name}' adicionada ao banco local")
            return True

        except Exception as e:
            print(f"❌ Erro ao adicionar face: {e}")
            return False

    def _extract_face_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extrair embedding facial da imagem"""
        try:
            if FACENET_AVAILABLE:
                # Usar FaceNet PyTorch
                faces = self.mtcnn(image)
                if faces is None or len(faces) == 0:
                    return None

                # Pegar primeira face detectada
                face = faces[0].unsqueeze(0)
                with torch.no_grad():
                    embedding = self.facenet(face).squeeze().numpy()

                return embedding.astype(np.float32)

            elif FACE_RECOGNITION_AVAILABLE:
                # Usar face_recognition
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_image)

                if not face_locations:
                    return None

                # Pegar primeira face
                face_encoding = face_recognition.face_encodings(rgb_image, [face_locations[0]])
                if face_encoding:
                    return face_encoding[0].astype(np.float32)

            else:
                # Usar OpenCV básico (menos preciso)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

                if len(faces) == 0:
                    return None

                # Para OpenCV básico, retornamos apenas coordenadas
                # Não temos embedding real, mas podemos usar como placeholder
                x, y, w, h = faces[0]
                return np.array([x, y, w, h], dtype=np.float32)

        except Exception as e:
            print(f"❌ Erro na extração de embedding: {e}")
            return None

    def recognize_face(self, image: np.ndarray) -> Optional[str]:
        """Reconhecer face na imagem"""
        try:
            embedding = self._extract_face_embedding(image)
            if embedding is None:
                return None

            # Comparar com faces conhecidas
            best_match = None
            best_distance = float('inf')

            for name, face_embeddings in self.known_faces.items():
                for known_embedding in face_embeddings:
                    if FACENET_AVAILABLE or FACE_RECOGNITION_AVAILABLE:
                        # Usar distância euclidiana
                        distance = np.linalg.norm(embedding - known_embedding)
                    else:
                        # Para OpenCV básico, usar comparação simples
                        distance = np.sum(np.abs(embedding - known_embedding))

                    if distance < best_distance:
                        best_distance = distance
                        best_match = name

            # Threshold de reconhecimento
            threshold = 0.6 if (FACENET_AVAILABLE or FACE_RECOGNITION_AVAILABLE) else 50
            if best_distance < threshold:
                return best_match

            return None

        except Exception as e:
            print(f"❌ Erro no reconhecimento facial: {e}")
            return None

    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar faces na imagem"""
        faces = []

        try:
            if FACENET_AVAILABLE:
                # Usar MTCNN
                boxes, probs = self.mtcnn.detect(image)
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        faces.append({
                            'x': int(box[0]),
                            'y': int(box[1]),
                            'width': int(box[2] - box[0]),
                            'height': int(box[3] - box[1]),
                            'confidence': float(probs[i]) if probs is not None else 0.0
                        })

            elif FACE_RECOGNITION_AVAILABLE:
                # Usar face_recognition
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_image)

                for location in face_locations:
                    top, right, bottom, left = location
                    faces.append({
                        'x': left,
                        'y': top,
                        'width': right - left,
                        'height': bottom - top,
                        'confidence': 0.9  # face_recognition não retorna confidence
                    })

            else:
                # Usar OpenCV Haar Cascade
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                detected_faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

                for (x, y, w, h) in detected_faces:
                    faces.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'confidence': 0.8  # Haar cascade não retorna confidence precisa
                    })

        except Exception as e:
            print(f"❌ Erro na detecção de faces: {e}")

        return faces


class LocalObjectDetection:
    """Detecção de objetos 100% local"""

    def __init__(self, models_dir="./models"):
        self.models_dir = Path(models_dir)

        # Usar YOLOv8 nano (versão leve) se disponível
        try:
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')  # Modelo leve, ~5MB
            self.yolo_available = True
            print("✅ YOLOv8 Nano carregado para detecção de objetos")
        except ImportError:
            self.yolo_available = False
            print("⚠️ YOLO não disponível. Usando detecção básica.")

    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar objetos na imagem"""
        if not self.yolo_available:
            return self._basic_detection(image)

        try:
            results = self.model(image, conf=0.5, iou=0.5)
            objects = []

            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        cls = int(box.cls[0].cpu().numpy())
                        name = self.model.names[cls]

                        objects.append({
                            'name': name,
                            'confidence': float(conf),
                            'bbox': {
                                'x': int(x1),
                                'y': int(y1),
                                'width': int(x2 - x1),
                                'height': int(y2 - y1)
                            }
                        })

            return objects

        except Exception as e:
            print(f"❌ Erro na detecção YOLO: {e}")
            return self._basic_detection(image)

    def _basic_detection(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detecção básica usando OpenCV"""
        objects = []

        try:
            # Detecção básica de movimento/cor
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (21, 21), 0)

            # Threshold para detectar objetos
            thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 500:
                    continue

                (x, y, w, h) = cv2.boundingRect(contour)
                objects.append({
                    'name': 'objeto_desconhecido',
                    'confidence': 0.5,
                    'bbox': {'x': x, 'y': y, 'width': w, 'height': h}
                })

        except Exception as e:
            print(f"❌ Erro na detecção básica: {e}")

        return objects


class LocalGestureRecognition:
    """Reconhecimento de gestos 100% local"""

    def __init__(self):
        # Usar MediaPipe se disponível
        try:
            import mediapipe as mp
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
            self.mediapipe_available = True
            print("✅ MediaPipe Hands carregado")
        except ImportError:
            self.mediapipe_available = False
            print("⚠️ MediaPipe não disponível. Usando detecção básica.")

    def recognize_gesture(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Reconhecer gestos na imagem"""
        if not self.mediapipe_available:
            return self._basic_gesture_detection(image)

        gestures = []

        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_image)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    gesture = self._classify_gesture(hand_landmarks)
                    if gesture:
                        gestures.append({
                            'gesture': gesture,
                            'confidence': 0.8,
                            'hand_landmarks': hand_landmarks
                        })

        except Exception as e:
            print(f"❌ Erro no reconhecimento MediaPipe: {e}")
            return self._basic_gesture_detection(image)

        return gestures

    def _classify_gesture(self, hand_landmarks) -> Optional[str]:
        """Classificar gesto baseado nas landmarks"""
        try:
            # Extrair posições dos dedos
            fingers = []
            tip_ids = [4, 8, 12, 16, 20]  # Polegar, indicador, médio, anelar, mínimo

            for tip_id in tip_ids:
                tip_y = hand_landmarks.landmark[tip_id].y
                pip_y = hand_landmarks.landmark[tip_id - 2].y
                fingers.append(1 if tip_y < pip_y else 0)

            # Classificar gestos comuns
            if fingers == [0, 1, 1, 1, 1]:  # Apenas polegar fechado
                return "thumbs_up"
            elif fingers == [0, 0, 0, 0, 0]:  # Todos fechados
                return "fist"
            elif fingers == [1, 1, 1, 1, 1]:  # Todos abertos
                return "open_palm"
            elif fingers == [0, 1, 0, 0, 0]:  # Apenas indicador
                return "pointing"
            elif fingers == [1, 1, 0, 0, 0]:  # V de vitória
                return "peace"
            elif fingers == [0, 1, 1, 0, 0]:  # OK
                return "ok"

        except Exception as e:
            print(f"❌ Erro na classificação de gesto: {e}")

        return None

    def _basic_gesture_detection(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detecção básica de gestos usando OpenCV"""
        gestures = []

        try:
            # Conversão para detectar contornos
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]  # Top 2

            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 10000:  # Área típica de mão
                    x, y, w, h = cv2.boundingRect(contour)

                    # Classificação básica baseada na forma
                    gestures.append({
                        'gesture': 'hand_detected',
                        'confidence': 0.6,
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h}
                    })

        except Exception as e:
            print(f"❌ Erro na detecção básica de gestos: {e}")

        return gestures


class LocalVisionProcessor:
    """Processador de visão integrado 100% local"""

    def __init__(self, models_dir="./models"):
        self.models_dir = Path(models_dir)

        # Inicializar módulos
        self.face_recognition = LocalFaceRecognition(models_dir)
        self.object_detection = LocalObjectDetection(models_dir)
        self.gesture_recognition = LocalGestureRecognition()

        # Estatísticas
        self.stats = {
            'frames_processed': 0,
            'faces_detected': 0,
            'objects_detected': 0,
            'gestures_detected': 0,
            'start_time': time.time()
        }

        print("🎥 Processador de Visão Local inicializado")

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Processar frame completo com todos os módulos"""
        self.stats['frames_processed'] += 1

        result = {
            'timestamp': time.time(),
            'faces': [],
            'objects': [],
            'gestures': [],
            'stats': self.stats.copy()
        }

        try:
            # Detecção facial
            faces = self.face_recognition.detect_faces(frame)
            result['faces'] = faces
            self.stats['faces_detected'] += len(faces)

            # Reconhecimento facial (se houver faces)
            if faces:
                recognized_names = []
                for face in faces:
                    # Recortar face para reconhecimento
                    x, y, w, h = face['x'], face['y'], face['width'], face['height']
                    face_crop = frame[y:y+h, x:x+w]
                    if face_crop.size > 0:
                        name = self.face_recognition.recognize_face(face_crop)
                        if name:
                            recognized_names.append(name)

                result['recognized_faces'] = recognized_names

            # Detecção de objetos
            objects = self.object_detection.detect_objects(frame)
            result['objects'] = objects
            self.stats['objects_detected'] += len(objects)

            # Reconhecimento de gestos
            gestures = self.gesture_recognition.recognize_gesture(frame)
            result['gestures'] = gestures
            self.stats['gestures_detected'] += len(gestures)

        except Exception as e:
            print(f"❌ Erro no processamento de visão: {e}")
            result['error'] = str(e)

        return result

    def add_user_face(self, image_path: str, user_name: str) -> bool:
        """Adicionar face de usuário"""
        return self.face_recognition.add_user_face(image_path, user_name)

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do processador"""
        uptime = time.time() - self.stats['start_time']
        stats = self.stats.copy()
        stats['uptime'] = uptime
        stats['fps_avg'] = stats['frames_processed'] / uptime if uptime > 0 else 0
        return stats

    def reset_stats(self):
        """Resetar estatísticas"""
        self.stats = {
            'frames_processed': 0,
            'faces_detected': 0,
            'objects_detected': 0,
            'gestures_detected': 0,
            'start_time': time.time()
        }


# Função de teste
def test_vision_system():
    """Testar sistema de visão local"""
    print("🧪 Testando sistema de visão local...")

    vision = LocalVisionProcessor()

    # Testar com câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Câmera não disponível para teste")
        return

    print("📹 Teste iniciado. Pressione 'q' para sair.")

    frame_count = 0
    while frame_count < 10:  # Testar 10 frames
        ret, frame = cap.read()
        if ret:
            result = vision.process_frame(frame)
            frame_count += 1

            if result['faces']:
                print(f"✅ Faces detectadas: {len(result['faces'])}")
            if result['objects']:
                print(f"✅ Objetos detectados: {len(result['objects'])}")
            if result['gestures']:
                print(f"✅ Gestos detectados: {len(result['gestures'])}")

            cv2.imshow('Teste Visão Local', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.1)

    cap.release()
    cv2.destroyAllWindows()

    stats = vision.get_stats()
    print("📊 Estatísticas do teste:")
    print(f"  - Frames processados: {stats['frames_processed']}")
    print(f"  - FPS médio: {stats['fps_avg']:.1f}")
    print("✅ Teste concluído!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Processador de Visão Local JARVIS")
    parser.add_argument("--test", action="store_true", help="Executar teste do sistema")
    parser.add_argument("--add-face", nargs=2, metavar=('IMAGE', 'NAME'),
                       help="Adicionar face ao banco local")

    args = parser.parse_args()

    if args.test:
        test_vision_system()
    elif args.add_face:
        image_path, user_name = args.add_face
        vision = LocalVisionProcessor()
        if vision.add_user_face(image_path, user_name):
            print(f"✅ Face de '{user_name}' adicionada com sucesso!")
        else:
            print("❌ Falha ao adicionar face.")
    else:
        print("🎥 Processador de Visão Local JARVIS 5.0")
        print("Use --test para testar ou --add-face para adicionar faces")
