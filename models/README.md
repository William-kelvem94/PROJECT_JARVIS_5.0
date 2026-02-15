# 🧠 JARVIS 5.0 - Models Directory

Esta pasta contém todos os modelos de Machine Learning e Deep Learning utilizados pelo JARVIS 5.0.

---

## 📂 **Estrutura**

```
models/
├── speech/                       # Modelos de áudio/voz
│   └── vosk-model-small-pt-0.3/  # Reconhecimento de voz offline (PT-BR)
├── training/                     # Modelos treinados/fine-tuned
│   └── continual/                # Aprendizado contínuo
├── vision/                       # Modelos de visão computacional
│   ├── hand_landmarker.task      # MediaPipe Hand Tracking
│   └── yolov8n.pt                # YOLO v8 Nano (PRINCIPAL)
└── yolo/                         # Modelos YOLO adicionais
    └── DOWNLOAD.md               # Instruções para baixar variantes YOLO
```

---

## 🎯 **Modelos Incluídos**

### **1. YOLOv8n (You Only Look Once v8 Nano)**
- **Arquivo**: `yolov8n.pt`
- **Tamanho**: 6.5 MB
- **Uso**: Detecção de objetos em tempo real
- **Classes**: 80 objetos do COCO dataset
- **Performance**: ~45 FPS em CPU, ~200 FPS em GPU
- **Localização**: `models/vision/yolov8n.pt` ✅ (única cópia)

**Usado em:**
- Detecção de UI elements
- Reconhecimento de objetos na tela
- Análise de contexto visual

**Variantes disponíveis**: Veja `models/yolo/DOWNLOAD.md` para instruções

---

### **2. MediaPipe Hand Landmarker**
- **Arquivo**: `hand_landmarker.task`
- **Tamanho**: 7.8 MB
- **Uso**: Detecção e rastreamento de mãos
- **Pontos**: 21 landmarks por mão
- **Performance**: Tempo real (30+ FPS)

**Usado em:**
- Controle por gestos
- Detecção de interação do usuário
- Análise de atividade

---

### **3. Vosk Speech Recognition (PT-BR)**
- **Diretório**: `speech/vosk-model-small-pt-0.3/`
- **Idioma**: Português Brasileiro
- **Tamanho**: ~40 MB (descompactado)
- **Tipo**: Modelo pequeno (rápido, menos preciso)
- **Uso**: Reconhecimento de voz offline

**Usado em:**
- Wake word detection
- Comandos de voz offline
- Transcrição em tempo real

**Arquivos:**
- `am/` - Modelo acústico
- `graph/` - Grafo de linguagem
- `phones.txt` - Mapeamento de fonemas
- `conf/` - Configurações

---

### **4. Continual Learning Models**
- **Diretório**: `training/continual/`
- **Uso**: Armazena modelos fine-tuned
- **Formato**: PyTorch (.pt, .pth), LoRA adapters

**Modelos esperados:**
- `qwen_lora_adapter/` - Adaptador LoRA para Qwen
- `checkpoints/` - Checkpoints de treinamento
- `best_model.pt` - Melhor modelo treinado

---

## 📥 **Download de Modelos**

### **Modelos Incluídos (Já Baixados)**
✅ YOLOv8n - Incluído  
✅ MediaPipe Hand Landmarker - Incluído  
✅ Vosk PT-BR Small - Incluído  

### **Modelos Opcionais (Download Manual)**

#### **YOLOv8 Variantes Maiores:**
```bash
# YOLOv8s (Small) - Mais preciso
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt

# YOLOv8m (Medium) - Balanceado
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt

# YOLOv8l (Large) - Alta precisão
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8l.pt
```

#### **Vosk Modelos Maiores (Mais Precisos):**
```bash
# Modelo médio PT-BR (~1 GB)
wget https://alphacephei.com/vosk/models/vosk-model-pt-fb-v0.1.1-20220516_2113.zip

# Extrair
unzip vosk-model-pt-fb-v0.1.1-20220516_2113.zip -d models/speech/
```

#### **Whisper (Alternativa ao Vosk):**
```bash
# Instalado via pip, modelos baixados automaticamente
pip install openai-whisper

# Modelos disponíveis: tiny, base, small, medium, large
# Baixados automaticamente no primeiro uso
```

---

## 🔧 **Gerenciamento de Modelos**

### **Verificar Modelos Instalados:**
```python
from pathlib import Path

models_dir = Path("models")
for model in models_dir.rglob("*.pt"):
    size_mb = model.stat().st_size / (1024 * 1024)
    print(f"{model.name}: {size_mb:.1f} MB")
```

### **Limpar Modelos Duplicados:**
```bash
# Manter apenas em models/vision/
del models\yolov8n.pt
del models\yolo\yolov8n.pt
```

### **Atualizar YOLOv8:**
```python
from ultralytics import YOLO

# Baixa automaticamente a versão mais recente
model = YOLO('yolov8n.pt')
```

---

## 📊 **Uso de Espaço**

| Modelo | Tamanho | Localização |
|--------|---------|-------------|
| YOLOv8n | 6.5 MB | vision/ |
| Hand Landmarker | 7.8 MB | vision/ |
| Vosk PT-BR Small | ~40 MB | speech/ |
| **TOTAL** | **~54 MB** | - |

**Economia**: ~13 MB removidos (duplicatas do YOLOv8n)

---

## 🚀 **Performance**

### **YOLOv8n:**
- **CPU**: ~45 FPS (Intel i5+)
- **GPU**: ~200 FPS (NVIDIA GTX 1060+)
- **Latência**: ~20ms por frame

### **MediaPipe Hand:**
- **CPU**: ~30 FPS
- **GPU**: ~60 FPS
- **Latência**: ~15ms por frame

### **Vosk PT-BR:**
- **CPU**: Tempo real (streaming)
- **Latência**: ~100-200ms
- **Precisão**: ~85% (modelo small)

---

## 🔄 **Atualização de Modelos**

### **Script Automático:**
```bash
python scripts/install/download_models.py
```

### **Manual:**
1. Baixar modelo do repositório oficial
2. Colocar na pasta apropriada (`vision/`, `speech/`, etc)
3. Atualizar configuração em `config/ai_config.yaml`

---

## 📝 **Notas**

- ✅ Modelos são versionados via Git LFS (Large File Storage)
- ✅ Modelos grandes (>100MB) não são commitados
- ✅ `.gitignore` configurado para ignorar checkpoints temporários
- ✅ Modelos treinados localmente ficam em `training/continual/`

---

## 🆘 **Troubleshooting**

### **Modelo não encontrado:**
```python
# Verificar se existe
from pathlib import Path
model_path = Path("models/vision/yolov8n.pt")
print(f"Exists: {model_path.exists()}")
```

### **Erro ao carregar modelo:**
```python
# Redownload
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Baixa automaticamente
```

### **Vosk não funciona:**
```bash
# Verificar estrutura
ls models/speech/vosk-model-small-pt-0.3/
# Deve conter: am/, graph/, conf/, phones.txt
```

---

**Última Atualização**: 2026-02-09  
**Mantido por**: JARVIS 5.0 Team
