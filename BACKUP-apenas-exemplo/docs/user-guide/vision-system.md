# 👁️ JARVIS 5.0 - Sistema de Visão

**Computer Vision, FaceID e Análise Visual**

---

## 📖 Visão Geral

O Sistema de Visão do JARVIS permite:
- 🎭 **Reconhecimento Facial** (FaceID)
- 🖼️ **Análise de Tela** (Screen Understanding)
- ✋ **Detecção de Gestos** (Hand Tracking)
- 📷 **Captura Inteligente** (Smart Screenshots)
- 👥 **Rastreamento de Objetos** (YOLO v8)

---

## 🎭 FaceID - Reconhecimento Facial

### Como Funciona

JARVIS usa **MediaPipe Face Detection** + **DeepFace** para:
1. Detectar rostos na câmera
2. Extrair características faciais (embeddings)
3. Comparar com banco de dados local
4. Identificar pessoas com >95% confiança

### Cadastrar seu Rosto

#### Método 1: Via Dashboard

1. Abra **Control Dashboard**
2. Tab **👁️ Vision**
3. Seção **FaceID Management**
4. Clique **📷 Capture New Face**
5. Digite seu nome
6. Olhe para câmera (~3 segundos)
7. ✅ "Face registered: William"

#### Método 2: Via Comando de Voz

```
"JARVIS, cadastrar meu rosto"
"JARVIS, registrar rosto de William"
```

### Usar FaceID

**Auto-reconhecimento:**
- JARVIS detecta automaticamente ao iniciar
- Mensagem: *"Olá William, sistemas inicializados"*

**Reconhecimento manual:**
```
"Quem sou eu?"
"Me reconheça"
```

### Gerenciar Faces Cadastradas

**Dashboard → Vision → FaceID Management:**
- Lista de rostos cadastrados
- Opção de deletar
- Re-treinar reconhecimento

**Arquivos locais:**
- Faces armazenadas em: `data/faces/`
- Formato: `{nome}_{timestamp}.jpg`
- Embeddings: `data/memory/face_embeddings.json`

---

## 🖼️ Análise de Tela

### Captura e Descrição

JARVIS pode "ver" sua tela e descrever o que está acontecendo.

#### Comandos

```
"O que você está vendo?"
"Descreva a tela"
"Há algum erro na tela?"
"Leia a mensagem da tela"
```

#### Tecnologias

- **Screenshot:** PIL + win32api
- **OCR:** Tesseract ou EasyOCR
- **Análise Visual:** Gemini Vision API

#### Exemplo de Uso

**Você:** "JARVIS, o que você vê na tela?"

**JARVIS:** *"Vejo um editor de código com Python aberto. Há um erro na linha 47: 'NameError: name 'variavel' is not defined'. Você esqueceu de declarar a variável antes de usar."*

---

## ✋ Detecção de Gestos

### Gestos Suportados

| Gesto | Ação | Status |
|-------|------|--------|
| 👍 Polegar para cima | Aprovar/Confirmar | ✅ Ativo |
| 👎 Polegar para baixo | Reprovar/Cancelar | ✅ Ativo |
| ✋ Mão aberta | Pausar | ✅ Ativo |
| ✊ Punho fechado | Continuar | ✅ Ativo |
| ☝️ Dedo apontando | Selecionar área | 🚧 Em desenvolvimento |

### Ativar Gestos

**Dashboard → Vision → Gesture Control:**
- [ ] Enable Hand Tracking
- [x] Use gestures for feedback

**Uso:**
1. Marque "Enable Hand Tracking"
2. JARVIS processa gestos da câmera
3. Use 👍 ou 👎 para dar feedback visual

**Latência:** ~100ms (depende da GPU)

---

## 📷 Captura Inteligente

### Tipos de Captura

#### 1. Screenshot Rápido

```python
# Via comando
"JARVIS, tire um screenshot"
```

Salvo em: `data/screenshots/capture_{timestamp}.png`

#### 2. Captura de Câmera

```python
"JARVIS, tire uma foto"
```

Salvo em: `data/captures/photo_{timestamp}.jpg`

#### 3. Captura com Análise

```python
"JARVIS, analise a tela e salve"
```

Salva + gera análise em: `data/processed/{timestamp}_analysis.json`

### Histórico

**Dashboard → Vision → Capture History:**
- Últimas 50 capturas
- Miniatura + timestamp
- Opção de deletar

---

## 👥 Rastreamento de Objetos (YOLO)

### O que é YOLO?

**YOLO v8n** (You Only Look Once) detecta:
- Pessoas
- Animais
- Objetos comuns (80 classes)

### Classes Detectadas

```
person, car, bicycle, dog, cat, laptop, keyboard, mouse, 
phone, cup, bottle, chair, couch, tv, book, etc.
```

Lista completa: 80 objetos COCO dataset

### Usar Detecção

**Via código:**
```python
from src.core.vision.vision_processor import VisionProcessor

vision = VisionProcessor()
frame = vision.capture_frame()
detections = vision.yolo_detect(frame)

for obj in detections:
    print(f"Detectado: {obj['class']} ({obj['confidence']:.2f})")
```

**Via comando:**
```
"JARVIS, o que há na câmera?"
```

---

## ⚙️ Configuração Avançada

### Arquivo de Config

**`config/ai_config.yaml`**

```yaml
vision:
  camera:
    device_id: 0  # Câmera padrão
    resolution: [1280, 720]
    fps: 30
  
  faceid:
    enabled: true
    confidence_threshold: 0.95
    recognition_interval: 2.0  # segundos
  
  yolo:
    model: "yolov8n.pt"  # nano model (rápido)
    confidence: 0.5
    device: "cuda"  # ou "cpu"
  
  hand_tracking:
    enabled: false
    min_detection_confidence: 0.7
    max_num_hands: 2
```

### Dashboard Settings

**Control Dashboard → Vision:**

1. **Camera Selection**
   - Dropdown com câmeras disponíveis
   - Resolução: 480p, 720p, 1080p
   - FPS: 15, 30, 60

2. **FaceID Settings**
   - Threshold de confiança (0.85 - 0.99)
   - Auto-greeting ao reconhecer
   - Modo Unknown Face Alert

3. **YOLO Detection**
   - Modelo: nano, small, medium, large
   - Classes a detectar (filtro)
   - Exibir bounding boxes

---

## 🔧 Solução de Problemas

### "Câmera não encontrada"

**Soluções:**
1. Verifique se câmera está conectada
2. Feche outros apps usando câmera (Zoom, Teams)
3. Dashboard → Vision → Camera dropdown → Selecione outra
4. Reinicie JARVIS com Admin

### "FaceID não reconhece"

**Motivos:**
- Pouca iluminação 💡
- Rosto parcialmente coberto (máscara, óculos escuros)
- Ângulo muito lateral
- Banco de dados corrompido

**Soluções:**
1. Melhore iluminação
2. Olhe diretamente para câmera
3. Recadastre seu rosto
4. Baixe threshold para 0.90

### "YOLO muito lento"

**Otimizações:**
1. Troque modelo: `yolov8l.pt` → `yolov8n.pt`
2. Reduza resolução: 1080p → 720p
3. Reduza FPS: 30 → 15
4. Use GPU se disponível (`device: "cuda"`)

### "Hand tracking travando"

**Soluções:**
1. Desative temporariamente
2. Reduza `max_num_hands: 2` → `1`
3. Aumente `min_detection_confidence: 0.7` → `0.8`

---

## 📊 Performance

### Benchmarks

**Hardware:** RTX 3060, i7-10700K

| Operação | FPS | Latência |
|----------|-----|----------|
| FaceID | 30 | ~33ms |
| YOLO nano | 60 | ~16ms |
| YOLO large | 20 | ~50ms |
| Hand Tracking | 30 | ~33ms |
| Screenshot + OCR | - | ~200ms |

### Otimização de Memória

JARVIS usa **lazy loading**:
- Modelos carregam sob demanda
- Libera RAM quando não usados
- Cache de embeddings faciais

---

## 🆘 Suporte

- **Câmera:** [device-manager.md](../maintenance/device-manager.md)
- **Erros:** [troubleshooting.md](../maintenance/troubleshooting.md)
- **Performance:** [performance.md](../maintenance/performance.md)

---

<div align="center">

**Visão é conhecimento. JARVIS vê tudo. 👁️**

</div>
