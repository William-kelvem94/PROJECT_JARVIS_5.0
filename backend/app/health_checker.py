"""
JARVIS 5.0 — System Health Checker
===================================
Sistema de verificação de saúde de todos os componentes em tempo real.
Verifica disponibilidade, funcionalidade e status de cada subsistema.
"""

import os
import importlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class ComponentStatus(Enum):
    """Status possíveis de um componente."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    ERROR = "error"
    INITIALIZING = "initializing"
    NOT_CONFIGURED = "not_configured"


@dataclass
class ComponentHealth:
    """Representa o estado de saúde de um componente."""
    name: str
    status: ComponentStatus
    available: bool = False
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    error: Optional[str] = None


class HealthChecker:
    """Verifica a saúde de todos os componentes do JARVIS."""
    
    def __init__(self):
        self.last_check: Dict[str, ComponentHealth] = {}
        logger.info("[HealthChecker] Initialized")
    
    # ========================================================================
    # NUCLEO COGNITIVO
    # ========================================================================
    
    def check_smart_router(self) -> ComponentHealth:
        """Verifica Smart Router (roteamento inteligente de queries)."""
        try:
            from .smart_router import SmartRouter
            # Verificar se existe instância
            return ComponentHealth(
                name="Smart router",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Roteamento inteligente ativo",
                details={"module": "smart_router"}
            )
        except ImportError:
            return ComponentHealth(
                name="Smart router",
                status=ComponentStatus.NOT_CONFIGURED,
                available=False,
                message="Módulo smart_router não encontrado",
                error="Module not implemented yet"
            )
        except Exception as e:
            return ComponentHealth(
                name="Smart router",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro ao carregar: {str(e)}",
                error=str(e)
            )
    
    def check_unified_memory(self) -> ComponentHealth:
        """Verifica Memoria Unificada (sistema de memória vetorial)."""
        try:
            from .unified_memory import memory
            if memory:
                return ComponentHealth(
                    name="Memoria unificada",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message="Sistema de memória vetorial ativo",
                    details={
                        "vector_store": "chromadb",
                        "embeddings": "sentence-transformers"
                    }
                )
            else:
                return ComponentHealth(
                    name="Memoria unificada",
                    status=ComponentStatus.OFFLINE,
                    available=False,
                    message="Memory manager não inicializado"
                )
        except Exception as e:
            return ComponentHealth(
                name="Memoria unificada",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_engineer_brain(self) -> ComponentHealth:
        """Verifica Engineer Brain (raciocínio técnico)."""
        try:
            from .engineer_brain import EngineerBrain
            return ComponentHealth(
                name="Engineer brain",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Raciocínio técnico disponível",
                details={"module": "engineer_brain"}
            )
        except ImportError:
            return ComponentHealth(
                name="Engineer brain",
                status=ComponentStatus.OFFLINE,
                available=False,
                message="Módulo engineer_brain não encontrado",
                error="Module not found"
            )
        except Exception as e:
            return ComponentHealth(
                name="Engineer brain",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_adaptive_persona(self) -> ComponentHealth:
        """Verifica Persona Adaptativa."""
        try:
            from .persona import PersonaManager
            return ComponentHealth(
                name="Persona adaptativa",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Sistema de personalidade adaptativa ativo",
                details={"module": "persona"}
            )
        except Exception as e:
            return ComponentHealth(
                name="Persona adaptativa",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    # ========================================================================
    # PERCEPCAO
    # ========================================================================
    
    def check_face_engine(self) -> ComponentHealth:
        """Verifica Face Engine (reconhecimento facial)."""
        try:
            # Verificar se face_recognition está disponível
            import face_recognition
            return ComponentHealth(
                name="Face engine",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Reconhecimento facial disponível (Level A)",
                details={
                    "library": "face_recognition",
                    "level": "A (identity)"
                },
                dependencies=["camera"]
            )
        except ImportError:
            return ComponentHealth(
                name="Face engine",
                status=ComponentStatus.NOT_CONFIGURED,
                available=False,
                message="face_recognition não instalado",
                error="pip install face_recognition"
            )
        except Exception as e:
            return ComponentHealth(
                name="Face engine",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_gesture_engine(self) -> ComponentHealth:
        """Verifica Gesture Engine (detecção de gestos)."""
        try:
            import mediapipe
            import cv2
            return ComponentHealth(
                name="Gestos",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Detecção de gestos disponível",
                details={
                    "library": "mediapipe",
                    "models": "hand_landmarker, pose_landmarker"
                },
                dependencies=["camera"]
            )
        except ImportError as e:
            return ComponentHealth(
                name="Gestos",
                status=ComponentStatus.NOT_CONFIGURED,
                available=False,
                message="Dependências não instaladas",
                error=str(e)
            )
        except Exception as e:
            return ComponentHealth(
                name="Gestos",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_object_detection(self) -> ComponentHealth:
        """Verifica Object Detection (detecção de objetos)."""
        try:
            from ultralytics import YOLO
            import cv2
            # Verificar se modelo existe
            model_path = "yolov8n.pt"
            if os.path.exists(model_path):
                return ComponentHealth(
                    name="Objetos",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message="Detecção de objetos ativa (YOLOv8)",
                    details={
                        "model": "yolov8n",
                        "library": "ultralytics"
                    },
                    dependencies=["camera"]
                )
            else:
                return ComponentHealth(
                    name="Objetos",
                    status=ComponentStatus.DEGRADED,
                    available=True,
                    message="Modelo YOLOv8 não encontrado",
                    details={"note": "Será baixado no primeiro uso"}
                )
        except ImportError:
            return ComponentHealth(
                name="Objetos",
                status=ComponentStatus.NOT_CONFIGURED,
                available=False,
                message="ultralytics não instalado",
                error="pip install ultralytics"
            )
        except Exception as e:
            return ComponentHealth(
                name="Objetos",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_realtime_audio(self) -> ComponentHealth:
        """Verifica Audio em Tempo Real."""
        try:
            import sounddevice
            import openwakeword
            # Verificar se consegue acessar microfone
            devices = sounddevice.query_devices()
            has_input = any(d['max_input_channels'] > 0 for d in devices)
            
            if has_input:
                return ComponentHealth(
                    name="Audio em tempo real",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message="Sistema de áudio ativo com wake word",
                    details={
                        "input_devices": sum(1 for d in devices if d['max_input_channels'] > 0),
                        "wake_word": "openwakeword"
                    },
                    dependencies=["microfone"]
                )
            else:
                return ComponentHealth(
                    name="Audio em tempo real",
                    status=ComponentStatus.OFFLINE,
                    available=False,
                    message="Nenhum dispositivo de entrada detectado",
                    error="No audio input devices"
                )
        except ImportError as e:
            return ComponentHealth(
                name="Audio em tempo real",
                status=ComponentStatus.NOT_CONFIGURED,
                available=False,
                message="Dependências de áudio não instaladas",
                error=str(e)
            )
        except Exception as e:
            return ComponentHealth(
                name="Audio em tempo real",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro ao verificar áudio: {str(e)}",
                error=str(e)
            )
    
    # ========================================================================
    # SISTEMA
    # ========================================================================
    
    def check_os_tools(self) -> ComponentHealth:
        """Verifica OS Tools (controle de sistema operacional)."""
        try:
            from .system_control import SystemControlMatrix
            import psutil
            return ComponentHealth(
                name="OS tools",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Controles de sistema disponíveis",
                details={
                    "features": ["volume", "brightness", "screenshots"],
                    "os": os.name
                }
            )
        except Exception as e:
            return ComponentHealth(
                name="OS tools",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_browser_engine(self) -> ComponentHealth:
        """Verifica Browser Engine (automação web)."""
        try:
            from .browser_engine import BrowserEngine
            import playwright
            return ComponentHealth(
                name="Browser engine",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Automação web disponível (Playwright)",
                details={"library": "playwright"}
            )
        except ImportError:
            return ComponentHealth(
                name="Browser engine",
                status=ComponentStatus.NOT_CONFIGURED,
                available=False,
                message="playwright não instalado",
                error="pip install playwright"
            )
        except Exception as e:
            return ComponentHealth(
                name="Browser engine",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_screen_capture(self) -> ComponentHealth:
        """Verifica Capturas (screenshots e gravação)."""
        try:
            import mss
            with mss.mss() as sct:
                monitors = sct.monitors
                return ComponentHealth(
                    name="Capturas",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message=f"Captura de tela disponível ({len(monitors)-1} monitor(es))",
                    details={
                        "library": "mss",
                        "monitors": len(monitors) - 1
                    },
                    dependencies=["espelhamento_tela"]
                )
        except Exception as e:
            return ComponentHealth(
                name="Capturas",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro ao acessar tela: {str(e)}",
                error=str(e)
            )
    
    def check_assisted_execution(self) -> ComponentHealth:
        """Verifica Execução Assistida."""
        try:
            import pyautogui
            return ComponentHealth(
                name="Execucao assistida",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Automação de interface disponível",
                details={"library": "pyautogui"}
            )
        except Exception as e:
            return ComponentHealth(
                name="Execucao assistida",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    # ========================================================================
    # SEGURANÇA
    # ========================================================================
    
    def check_sentinel_parser(self) -> ComponentHealth:
        """Verifica Sentinel Parser (análise de comandos)."""
        try:
            from .security.sentinel_parser import SentinelParser
            return ComponentHealth(
                name="Sentinel parser",
                status=ComponentStatus.ONLINE,
                available=True,
                message="Parser de segurança ativo",
                details={"module": "sentinel_parser"}
            )
        except Exception as e:
            return ComponentHealth(
                name="Sentinel parser",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_blackbox(self) -> ComponentHealth:
        """Verifica BlackBox (logging criptografado)."""
        try:
            from .security.blackbox import BlackBox
            # Verificar se DB existe
            db_path = "data/blackbox.db"
            exists = os.path.exists(db_path)
            return ComponentHealth(
                name="Blackbox",
                status=ComponentStatus.ONLINE if exists else ComponentStatus.INITIALIZING,
                available=True,
                message="Sistema de logging criptografado ativo" if exists else "Será inicializado no primeiro uso",
                details={"database": db_path, "exists": exists}
            )
        except Exception as e:
            return ComponentHealth(
                name="Blackbox",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_holodeck(self) -> ComponentHealth:
        """Verifica Holodeck (sandbox de testes)."""
        try:
            # Verificar se existe diretório holodeck
            holodeck_path = "data/holodeck"
            if os.path.exists(holodeck_path):
                return ComponentHealth(
                    name="Holodeck",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message="Ambiente de simulação disponível",
                    details={"path": holodeck_path}
                )
            else:
                return ComponentHealth(
                    name="Holodeck",
                    status=ComponentStatus.NOT_CONFIGURED,
                    available=False,
                    message="Diretório holodeck não configurado",
                    error="Directory not found"
                )
        except Exception as e:
            return ComponentHealth(
                name="Holodeck",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_biometric_vault(self) -> ComponentHealth:
        """Verifica Biometric Vault (armazenamento biométrico)."""
        try:
            # Verificar se diretórios de biometria existem
            faces_path = "data/faces"
            voices_path = "data/voices"
            faces_exists = os.path.exists(faces_path)
            voices_exists = os.path.exists(voices_path)
            
            if faces_exists and voices_exists:
                face_count = len([f for f in os.listdir(faces_path) if f.endswith(('.jpg', '.png'))])
                voice_count = len([f for f in os.listdir(voices_path) if f.endswith('.npy')])
                
                return ComponentHealth(
                    name="Biometric vault",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message=f"Vault biométrico ativo ({face_count} faces, {voice_count} vozes)",
                    details={
                        "faces": face_count,
                        "voices": voice_count,
                        "paths": [faces_path, voices_path]
                    }
                )
            else:
                return ComponentHealth(
                    name="Biometric vault",
                    status=ComponentStatus.INITIALIZING,
                    available=True,
                    message="Diretórios serão criados no primeiro uso",
                    details={"faces_ready": faces_exists, "voices_ready": voices_exists}
                )
        except Exception as e:
            return ComponentHealth(
                name="Biometric vault",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    # ========================================================================
    # HARDWARE DEPENDENCIES
    # ========================================================================
    
    def check_camera(self) -> ComponentHealth:
        """Verifica disponibilidade de câmera."""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return ComponentHealth(
                    name="camera",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message="Câmera disponível"
                )
            else:
                return ComponentHealth(
                    name="camera",
                    status=ComponentStatus.OFFLINE,
                    available=False,
                    message="Câmera não detectada ou em uso",
                    error="Camera not available"
                )
        except Exception as e:
            return ComponentHealth(
                name="camera",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro ao acessar câmera: {str(e)}",
                error=str(e)
            )
    
    def check_microphone(self) -> ComponentHealth:
        """Verifica disponibilidade de microfone."""
        try:
            import sounddevice
            devices = sounddevice.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if input_devices:
                return ComponentHealth(
                    name="microfone",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message=f"{len(input_devices)} dispositivo(s) de entrada detectado(s)",
                    details={"devices": len(input_devices)}
                )
            else:
                return ComponentHealth(
                    name="microfone",
                    status=ComponentStatus.OFFLINE,
                    available=False,
                    message="Nenhum microfone detectado",
                    error="No input devices"
                )
        except Exception as e:
            return ComponentHealth(
                name="microfone",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro: {str(e)}",
                error=str(e)
            )
    
    def check_screen_mirror(self) -> ComponentHealth:
        """Verifica capacidade de espelhamento de tela."""
        try:
            import mss
            with mss.mss() as sct:
                # Tentar capturar um frame
                monitor = sct.monitors[0]
                img = sct.grab(monitor)
                return ComponentHealth(
                    name="espelhamento_tela",
                    status=ComponentStatus.ONLINE,
                    available=True,
                    message="Captura de tela funcionando",
                    details={"resolution": f"{img.width}x{img.height}"}
                )
        except Exception as e:
            return ComponentHealth(
                name="espelhamento_tela",
                status=ComponentStatus.ERROR,
                available=False,
                message=f"Erro ao capturar tela: {str(e)}",
                error=str(e)
            )
    
    # ========================================================================
    # CHECK ALL
    # ========================================================================
    
    def check_all(self) -> Dict[str, ComponentHealth]:
        """Executa todos os health checks."""
        checks = {
            # Nucleo Cognitivo
            "smart_router": self.check_smart_router(),
            "unified_memory": self.check_unified_memory(),
            "engineer_brain": self.check_engineer_brain(),
            "adaptive_persona": self.check_adaptive_persona(),
            
            # Percepção
            "face_engine": self.check_face_engine(),
            "gestures": self.check_gesture_engine(),
            "objects": self.check_object_detection(),
            "realtime_audio": self.check_realtime_audio(),
            
            # Sistema
            "os_tools": self.check_os_tools(),
            "browser_engine": self.check_browser_engine(),
            "screen_capture": self.check_screen_capture(),
            "assisted_execution": self.check_assisted_execution(),
            
            # Segurança
            "sentinel_parser": self.check_sentinel_parser(),
            "blackbox": self.check_blackbox(),
            "holodeck": self.check_holodeck(),
            "biometric_vault": self.check_biometric_vault(),
            
            # Hardware
            "camera": self.check_camera(),
            "microphone": self.check_microphone(),
            "screen_mirror": self.check_screen_mirror(),
        }
        
        self.last_check = checks
        return checks
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna sumário do status geral."""
        if not self.last_check:
            self.check_all()
        
        total = len(self.last_check)
        online = sum(1 for c in self.last_check.values() if c.status == ComponentStatus.ONLINE)
        offline = sum(1 for c in self.last_check.values() if c.status == ComponentStatus.OFFLINE)
        degraded = sum(1 for c in self.last_check.values() if c.status == ComponentStatus.DEGRADED)
        error = sum(1 for c in self.last_check.values() if c.status == ComponentStatus.ERROR)
        not_configured = sum(1 for c in self.last_check.values() if c.status == ComponentStatus.NOT_CONFIGURED)
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "degraded": degraded,
            "error": error,
            "not_configured": not_configured,
            "health_percentage": (online / total * 100) if total > 0 else 0
        }


# Global singleton
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Retorna a instância global do health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
