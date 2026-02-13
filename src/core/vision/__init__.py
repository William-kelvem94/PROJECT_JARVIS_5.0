"""
🎥 JARVIS Vision System - Sistema de Visão Computacional
=======================================================

Este módulo contém todas as funcionalidades de processamento visual do JARVIS,
incluindo captura de tela, OCR, reconhecimento de gestos, detecção de UI e
processamento avançado de imagens.

Módulos Principais:
- vision_system: Sistema central de visão
- screen_capture: Captura e processamento de tela
- ocr_processor: Reconhecimento óptico de caracteres
- gesture_recognizer: Reconhecimento de gestos
- ui_detector: Detecção de elementos de interface
- camera_controller: Controle de câmera
- vision_enhancer: Melhorias de imagem
- vision_language_model: Integração visão-linguagem

Exemplo de uso:
    from src.core.vision import VisionSystem, ScreenCapture

    vision = VisionSystem()
    capture = ScreenCapture()
"""

# Lazy import to avoid heavy dependencies at startup
def __getattr__(name):
    if name == "VisionSystem":
        try:
            from .vision_system import VisionSystem
            return VisionSystem
        except ImportError as e:
            print(f"WARNING: VisionSystem not available: {e}")
            return None
    elif name == "ScreenCapture":
        try:
            from .screen_capture import ScreenCapture
            return ScreenCapture
        except ImportError as e:
            print(f"WARNING: ScreenCapture not available: {e}")
            return None
    elif name == "OCRProcessor":
        try:
            from .ocr_processor import OCRProcessor
            return OCRProcessor
        except ImportError as e:
            print(f"WARNING: OCRProcessor not available: {e}")
            return None
    elif name == "GestureRecognizer":
        try:
            from .gesture_recognizer import GestureRecognizer
            return GestureRecognizer
        except ImportError as e:
            print(f"WARNING: GestureRecognizer not available: {e}")
            return None
    elif name == "UIDetector":
        try:
            from .ui_detector import UIDetector
            return UIDetector
        except ImportError as e:
            print(f"WARNING: UIDetector not available: {e}")
            return None
    elif name == "CameraController":
        try:
            from .camera_controller import CameraController
            return CameraController
        except ImportError as e:
            print(f"WARNING: CameraController not available: {e}")
            return None
    elif name == "VisionEnhancer":
        try:
            from .vision_enhancer import VisionEnhancer
            return VisionEnhancer
        except ImportError as e:
            print(f"WARNING: VisionEnhancer not available: {e}")
            return None
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Note: Dynamic attributes via __getattr__ handle the imports lazily
# to avoid heavy dependencies at startup.

__all__ = [
    'VisionSystem',
    'ScreenCapture',
    'OCRProcessor',
    'GestureRecognizer',
    'UIDetector',
    'CameraController',
    'VisionEnhancer',
    'get_vision_system'
]

def get_vision_system(*args, **kwargs):
    from .vision_system import VisionSystem
    return VisionSystem(*args, **kwargs)

# Export symbols
__all__ = [
    'VisionSystem',
    'ScreenCapture',
    'OCRProcessor',
    'GestureRecognizer',
    'UIDetector',
    'CameraController',
    'VisionEnhancer',
    'get_vision_system'
]
