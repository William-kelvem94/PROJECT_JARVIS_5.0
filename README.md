# 🤖 JARVIS Ultimate - Infraestrutura de Vida Artificial

<div align="center">

![JARVIS](https://img.shields.io/badge/JARVIS-Ultimate-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Integrated-green?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-Enabled-purple?style=for-the-badge)

**Assistente de IA com Aprendizado Contínuo e Controle Total do Sistema**

[🚀 Início Rápido](#-início-rápido) • [📖 Documentação](#-documentação) • [🎯 Recursos](#-recursos)

</div>

---

## ✨ O que é o JARVIS Ultimate?

O JARVIS Ultimate é uma **infraestrutura de vida artificial** completa que vai além de um simples assistente. Ele:

- 🔄 **Aprende continuamente** com suas interações
- 🎤 **Fala e ouve** naturalmente
- 💻 **Controla seu hardware** automaticamente
- 🧠 **Memória inteligente** com RAG
- 📱 **Agnóstico ao hardware** (funciona no Galaxy Book2 ou Desktop parrudo)
- 🐳 **Roda em Docker** ou nativo

### 🏗️ Arquitetura Híbrida

```
JARVIS Ultimate/
├── core/               # Cérebro e sensores
│   ├── brain.py       # IA com RAG integrado
│   ├── hearing.py     # Reconhecimento de voz
│   ├── speech.py      # Síntese de voz
│   └── hardware.py    # Monitoramento inteligente
├── tools/             # Ferramentas avançadas
│   └── model_manager.py # Gestão de modelos IA
├── data/              # Memória persistente
├── config.py          # Configuração inteligente
└── main.py           # Orquestrador principal
```

---

## 🚀 Início Rápido

### Pré-requisitos

1. **Python 3.11+**
2. **Ollama** (instale em: https://ollama.com)
3. **Microfone** (para modo voz)

### Instalação Simples

```bash
# 1. Baixar modelos essenciais
ollama pull codellama:7b
ollama pull mistral:7b

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar
python main.py
```

### 🎤 Modo Voz (Completo)

```bash
# Para experiência completa com voz
pip install openai-whisper sounddevice

# Executar
python main.py
```

### 🐳 Docker (Isolado)

```bash
# Com Ollama integrado
docker-compose -f docker/docker-compose.yml --profile with-ollama up -d

# Acessar
docker-compose logs -f jarvis-ultimate
```

---

## 🎯 Recursos Principais

### 🧠 Cérebro com RAG
- **Memória Vetorial**: Aprende instantaneamente
- **Contexto Inteligente**: Recupera informações relevantes
- **Personalização**: Adapta-se ao seu perfil

### 🎤 Sistema de Voz Avançado
- **Múltiplas Engines**: pyttsx3, Edge-TTS, ElevenLabs
- **Reconhecimento**: SpeechRecognition, Whisper, Vosk
- **Wake Word**: Ativa com "Jarvis"

### 💻 Controle de Hardware
- **Detecção Automática**: Galaxy Book2 vs Desktop
- **Monitoramento**: CPU, RAM, temperatura, bateria
- **Otimização**: Ajustes específicos por hardware

### 🤖 Gestão de Modelos
- **Busca no HF**: Modelos compatíveis com Ollama
- **Download Automático**: `ollama pull` integrado
- **Recomendações**: Sugestões inteligentes

---

## 💬 Como Usar

### Modo Voz
1. Execute `python main.py`
2. Diga **"Jarvis"** para ativar
3. Converse naturalmente

### Comandos Especiais
```
"Aprenda que [frase]"    - Ensina algo novo
"Status"                 - Mostra estado do sistema
"Calibrar microfone"     - Ajusta áudio
"Sair"                   - Encerra
```

### Exemplo de Conversa
```
Você: Jarvis, aprenda que eu gosto de volume em 20%
JARVIS: ✅ Aprendido!

Você: Qual volume eu gosto?
JARVIS: Baseado no que você me ensinou, você prefere volume em 20%
```

---

## ⚙️ Configuração Avançada

### `config.json`
```json
{
  "user": {
    "name": "William",
    "preferences": {
      "volume_preference": 20,
      "desktop_water_cooling": true
    }
  },
  "voice": {
    "stt_engine": "whisper",
    "tts_engine": "pyttsx3",
    "language": "pt-BR"
  },
  "learning": {
    "rag_enabled": true,
    "auto_learn_from_interactions": true
  }
}
```

### Variáveis de Ambiente
```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export HUGGINGFACE_TOKEN="seu_token_aqui"  # Opcional
```

---

## 🐳 Docker Avançado

### Perfis Disponíveis
```bash
# Básico
docker-compose up -d

# Com Ollama integrado
docker-compose --profile with-ollama up -d

# Com Redis e ChromaDB
docker-compose --profile with-redis --profile with-chromadb up -d
```

### Acesso ao Host
Para controle completo do hardware via Docker:
```yaml
# docker-compose.yml
services:
  jarvis-ultimate:
    network_mode: host  # Acesso direto ao host
    privileged: true    # Acesso a dispositivos
```

---

## 🔧 Desenvolvimento

### Estrutura do Código
- **`main.py`**: Loop principal e orquestração
- **`core/brain.py`**: Sistema RAG e aprendizado
- **`core/hardware.py`**: Monitoramento de hardware
- **`tools/model_manager.py`**: Gestão de modelos

### Adicionar Novos Recursos
```python
# Exemplo: Novo sensor
from core.hardware import HardwareMonitor

class MeuSensor:
    def __init__(self, hardware_monitor):
        self.hardware = hardware_monitor

    def ler_dado(self):
        # Implementação do sensor
        pass
```

---

## 📊 Monitoramento

### Status em Tempo Real
```bash
curl http://localhost:8000/api/status
```

### Logs
```bash
# Ver logs
docker-compose logs -f jarvis-ultimate

# Logs detalhados
tail -f logs/jarvis.log
```

---

## 🐛 Troubleshooting

### Voz não funciona
```bash
# Instalar dependências de áudio
sudo apt-get install alsa-utils pulseaudio

# Testar microfone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

### Ollama não conecta
```bash
# Verificar se está rodando
curl http://localhost:11434/api/tags

# Reiniciar
ollama serve
```

### Docker sem acesso ao host
```bash
# Para controle de hardware no Docker
echo "network_mode: host" >> docker-compose.yml
docker-compose down && docker-compose up -d
```

---

## 📈 Performance

### Otimizações por Hardware

**Galaxy Book2 (Notebook):**
- ✅ Monitoramento de bateria
- ✅ Calibração automática de microfone
- ✅ Modo economia de energia

**Desktop Parrudo:**
- ✅ Monitoramento de GPU
- ✅ Controle de water cooler
- ✅ Processamento paralelo

### Benchmark
- **Inicialização**: < 5 segundos
- **Resposta RAG**: < 500ms
- **Reconhecimento de voz**: < 2 segundos
- **Síntese de voz**: < 1 segundo

---

## 🤝 Contribuições

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit (`git commit -am 'Adiciona nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Áreas de Interesse
- 🤖 Novos modelos de IA
- 🎤 Melhorias na síntese de voz
- 💻 Suporte a novos hardwares
- 🧠 Algoritmos de aprendizado avançados

---

## 📄 Licença

Este projeto é open-source e gratuito para uso pessoal e comercial.

---

## 🙏 Agradecimentos

- **Ollama** - Por tornar IA local acessível
- **HuggingFace** - Por modelos open-source
- **ChromaDB** - Por RAG eficiente
- **Comunidade Open Source** - Por todas as ferramentas

---

<div align="center">

**Desenvolvido com ❤️ para criar vida artificial**

⭐ **Dê uma estrela se gostou!**

</div>