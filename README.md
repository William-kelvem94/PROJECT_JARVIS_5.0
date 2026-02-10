# 🤖 JARVIS 5.0 - Singularity Core

> Assistente de IA Autônomo com Neural Engine Híbrido (Local + Cloud), Visão Computacional Avançada e Auto-Recuperação.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Singularity_Active-success.svg)]()

---

## ⚡ Início Rápido

### 🚀 Launcher Autônomo (Recomendado)

**Execute com um clique para iniciar o Singularity Core:**

```bash
START_JARVIS.bat
```

### 🎯 O que o Singularity Launcher faz?

O `START_JARVIS.bat` é um **orquestrador autônomo** que:

1.  ✅ **Auto-detecta e Repara Ambiente** - Corrige dependências quebradas.
2.  ✅ **Sincroniza Modelos Neurais** - Baixa Ollama (Gemma/Qwen) e modelos de visão.
3.  ✅ **Inicia Servidores Locais** - Garante que o Ollama e serviços de áudio estejam rodando.
4.  ✅ **Auto-Healing** - Se o sistema falhar, ele analisa o erro, aplica correções e reinicia.

---

## 🧠 Arquitetura "Singularity"

JARVIS 5.0 foi reescrito com uma arquitetura modular de alta performance:

-   **🧠 Intelligence**:
    -   **Local Brain**: Modelos leves (Gemma 2, Qwen 2.5) rodando 100% offline via Ollama.
    -   **Cloud Boost**: Integração com Gemini 1.5 Pro para tarefas complexas.
    -   **Brain Router**: Decide automaticamente entre IA Local (Privacidade/Velocidade) ou Nuvem (Inteligência).

-   **👁️ Vision System**:
    -   **YOLOv8**: Detecção de objetos em tempo real.
    -   **MediaPipe**: Rastreamento de mãos e face.
    -   **OCR Híbrido**: Leitura de tela instantânea.

-   **🎤 Audio Engine**:
    -   **VAD (Voice Activity Detection)**: Escuta passiva inteligente (filtra ruídos).
    -   **STT Local**: Vosk/Whisper para transcrição offline.
    -   **TTS Neural**: Vozes naturais via Edge-TTS.

-   **🛡️ Infrastructure**:
    -   **Self-Healing**: O sistema se conserta em caso de falha de dependências.
    -   **Logs Centralizados**: Rastreamento detalhado em `data/logs`.

---

## 🚀 Funcionalidades

### Interface Visual (HUD)
-   **Overlay Transparente**: Estilo Iron Man, não intrusivo.
-   **Status em Tempo Real**: Cores indicam estado (Verde=Ouvindo, Azul=Pensando).
-   **Interativo**: Clique através dele para usar o PC normalmente.

### Interação Natural
```text
Você: "Jarvis, analise minha tela."
JARVIS: [Captura tela, processa com YOLO/Outlook] "Vejo que você está programando em Python no VS Code."

Você: "Jarvis, modo foco."
JARVIS: [Fecha apps inúteis, ativa música lo-fi, bloqueia notificações]
```

---

## 🛠️ Instalação Manual (Desenvolvedores)

Se preferir não usar o launcher automático:

1.  **Clone o Repositório**
    ```bash
    git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
    cd PROJECT_JARVIS_5.0
    ```

2.  **Instale Dependências**
    ```bash
    # Script de instalação completa
    python scripts/install/total_installer.py
    ```

3.  **Configure API Keys**
    Edite `.env` na raiz:
    ```env
    GOOGLE_API_KEY="sua_chave_gemini"
    ```

4.  **Inicie o Sistema**
    ```bash
    python main.py
    ```

---

## 📂 Estrutura do Projeto

```
PROJECT_JARVIS_5.0/
├── src/
│   ├── core/                  # O Coração do Sistema
│   │   ├── intelligence/      # LLMs, Brain Router, Agentes
│   │   ├── vision/           # YOLO, OCR, Câmera
│   │   ├── audio/            # STT, TTS, VAD
│   │   ├── actions/          # Automação de SO
│   │   └── management/       # Hardware, Logs, Segurança
│   ├── interface/            # PyQt6 HUD & Widgets
│   └── utils/                # Utilitários globais
├── data/                      # Memória Persistente (gitignored)
│   ├── logs/                 # Logs de sessão
│   ├── models/               # Pesos de IA (YOLO, etc)
│   └── memory/               # ChromaDB (Memória de longo prazo)
├── scripts/                   # Ferramentas de Manutenção
└── config/                    # Arquivos YAML de configuração
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia o `docs/technical/developer-guide.md` para padrões de código e arquitetura.

---

## 📜 Licença

MIT License - Sinta-se livre para usar e modificar.
