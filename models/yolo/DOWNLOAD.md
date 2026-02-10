# YOLOv8 Models - Download Instructions

## 📥 Como Baixar Modelos YOLO

### Modelo Principal (Já Instalado)
✅ **YOLOv8n** está em: `models/vision/yolov8n.pt`

### Download de Variantes YOLO

#### **Opção 1: Via Python (Automático)**
```python
from ultralytics import YOLO

# Nano (mais rápido, menos preciso) - 6.5 MB
model = YOLO('yolov8n.pt')

# Small (balanceado) - 22 MB
model = YOLO('yolov8s.pt')

# Medium (mais preciso) - 52 MB
model = YOLO('yolov8m.pt')

# Large (alta precisão) - 87 MB
model = YOLO('yolov8l.pt')

# Extra Large (máxima precisão) - 131 MB
model = YOLO('yolov8x.pt')
```

#### **Opção 2: Download Manual**
```bash
# YOLOv8 Nano (6.5 MB)
curl -L https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -o yolov8n.pt

# YOLOv8 Small (22 MB)
curl -L https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt -o yolov8s.pt

# YOLOv8 Medium (52 MB)
curl -L https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt -o yolov8m.pt

# YOLOv8 Large (87 MB)
curl -L https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8l.pt -o yolov8l.pt

# YOLOv8 Extra Large (131 MB)
curl -L https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt -o yolov8x.pt
```

#### **Opção 3: Via PowerShell (Windows)**
```powershell
# YOLOv8 Nano
Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt" -OutFile "yolov8n.pt"

# YOLOv8 Small
Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt" -OutFile "yolov8s.pt"
```

---

## 📊 Comparação de Modelos

| Modelo | Tamanho | mAP50-95 | Velocidade (CPU) | Velocidade (GPU) |
|--------|---------|----------|------------------|------------------|
| YOLOv8n | 6.5 MB | 37.3% | ~45 FPS | ~200 FPS |
| YOLOv8s | 22 MB | 44.9% | ~30 FPS | ~150 FPS |
| YOLOv8m | 52 MB | 50.2% | ~20 FPS | ~120 FPS |
| YOLOv8l | 87 MB | 52.9% | ~15 FPS | ~100 FPS |
| YOLOv8x | 131 MB | 53.9% | ~10 FPS | ~80 FPS |

---

## 🎯 Recomendações

- **Para CPU**: Use YOLOv8n (mais rápido)
- **Para GPU (GTX 1060+)**: Use YOLOv8s ou YOLOv8m
- **Para máxima precisão**: Use YOLOv8l ou YOLOv8x

---

## 📝 Uso no JARVIS

Após baixar, o modelo será usado automaticamente pelo sistema de visão:

```python
from src.core.vision.vision_system import get_vision_system

vision = get_vision_system()
# Usa automaticamente o modelo em models/vision/yolov8n.pt
```

Para usar um modelo diferente, configure em `config/ai_config.yaml`:

```yaml
vision:
  yolo_model: "models/yolo/yolov8s.pt"  # Trocar para modelo desejado
```

---

## 🔗 Links Oficiais

- **Documentação**: https://docs.ultralytics.com/
- **GitHub**: https://github.com/ultralytics/ultralytics
- **Modelos**: https://github.com/ultralytics/assets/releases

---

**Última Atualização**: 2026-02-09
