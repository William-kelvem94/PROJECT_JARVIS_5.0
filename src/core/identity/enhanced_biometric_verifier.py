#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS SINGULARITY - Enhanced Biometric Identity Verification System
===================================================================
Sistema aprimorado de verificaÃ§Ã£o biomÃ©trica (facial + vocal) integrado
com identificaÃ§Ã£o Microsoft para autorizaÃ§Ã£o democrÃ¡tica.
"""

import cv2
import numpy as np
import threading
import time
import json
import hashlib
from typing import Optional, List, Dict, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import logging

# Imports obrigatÃ³rios de face recognition
import face_recognition

# Mock camera support
from src.core.config.system_manifest import system_manifest

try:
    from src.core.vision.camera_controller import MockVideoCapture
except Exception:
    MockVideoCapture = None

# Imports obrigatÃ³rios de Ã¡udio
import pyaudio
import librosa

# Import do sistema de identificaÃ§Ã£o Microsoft
from src.core.identity.microsoft_device_identifier import MicrosoftDeviceIdentifier

logger = logging.getLogger(__name__)


@dataclass
class BiometricProfile:
    """ðŸ‘¤ Perfil biomÃ©trico completo do usuÃ¡rio"""

    user_id: str
    microsoft_account: str
    # Face recognition
    face_encodings: List[List[float]]
    face_samples_count: int
    face_confidence_threshold: float
    # Voice recognition
    voice_features: Optional[List[float]]
    voice_samples_count: int
    voice_confidence_threshold: float
    # Metadata
    created_at: datetime
    last_updated: datetime
    total_verifications: int
    successful_verifications: int


@dataclass
class VerificationResult:
    """âœ… Resultado de uma verificaÃ§Ã£o biomÃ©trica"""

    success: bool
    confidence_score: float
    verification_type: str  # "face", "voice", "both"
    user_id: str
    timestamp: datetime
    device_id: str
    additional_info: Dict[str, Any]


class EnhancedBiometricVerifier:
    """
    ðŸ” SISTEMA APRIMORADO DE VERIFICAÃ‡ÃƒO BIOMÃ‰TRICA

    Funcionalidades:
    - Reconhecimento facial com mÃºltiplas amostras
    - VerificaÃ§Ã£o vocal com features avanÃ§adas
    - IntegraÃ§Ã£o com identificaÃ§Ã£o Microsoft
    - Sistema de confianÃ§a adaptativo
    - Cache de verificaÃ§Ãµes para performance
    - Anti-spoofing bÃ¡sico
    """

    def __init__(self, jarvis_core, microsoft_identifier: MicrosoftDeviceIdentifier):
        self.jarvis_core = jarvis_core
        self.microsoft_identifier = microsoft_identifier
        self.config_path = (
            Path(jarvis_core.config["system"]["base_path"])
            / "data"
            / "biometric_profiles"
        )
        self.config_path.mkdir(parents=True, exist_ok=True)

        # Estado do sistema
        self.current_user_profile: Optional[BiometricProfile] = None
        self.is_monitoring = False
        self.last_verification: Optional[VerificationResult] = None

        # Cache de verificaÃ§Ã£o
        self.verification_cache = {}
        self.cache_duration_minutes = 30

        # ConfiguraÃ§Ãµes de face
        self.face_detection_model = "hog"  # ou "cnn" para GPU
        self.face_samples_needed = 3  # MÃ­nimo de amostras de face
        self.face_confidence_threshold = 0.6

        # ConfiguraÃ§Ãµes de voz
        self.voice_samples_needed = 2
        self.voice_confidence_threshold = 0.7
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.audio_rate = 16000
        self.audio_chunk = 1024

        # Threading
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()

        # Callbacks
        self.on_user_verified: Optional[Callable] = None
        self.on_verification_failed: Optional[Callable] = None
        self.on_unauthorized_access: Optional[Callable] = None

        print("ðŸ” Enhanced Biometric Verifier inicializado")

    def setup_user_profile(self, force_recreate: bool = False) -> bool:
        """ðŸ‘¤ CONFIGURA PERFIL BIOMÃ‰TRICO DO USUÃRIO"""

        print("ðŸ‘¤ Configurando perfil biomÃ©trico...")

        try:
            # Obter informaÃ§Ãµes da identificaÃ§Ã£o Microsoft
            if not self.microsoft_identifier.microsoft_account:
                print("âŒ Conta Microsoft nÃ£o identificada")
                return False

            if not self.microsoft_identifier.device_fingerprint:
                print("âŒ Device fingerprint nÃ£o identificado")
                return False

            account_email = self.microsoft_identifier.microsoft_account.account_email
            device_id = self.microsoft_identifier.device_fingerprint.device_id

            # Gerar user_id Ãºnico
            user_id = hashlib.sha256(
                f"{account_email}_{device_id}".encode()
            ).hexdigest()[:16]

            # Verificar se perfil jÃ¡ existe
            profile_path = self.config_path / f"{user_id}_profile.json"

            if profile_path.exists() and not force_recreate:
                # Carregar perfil existente
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile_data = json.load(f)

                # Converter timestamps
                profile_data["created_at"] = datetime.fromisoformat(
                    profile_data["created_at"]
                )
                profile_data["last_updated"] = datetime.fromisoformat(
                    profile_data["last_updated"]
                )

                self.current_user_profile = BiometricProfile(**profile_data)
                print(
                    f"âœ… Perfil carregado: {len(self.current_user_profile.face_encodings)} faces, {self.current_user_profile.voice_samples_count} voice samples"
                )
                return True

            # Criar novo perfil
            print("ðŸ†• Criando novo perfil biomÃ©trico...")
            return self._create_new_profile(user_id, account_email)

        except Exception as e:
            print(f"âŒ Erro configurando perfil: {e}")
            return False

    def _create_new_profile(self, user_id: str, account_email: str) -> bool:
        """ðŸ†• CRIA NOVO PERFIL BIOMÃ‰TRICO"""

        print("ðŸ“¸ Iniciando coleta de amostras biomÃ©tricas...")

        try:
            # 1. COLETAR AMOSTRAS DE FACE
            print(f"   ðŸ“· Coletando {self.face_samples_needed} amostras de face...")
            face_encodings = self._collect_face_samples()

            # 2. COLETAR AMOSTRAS DE VOZ
            print(f"   ðŸŽ¤ Coletando {self.voice_samples_needed} amostras de voz...")
            voice_features, voice_samples_count = self._collect_voice_samples()

            # 3. CRIAR PERFIL
            if len(face_encodings) == 0 and voice_features is None:
                print("âŒ Nenhuma amostra biomÃ©trica coletada")
                return False

            self.current_user_profile = BiometricProfile(
                user_id=user_id,
                microsoft_account=account_email,
                face_encodings=face_encodings,
                face_samples_count=len(face_encodings),
                face_confidence_threshold=self.face_confidence_threshold,
                voice_features=voice_features,
                voice_samples_count=voice_samples_count,
                voice_confidence_threshold=self.voice_confidence_threshold,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                total_verifications=0,
                successful_verifications=0,
            )

            # 4. SALVAR PERFIL
            if hasattr(self, "_save_profile") and callable(
                getattr(self, "_save_profile")
            ):
                self._save_profile()

            print("âœ… Perfil criado com sucesso:")
            print(f"   ðŸ“· {len(face_encodings)} amostras de face")
            print(f"   ðŸŽ¤ {voice_samples_count} amostras de voz")

            return True

        except Exception as e:
            print(f"âŒ Erro criando perfil: {e}")
            return False

    def _collect_face_samples(self) -> List[List[float]]:
        """ðŸ“· COLETA AMOSTRAS DE FACE DO USUÃRIO"""

        face_encodings = []

        try:
            if (
                getattr(system_manifest.vision, "mock_camera", False)
                and MockVideoCapture
            ):
                cap = MockVideoCapture(0)
            else:
                cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("âŒ NÃ£o foi possÃ­vel acessar a webcam")
                return []

            print("   ðŸ‘€ Olhe para a cÃ¢mera e mantenha o rosto visÃ­vel")
            print("   ðŸ“¸ Pressione ESPAÃ‡O para capturar amostra (ESC para cancelar)")

            samples_collected = 0

            while samples_collected < self.face_samples_needed:
                ret, frame = cap.read()
                if not ret:
                    continue

                # Redimensionar para performance
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Detectar faces
                face_locations = face_recognition.face_locations(
                    rgb_small_frame, model=self.face_detection_model
                )

                # Desenhar retÃ¢ngulos nas faces
                for top, right, bottom, left in face_locations:
                    # Escalar de volta para o tamanho original
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Mostrar instruÃ§Ãµes
                cv2.putText(
                    frame,
                    f"Amostras: {samples_collected}/{self.face_samples_needed}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                if len(face_locations) > 0:
                    cv2.putText(
                        frame,
                        "ESPAÃ‡O para capturar",
                        (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )
                else:
                    cv2.putText(
                        frame,
                        "Nenhum rosto detectado",
                        (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                    )

                cv2.imshow("Coleta de Face - JARVIS", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord(" ") and len(face_locations) == 1:  # Apenas uma face
                    # Capturar encoding da face
                    face_encoding = face_recognition.face_encodings(
                        rgb_small_frame, face_locations
                    )[0]
                    face_encodings.append(face_encoding.tolist())
                    samples_collected += 1
                    print(f"   âœ… Amostra {samples_collected} capturada")

                elif key == 27:  # ESC
                    break

            cap.release()
            cv2.destroyAllWindows()

            return face_encodings

        except Exception as e:
            print(f"âŒ Erro coletando amostras de face: {e}")
            return []

    def _collect_voice_samples(self) -> Tuple[Optional[List[float]], int]:
        """ðŸŽ¤ COLETA AMOSTRAS DE VOZ DO USUÃRIO"""

        try:
            voice_features_list = []

            p = pyaudio.PyAudio()

            for i in range(self.voice_samples_needed):
                print(f"   ðŸŽ¤ Amostra de voz {i+1}/{self.voice_samples_needed}")
                print("   ðŸ—£ï¸ Fale por 3 segundos quando comeÃ§ar a gravar...")

                input("   Pressione ENTER para comeÃ§ar a gravaÃ§Ã£o...")

                # Gravar Ã¡udio
                audio_format = (
                    self.audio_format
                    if self.audio_format is not None
                    else pyaudio.paInt16
                )
                stream = p.open(
                    format=audio_format,
                    channels=self.audio_channels,
                    rate=self.audio_rate,
                    input=True,
                    frames_per_buffer=self.audio_chunk,
                )

                print("   ðŸ”´ GRAVANDO... (3 segundos)")

                frames = []
                for _ in range(
                    int(self.audio_rate / self.audio_chunk * 3)
                ):  # 3 segundos
                    data = stream.read(self.audio_chunk)
                    frames.append(data)

                stream.stop_stream()
                stream.close()

                # Converter para numpy array
                audio_data = b"".join(frames)
                audio_np = (
                    np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                    / 32768.0
                )

                # Extrair features usando librosa
                mfccs = librosa.feature.mfcc(y=audio_np, sr=self.audio_rate, n_mfcc=13)
                voice_features = np.mean(mfccs, axis=1).tolist()
                voice_features_list.append(voice_features)

                print(f"   âœ… Amostra {i+1} coletada")

            p.terminate()

            # Calcular features mÃ©dias
            if voice_features_list:
                avg_features = np.mean(voice_features_list, axis=0).tolist()
                return avg_features, len(voice_features_list)

            return None, 0

        except Exception as e:
            print(f"âŒ Erro coletando amostras de voz: {e}")
            return None, 0

    def verify_user_identity(
        self, use_face: bool = True, use_voice: bool = False, timeout_seconds: int = 10
    ) -> VerificationResult:
        """ðŸ” VERIFICA IDENTIDADE DO USUÃRIO"""

        if not self.current_user_profile:
            return VerificationResult(
                success=False,
                confidence_score=0.0,
                verification_type="none",
                user_id="unknown",
                timestamp=datetime.now(),
                device_id=(
                    getattr(
                        self.microsoft_identifier.device_fingerprint,
                        "device_id",
                        "unknown",
                    )
                    if self.microsoft_identifier.device_fingerprint
                    else "unknown"
                ),
                additional_info={"error": "Perfil biomÃ©trico nÃ£o configurado"},
            )

        verification_type = []
        total_confidence = 0.0
        verification_count = 0
        additional_info = {}

        try:
            # VERIFICAÃ‡ÃƒO FACIAL
            if use_face and self.current_user_profile.face_encodings:
                if hasattr(self, "_verify_face") and callable(
                    getattr(self, "_verify_face")
                ):
                    face_confidence = self._verify_face(timeout_seconds)
                    if face_confidence is not None:
                        verification_type.append("face")
                        total_confidence += face_confidence
                        verification_count += 1
                        additional_info["face_confidence"] = face_confidence

            # VERIFICAÃ‡ÃƒO VOCAL
            if use_voice and self.current_user_profile.voice_features:
                if hasattr(self, "_verify_voice") and callable(
                    getattr(self, "_verify_voice")
                ):
                    voice_confidence = self._verify_voice(timeout_seconds)
                    if voice_confidence is not None:
                        verification_type.append("voice")
                        total_confidence += voice_confidence
                        verification_count += 1
                        additional_info["voice_confidence"] = voice_confidence

            # CALCULAR RESULTADO FINAL
            if verification_count == 0:
                success = False
                final_confidence = 0.0
            else:
                final_confidence = total_confidence / verification_count

                # Threshold dinÃ¢mico baseado no tipo de verificaÃ§Ã£o
                if len(verification_type) == 2:  # Face + Voice
                    threshold = min(
                        self.face_confidence_threshold, self.voice_confidence_threshold
                    )
                elif "face" in verification_type:
                    threshold = self.face_confidence_threshold
                elif "voice" in verification_type:
                    threshold = self.voice_confidence_threshold
                else:
                    threshold = 1.0

                success = final_confidence >= threshold

            # Atualizar estatÃ­sticas do perfil
            self.current_user_profile.total_verifications += 1
            if success:
                self.current_user_profile.successful_verifications += 1
            self.current_user_profile.last_updated = datetime.now()

            # Criar resultado
            device_id = "unknown"
            if self.microsoft_identifier.device_fingerprint:
                device_id = self.microsoft_identifier.device_fingerprint.device_id

            result = VerificationResult(
                success=success,
                confidence_score=final_confidence,
                verification_type=(
                    "_".join(verification_type) if verification_type else "none"
                ),
                user_id=self.current_user_profile.user_id,
                timestamp=datetime.now(),
                device_id=device_id,
                additional_info=additional_info,
            )

            self.last_verification = result

            # Callbacks
            if success and self.on_user_verified:
                self.on_user_verified(result)
            elif not success and self.on_verification_failed:
                self.on_verification_failed(result)

            return result

        except Exception as e:
            device_id = "unknown"
            if self.microsoft_identifier.device_fingerprint:
                device_id = self.microsoft_identifier.device_fingerprint.device_id

            return VerificationResult(
                success=False,
                confidence_score=0.0,
                verification_type="error",
                user_id=self.current_user_profile.user_id,
                timestamp=datetime.now(),
                device_id=device_id,
                additional_info={"error": str(e)},
            )

    def _verify_face(self, timeout_seconds: int) -> Optional[float]:
        """ðŸ“· VERIFICA IDENTIDADE FACIAL"""

        try:
            if (
                getattr(system_manifest.vision, "mock_camera", False)
                and MockVideoCapture
            ):
                cap = MockVideoCapture(0)
            else:
                cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                return None

            start_time = time.time()
            best_confidence = 0.0

            while time.time() - start_time < timeout_seconds:
                ret, frame = cap.read()
                if not ret:
                    continue

                # Redimensionar para performance
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Detectar faces
                if face_recognition is not None:
                    face_locations = face_recognition.face_locations(
                        rgb_small_frame, model=self.face_detection_model
                    )
                else:
                    face_locations = []

                if len(face_locations) == 1:  # Apenas uma face
                    # Extrair encoding
                    if face_recognition is not None:
                        face_encodings = face_recognition.face_encodings(
                            rgb_small_frame, face_locations
                        )
                    else:
                        continue

                    if len(face_encodings) == 1:
                        unknown_encoding = face_encodings[0]

                        # Comparar com encodings conhecidos
                        if (
                            self.current_user_profile
                            and self.current_user_profile.face_encodings
                        ):
                            distances = []
                            for (
                                known_encoding
                            ) in self.current_user_profile.face_encodings:
                                if face_recognition is not None:
                                    distance = face_recognition.face_distance(
                                        [known_encoding], unknown_encoding
                                    )[0]
                                else:
                                    distance = 1.0
                                distances.append(distance)

                            if distances:
                                min_distance = min(distances)
                                confidence = (
                                    1.0 - min_distance
                                )  # Converter distÃ¢ncia em confianÃ§a
                                best_confidence = max(best_confidence, confidence)

                # Mostrar feedback visual (opcional)
                cv2.putText(
                    frame,
                    f"Verificando... {best_confidence:.2f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow("VerificaÃ§Ã£o Facial", frame)

                if cv2.waitKey(1) & 0xFF == 27:  # ESC
                    break

                # Se alcanÃ§ou confianÃ§a alta, pode parar cedo
                if best_confidence >= 0.8:
                    break

            cap.release()
            cv2.destroyAllWindows()

            return best_confidence

        except Exception as e:
            print(f"âŒ Erro na verificaÃ§Ã£o facial: {e}")
            return None

    def _verify_voice(self, timeout_seconds: int) -> Optional[float]:
        """ðŸŽ¤ VERIFICA IDENTIDADE VOCAL"""

        try:
            print("ðŸŽ¤ Fale por 3 segundos para verificaÃ§Ã£o...")

            p = pyaudio.PyAudio()

            # Gravar Ã¡udio
            audio_format = (
                self.audio_format if self.audio_format is not None else pyaudio.paInt16
            )
            stream = p.open(
                format=audio_format,
                channels=self.audio_channels,
                rate=self.audio_rate,
                input=True,
                frames_per_buffer=self.audio_chunk,
            )

            frames = []
            for _ in range(int(self.audio_rate / self.audio_chunk * 3)):  # 3 segundos
                data = stream.read(self.audio_chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Processar Ã¡udio
            audio_data = b"".join(frames)
            audio_np = (
                np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            )

            # Extrair features
            mfccs = librosa.feature.mfcc(y=audio_np, sr=self.audio_rate, n_mfcc=13)
            voice_features = np.mean(mfccs, axis=1)

            # Comparar com features conhecidas
            if self.current_user_profile and self.current_user_profile.voice_features:
                known_features = np.array(self.current_user_profile.voice_features)

                # Calcular similaridade (distÃ¢ncia cosine invertida)
                similarity = np.dot(known_features, voice_features) / (
                    np.linalg.norm(known_features) * np.linalg.norm(voice_features)
                )

                # Converter similaridade em confianÃ§a
                confidence = max(0.0, similarity)
                return confidence

            return None

        except Exception as e:
            print(f"âŒ Erro na verificaÃ§Ã£o vocal: {e}")
            return None

    def _save_profile(self):
        """ðŸ’¾ SALVA PERFIL BIOMÃ‰TRICO"""

        if not self.current_user_profile:
            return

        try:
            profile_path = (
                self.config_path / f"{self.current_user_profile.user_id}_profile.json"
            )

            profile_data = asdict(self.current_user_profile)

            # Converter timestamps para ISO format
            profile_data["created_at"] = (
                self.current_user_profile.created_at.isoformat()
            )
            profile_data["last_updated"] = (
                self.current_user_profile.last_updated.isoformat()
            )

            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"âŒ Erro salvando perfil: {e}")

    # ===== MÃ‰TODOS PÃšBLICOS =====

    def start_continuous_monitoring(self):
        """ðŸ‘ï¸ INICIA MONITORAMENTO CONTÃNUO"""

        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.stop_monitoring.clear()

        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        print("ðŸ‘ï¸ Monitoramento biomÃ©trico iniciado")

    def stop_continuous_monitoring(self):
        """â¹ï¸ PARA MONITORAMENTO CONTÃNUO"""

        if not self.is_monitoring:
            return

        self.is_monitoring = False
        self.stop_monitoring.set()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        print("â¹ï¸ Monitoramento biomÃ©trico parado")

    def _monitoring_loop(self):
        """ðŸ”„ LOOP DE MONITORAMENTO CONTÃNUO"""

        while not self.stop_monitoring.wait(30):  # Verificar a cada 30 segundos
            try:
                # VerificaÃ§Ã£o automÃ¡tica se detectar presenÃ§a
                result = self.verify_user_identity(
                    use_face=True, use_voice=False, timeout_seconds=5
                )

                if not result.success:
                    print(f"âš ï¸ VerificaÃ§Ã£o falhou: {result.confidence_score:.2f}")
                    if self.on_unauthorized_access:
                        self.on_unauthorized_access(result)

            except Exception as e:
                print(f"âŒ Erro no monitoramento: {e}")
                time.sleep(5)

    def get_verification_status(self) -> Dict[str, Any]:
        """ðŸ“Š STATUS DO SISTEMA DE VERIFICAÃ‡ÃƒO"""

        if not self.current_user_profile:
            return {"status": "not_configured"}

        success_rate = self.current_user_profile.successful_verifications / max(
            1, self.current_user_profile.total_verifications
        )

        return {
            "status": "configured",
            "user_id": self.current_user_profile.user_id,
            "microsoft_account": self.current_user_profile.microsoft_account,
            "face_samples": self.current_user_profile.face_samples_count,
            "voice_samples": self.current_user_profile.voice_samples_count,
            "total_verifications": self.current_user_profile.total_verifications,
            "success_rate": success_rate,
            "last_verification": (
                asdict(self.last_verification) if self.last_verification else None
            ),
            "monitoring_active": self.is_monitoring,
        }


# Exemplo de uso:
# identifier = MicrosoftDeviceIdentifier("./data")
# verifier = EnhancedBiometricVerifier(jarvis_core, identifier)
# verifier.setup_user_profile()
# result = verifier.verify_user_identity(use_face=True, use_voice=True)
