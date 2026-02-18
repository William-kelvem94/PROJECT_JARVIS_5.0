"""
Módulo de Detecção de Elementos de Interface (UI Detector)
Usa o YOLOv8 (Ultralytics) para identificar ícones, botões e outros componentes visuais.
Esta implementação evita importar o pacote `ultralytics` no momento do import do módulo
para impedir que incompatibilidades de `torch/torchvision` quebrassem o processo de
inicialização. A importação acontece de forma preguiçosa quando o detector for realmente
instanciado e ativado via configuração.
"""

from src.utils.config import config
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Indicador de disponibilidade do Ultralytics (definido durante a
# inicialização preguiçosa)
ULTRALYTICS_AVAILABLE = False


logger = logging.getLogger(__name__)


class UIDetector:
    """Classe para detecção de objetos de interface usando YOLOv8 (Ultralytics).

    A carga do pacote `ultralytics` e do modelo é feita de forma preguiçosa para
    evitar inicializar bibliotecas pesadas/incompatíveis no momento do import do módulo.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.enabled = config.get_setting("vision.yolo_enabled", True)
        self.model = None
        self.model_path = model_path or config.get_setting(
            "vision.yolo_model", "models/vision/yolov8n.pt"
        )
        self._ultralytics_imported = False

        if not self.enabled:
            logger.debug("UIDetector desativado pela configuração.")
            return

        # Don't load model immediately - wait for first use

    def detect_elements(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detecta elementos de UI na imagem.
        Retorna: Lista de dicionários com {label, confidence, x, y, width, height, center}
        """
        if not self.enabled:
            return []

        # Lazy import and model loading
        if self.model is None and not self._ultralytics_imported:
            try:
                # Importação preguiçosa do Ultralytics
                from ultralytics import YOLO  # type: ignore

                # Resolve path
                path = self.model_path
                if not os.path.isabs(path):
                    path = str(Path(__file__).parent.parent.parent.parent / path)

                self.model = YOLO(path)
                globals()["ULTRALYTICS_AVAILABLE"] = True
                self._ultralytics_imported = True
                logger.info(f"Modelo YOLO carregado: {path}")
            except Exception as e:
                logger.warning(
                    f"Ultralytics/YOLO indisponível ou falha ao carregar o modelo: {e}"
                )
                self.enabled = False
                return []

        if self.model is None:
            return []

        try:
            results = self.model(image_path, verbose=False)
            detections: List[Dict[str, Any]] = []

            for r in results:
                boxes = getattr(r, "boxes", [])
                for box in boxes:
                    # Coordenadas (xyxy)
                    coords = box.xyxy[0].tolist()
                    if len(coords) < 4:
                        continue
                    x1, y1, x2, y2 = coords
                    w = x2 - x1
                    h = y2 - y1

                    label_id = (
                        int(box.cls[0])
                        if hasattr(box, "cls") and len(box.cls) > 0
                        else 0
                    )
                    label = getattr(self.model, "names", {}).get(
                        label_id, str(label_id)
                    )
                    confidence = (
                        float(box.conf[0])
                        if hasattr(box, "conf") and len(box.conf) > 0
                        else 0.0
                    )

                    if confidence >= config.get_setting("vision.yolo_confidence", 0.25):
                        detections.append(
                            {
                                "label": label,
                                "confidence": confidence,
                                "x": int(x1),
                                "y": int(y1),
                                "width": int(w),
                                "height": int(h),
                                "center": (int(x1 + w / 2), int(y1 + h / 2)),
                            }
                        )

            logger.info(f"YOLO detectou {len(detections)} elementos em {image_path}")
            return detections

        except Exception as e:
            logger.error(f"Erro na detecção YOLO: {e}")
            return []

    def get_summary(self, detections: List[Dict[str, Any]]) -> str:
        """Gera uma descrição textual do que foi visto"""
        if not detections:
            return "Nenhum elemento visual identificado além de texto."

        summary_parts: List[str] = []
        labels = [d["label"] for d in detections]
        unique_labels = set(labels)

        for label in unique_labels:
            count = labels.count(label)
            summary_parts.append(f"{count} {label}(s)")

        return "Elementos visuais identificados: " + ", ".join(summary_parts)


# Lazy global instance - will be created only when first accessed
_ui_detector_instance = None


def get_ui_detector():
    """Get the global UI detector instance (lazy loading)"""
    global _ui_detector_instance
    if _ui_detector_instance is None:
        _ui_detector_instance = UIDetector()
    return _ui_detector_instance


# For backward compatibility, create a lazy property
class LazyUIDetector:
    def __getattr__(self, name):
        return getattr(get_ui_detector(), name)

    def __call__(self, *args, **kwargs):
        return get_ui_detector()(*args, **kwargs)


# Global instance with lazy loading
ui_detector = LazyUIDetector()
