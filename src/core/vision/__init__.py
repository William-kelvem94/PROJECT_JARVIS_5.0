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

from .vision_system import VisionSystem
from .screen_capture import ScreenCapture
from .ocr_processor import OCRProcessor
from .gesture_recognizer import GestureRecognizer
from .ui_detector import UIDetector
from .camera_controller import CameraController
from .vision_enhancer import VisionEnhancer

__all__ = [
    'VisionSystem',
    'ScreenCapture',
    'OCRProcessor',
    'GestureRecognizer',
    'UIDetector',
    'CameraController',
    'VisionEnhancer'
]
