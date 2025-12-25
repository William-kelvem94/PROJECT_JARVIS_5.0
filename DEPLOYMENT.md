# 🚀 Guia de Deployment - JARVIS 5.0

## 📋 Análise: Local vs Docker

### 🏠 **Execução Local (Recomendado para Desenvolvimento)**

#### ✅ **Vantagens:**
- **Acesso direto ao hardware** (câmera, microfone, alto-falantes)
- **Performance máxima** (sem overhead de virtualização)
- **Debugging mais fácil** (acesso direto aos logs e processos)
- **Instalação de dependências nativas** mais simples
- **Integração com Windows** (pywin32, controle do sistema)
- **Desenvolvimento ágil** (mudanças imediatas)

#### ❌ **Desvantagens:**
- **Dependências do sistema** podem conflitar
- **Configuração manual** de cada ambiente
- **Menos isolamento** entre projetos
- **Dificuldade de replicação** em outros sistemas

#### 🎯 **Melhor para:**
- Desenvolvimento e testes
- Uso pessoal diário
- Máxima performance de IA
- Acesso completo ao hardware

---

### 🐳 **Execução Docker (Recomendado para Produção)**

#### ✅ **Vantagens:**
- **Ambiente isolado** e reproduzível
- **Fácil deployment** em qualquer sistema
- **Gerenciamento de dependências** automatizado
- **Escalabilidade** para múltiplas instâncias
- **Versionamento** de ambientes
- **CI/CD** mais simples

#### ❌ **Desvantagens:**
- **Complexidade de acesso ao hardware** (áudio/vídeo)
- **Performance ligeiramente menor** (overhead)
- **Configuração inicial** mais complexa
- **Debugging** menos direto
- **Tamanho da imagem** pode ser grande

#### 🎯 **Melhor para:**
- Produção e deployment
- Ambientes de servidor
- Múltiplos usuários
- Ambientes padronizados

---

## 🏠 Instalação Local

### 1. **Instalação Automática (Recomendado)**
```bash
# Executar instalador inteligente
python scripts/install_dependencies.py
```

### 2. **Instalação Manual**
```bash
# Dependências básicas
pip install -r requirements.txt

# IA e ML
pip install spacy nltk scikit-learn
python -m spacy download pt_core_news_sm

# Visão computacional
pip install opencv-python mediapipe face-recognition

# Deep Learning (opcional)
pip install torch torchvision tensorflow

# Windows específico
pip install pywin32 pycaw pyautogui
```

### 3. **Executar**
```bash
# Teste básico
python main.py --test

# Execução normal
python main.py

# Modo debug
python main.py --debug
```

---

## 🐳 Deployment Docker

### 1. **Build da Imagem**
```bash
# Build básico
docker build -t jarvis:5.0 .

# Build com cache
docker build --no-cache -t jarvis:5.0 .
```

### 2. **Execução com Docker Compose**
```bash
# Produção
docker-compose up -d

# Desenvolvimento
docker-compose --profile dev up

# Logs
docker-compose logs -f jarvis
```

### 3. **Execução Manual**
```bash
# Linux/Mac
docker run -it --rm \
  --device=/dev/video0:/dev/video0 \
  --device=/dev/snd:/dev/snd \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/logs:/app/logs \
  jarvis:5.0

# Windows (PowerShell)
docker run -it --rm `
  -v ${PWD}/models:/app/models `
  -v ${PWD}/logs:/app/logs `
  jarvis:5.0
```

---

## ⚙️ Configurações por Ambiente

### 🏠 **Local - config.json**
```json
{
  "environment": "local",
  "voice": {
    "rate": 200,
    "volume": 0.9
  },
  "vision": {
    "camera_index": 0,
    "resolution": [640, 480]
  },
  "ai": {
    "models_dir": "models",
    "auto_train": true
  }
}
```

### 🐳 **Docker - config.json**
```json
{
  "environment": "docker",
  "voice": {
    "rate": 180,
    "volume": 0.8
  },
  "vision": {
    "camera_index": 0,
    "resolution": [640, 480]
  },
  "ai": {
    "models_dir": "/app/models",
    "auto_train": true
  }
}
```

---

## 🔧 Troubleshooting

### **Problemas Comuns - Local**

#### 1. **Erro de Áudio (PyAudio)**
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# Mac
brew install portaudio
pip install pyaudio
```

#### 2. **Erro de Visão (OpenCV)**
```bash
# Reinstalar OpenCV
pip uninstall opencv-python
pip install opencv-python-headless
```

#### 3. **Erro spaCy**
```bash
# Reinstalar modelo
python -m spacy download pt_core_news_sm --force
```

### **Problemas Comuns - Docker**

#### 1. **Áudio não funciona**
```bash
# Verificar dispositivos
ls -la /dev/snd/

# Adicionar usuário ao grupo audio
docker exec -it jarvis-5.0 usermod -a -G audio jarvis
```

#### 2. **Câmera não detectada**
```bash
# Verificar câmera
ls -la /dev/video*

# Executar com privilégios
docker run --privileged jarvis:5.0
```

#### 3. **Permissões de volume**
```bash
# Ajustar permissões
sudo chown -R 1000:1000 ./models ./logs
```

---

## 📊 Comparação de Performance

| Aspecto | Local | Docker | Vencedor |
|---------|-------|--------|----------|
| **Performance CPU** | 100% | ~95% | 🏠 Local |
| **Acesso Hardware** | Direto | Limitado | 🏠 Local |
| **Facilidade Setup** | Médio | Fácil | 🐳 Docker |
| **Reprodutibilidade** | Baixa | Alta | 🐳 Docker |
| **Debugging** | Fácil | Médio | 🏠 Local |
| **Escalabilidade** | Baixa | Alta | 🐳 Docker |
| **Isolamento** | Baixo | Alto | 🐳 Docker |
| **Tamanho** | Pequeno | Grande | 🏠 Local |

---

## 🎯 Recomendações Finais

### **Para Desenvolvimento:**
```bash
# Use execução local
python scripts/install_dependencies.py
python main.py --debug
```

### **Para Produção:**
```bash
# Use Docker
docker-compose up -d
```

### **Para Testes:**
```bash
# Local é melhor para testes de hardware
python tests/test_vision_system.py
python tests/test_ai_learning.py
```

### **Para Deploy em Servidor:**
```bash
# Docker é essencial
docker build -t jarvis:5.0 .
docker run -d --name jarvis jarvis:5.0
```

---

## 🚀 Próximos Passos

1. **Escolher ambiente** baseado no uso
2. **Executar instalação** apropriada
3. **Testar funcionalidades** básicas
4. **Configurar hardware** (câmera/áudio)
5. **Treinar IA** com suas preferências
6. **Personalizar** configurações

**O JARVIS 5.0 está pronto para funcionar em qualquer ambiente!** 🤖✨
