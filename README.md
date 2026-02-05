# 🤖 JARVIS 5.0 - Just A Rather Very Intelligent System

> Assistente de IA avançado com visão computacional, reconhecimento de voz e automação inteligente

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## ⚡ Início Rápido

### Windows

```bash
# Clique duplo no arquivo:
JARVIS.bat

# OU execute no terminal:
.\JARVIS.bat
```

### Modo Automático (Recomendado)

O launcher detecta e resolve automaticamente:
- ✅ Verifica Python instalado
- ✅ Instala PyQt6 se necessário
- ✅ Inicia HUD transparente
- ✅ Ativa reconhecimento de voz

---

## 🎯 O Que é JARVIS?

JARVIS é um assistente de IA inspirado no sistema da Marvel, com:

- 🧠 **Cérebro Híbrido**: Groq (Llama 3) + Gemini (Google)
- 👁️ **Visão Computacional**: OCR, detecção de objetos, análise de tela
- 🎤 **Reconhecimento de Voz**: Wake word + comandos naturais
- 🗣️ **Síntese de Voz**: Respostas faladas naturais
- 🖥️ **HUD Transparente**: Interface estilo Iron Man
- 🤖 **Automação**: Controle de sistema e aplicativos
- 📷 **FaceID**: Reconhecimento facial
- 🌐 **Hive Mind**: Sincronização entre dispositivos (opcional)

---

## 🚀 Funcionalidades

### Interface Visual
- **HUD Transparente**: Overlay estilo Iron Man com reator pulsante
- **Estados Visuais**: Verde (escutando), Azul (pensando), Laranja (falando)
- **Click-Through**: Você pode clicar através do HUD

### Interação por Voz
```
Você: "Jarvis"
JARVIS: [HUD fica verde] "Pois não?"
Você: "Abra o Chrome"
JARVIS: [HUD fica azul, processa, abre Chrome]
```

### Visão Computacional
- Captura de tela inteligente
- OCR (Tesseract + EasyOCR)
- Detecção de objetos (YOLO)
- Análise de interface

### Automação
- Controle de mouse e teclado
- Abertura de programas
- Manipulação de arquivos
- Execução de workflows

---

## 📋 Pré-requisitos

- **Python 3.10+**
- **Windows 10/11** (para UI Automation)
- **Microfone** (para comandos de voz)
- **Webcam** (opcional, para FaceID)

---

## 🔧 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

### 2. Execute o Launcher
```bash
JARVIS.bat
```

O launcher instala automaticamente todas as dependências necessárias.

### 3. Configure (Opcional)

Edite `config.yaml` para adicionar suas API keys:

```yaml
brain:
  groq_api_key: "gsk_..."      # https://console.groq.com
  gemini_api_key: "AI..."      # https://makersuite.google.com
```

---

## 💻 Como Usar

### Interface Gráfica (HUD)
```bash
python main_singularity.py
```

**O que acontece:**
1. HUD transparente aparece no canto inferior direito
2. Reator pulsante indica status do sistema
3. Sistema escuta "Jarvis" como wake word
4. Dê seu comando e veja o HUD reagir

### Comandos de Voz

```
"Jarvis, abra o navegador"
"Jarvis, qual é a hora?"
"Jarvis, tire uma screenshot"
"Jarvis, leia o que está na tela"
"Jarvis, execute o código"
```

### Linha de Comando (Avançado)

```bash
# Captura de tela completa
python legacy/main.py capture

# Captura de área específica
python legacy/main.py capture --area 100,100,800,600 --process

# Processar imagem existente
python legacy/main.py process --input imagem.png --analyze

# Processamento em lote
python legacy/main.py batch --input-dir ./imagens/
```

---

## 🏗️ Arquitetura

```
PROJECT_JARVIS_5.0/
├── src/                        # Código fonte
│   ├── interface/             # HUD e interface visual
│   │   └── hud.py            # HUD transparente ⭐
│   ├── core/                  # Módulos principais
│   │   ├── ai_agent.py       # Cérebro (Groq + Gemini)
│   │   ├── voice_controller.py # Reconhecimento de voz
│   │   ├── screen_capture.py  # Captura de tela
│   │   ├── ocr_processor.py   # OCR
│   │   ├── action_controller.py # Automação
│   │   └── camera_controller.py # FaceID
│   ├── database/              # Persistência
│   └── utils/                 # Utilitários
│
├── jarvis_core/               # Sistema modular (Singularity)
│   ├── brain/                # Cérebro híbrido
│   ├── senses/               # Visão + Audição
│   ├── mouth/                # TTS
│   ├── hive_mind/            # Sync distribuído
│   ├── world/                # IoT
│   ├── interface/            # HUD
│   └── guardian/             # Segurança
│
├── legacy/                    # Sistema antigo (preservado)
├── data/                      # Dados e cache
├── config.yaml               # Configuração
├── main_singularity.py       # Entry point ⭐
└── JARVIS.bat                # Launcher ⭐
```

---

## 🎨 Estados do HUD

| Cor | Estado | Significado |
|-----|--------|-------------|
| 🔵 Ciano | Idle | Sistema online, aguardando |
| 🟢 Verde | Listening | Escutando comando |
| 🔵 Azul | Thinking | Processando |
| 🟠 Laranja | Speaking | Falando |
| 🔴 Vermelho | Error | Erro detectado |

---

## ⚙️ Configuração Avançada

### API Keys

```yaml
brain:
  router: "auto"              # auto, groq, gemini
  groq_api_key: ""           # Groq API
  gemini_api_key: ""         # Gemini API

hive_mind:
  enabled: false             # Sync entre dispositivos
  remote_name: "gdrive"
  remote_path: "JARVIS_Hive"

interface:
  hud_enabled: true
  transparency: 0.9
  orb_color: "#00D9FF"

guardian:
  watchdog_enabled: true
  safe_mode_threshold: 3
  privacy_filter: true
```

---

## 🧪 Testes

```bash
# Testar HUD
python src/interface/hud.py

# Testar Voice Controller
python -c "from src.core.voice_controller import voice_controller; voice_controller.speak('Teste')"

# Testar AI Agent
python -c "from src.core.ai_agent import ai_agent; ai_agent.process_command('Olá')"
```

---

## 🐛 Troubleshooting

### PyQt6 não encontrado
```bash
python -m pip install PyQt6
```

### Voice não funciona
```bash
pip install SpeechRecognition pyaudio
```

### HUD não aparece
1. Verifique se PyQt6 está instalado
2. Veja logs em `jarvis_singularity.log`
3. Execute com privilégios de administrador

### Wake word não detecta
1. Verifique microfone
2. Ajuste sensibilidade em `config.yaml`
3. Teste com `python -c "import speech_recognition"`

---

## 📚 Documentação

- [**QUICKSTART.md**](QUICKSTART.md) - Guia de início rápido
- [**HOW_TO_START.md**](HOW_TO_START.md) - Instruções detalhadas
- [**Walkthrough**](file:///C:/Users/willi/.gemini/antigravity/brain/9976850e-9bb7-4c9e-b7f2-cf4ba8a4e2b7/walkthrough.md) - Implementação completa

---

## 🤝 Contribuição

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **Tesseract OCR** - Engine OCR
- **Google Gemini** - IA avançada
- **Groq** - Inferência rápida
- **PyQt6** - Interface gráfica
- **OpenCV** - Processamento de imagens
- **spaCy** - NLP
- **Whisper** - Transcrição de voz

---

## 🔄 Roadmap

### ✅ Implementado
- [x] HUD transparente estilo Iron Man
- [x] Reconhecimento de voz (wake word)
- [x] AI Agent (Groq + Gemini)
- [x] Visão computacional
- [x] Automação de sistema
- [x] FaceID
- [x] Arquitetura modular

### 🚧 Em Desenvolvimento
- [ ] TTS aprimorado
- [ ] Hive Mind (sync entre dispositivos)
- [ ] Controle por gestos
- [ ] Workflows complexos
- [ ] Integração com IoT

### 🔮 Futuro
- [ ] Suporte Linux/macOS
- [ ] App móvel
- [ ] Interface web
- [ ] Plugins de terceiros
- [ ] Marketplace de skills

---

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/PROJECT_JARVIS_5.0/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/PROJECT_JARVIS_5.0/discussions)
- 📖 **Wiki**: [Documentação Completa](https://github.com/seu-usuario/PROJECT_JARVIS_5.0/wiki)

---

## ⭐ Star este repositório se achou útil!

**JARVIS 5.0** - Seu assistente de IA pessoal está pronto para uso! 🚀

Execute `JARVIS.bat` e comece a interagir!
