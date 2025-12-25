# 📁 Estrutura do Projeto JARVIS 5.0

## 🏗️ Visão Geral da Arquitetura

O JARVIS 5.0 segue uma arquitetura modular e profissional, organizada em camadas bem definidas:

```
PROJECT_JARVIS_5.0/
├── 📁 jarvis/                  # Pacote principal do sistema
│   ├── 📁 core/               # Núcleo fundamental
│   ├── 📁 voice/              # Processamento de voz
│   └── 📁 commands/           # Processamento de comandos
├── 📁 tests/                  # Testes automatizados
├── 📁 docs/                   # Documentação técnica
├── 📁 examples/               # Exemplos de uso
├── 📁 scripts/                # Scripts de instalação
├── 📄 main.py                 # Ponto de entrada principal
├── 📄 config.json             # Configurações do sistema
├── 📄 requirements.txt        # Dependências Python
├── 📄 setup.py               # Configuração do pacote
└── 📄 README.md              # Documentação principal
```

## 📦 Detalhamento dos Módulos

### 🔧 jarvis/core/ - Núcleo do Sistema
```
core/
├── __init__.py           # Inicialização do módulo
├── assistant.py          # Classe principal JarvisAssistant
├── config.py            # Gerenciamento de configurações
└── logger.py            # Sistema de logging avançado
```

**Responsabilidades:**
- Inicialização e coordenação geral do sistema
- Gerenciamento de configurações centralizadas
- Sistema de logging estruturado e profissional
- Orquestração entre os diferentes módulos

### 🎙️ jarvis/voice/ - Processamento de Voz
```
voice/
├── __init__.py                 # Inicialização do módulo
├── speech_engine.py           # Engine principal de síntese
├── recognition_engine.py      # Reconhecimento de voz
├── secure_cloud_tts.py        # TTS seguro em nuvem
├── enhanced_local_tts.py      # TTS local otimizado
├── smart_natural_speech.py    # Processamento inteligente
└── natural_speech.py          # Processamento natural básico
```

**Responsabilidades:**
- Síntese de voz com múltiplos engines (Microsoft Edge, Google, Coqui, eSpeak)
- Reconhecimento de voz com calibração automática
- Processamento inteligente de linguagem natural
- Adaptação automática entre modos online/offline
- Segurança em comunicações com serviços em nuvem

### ⚡ jarvis/commands/ - Processamento de Comandos
```
commands/
├── __init__.py              # Inicialização do módulo
├── command_processor.py     # Processador principal
├── system_commands.py       # Comandos do sistema operacional
└── utility_commands.py      # Comandos utilitários
```

**Responsabilidades:**
- Interpretação e execução de comandos de voz
- Interface com o sistema operacional
- Comandos utilitários e de produtividade
- Extensibilidade para novos comandos

### 🧪 tests/ - Testes Automatizados
```
tests/
├── __init__.py              # Inicialização do módulo de testes
├── test_basic.py           # Testes fundamentais do sistema
├── test_secure_voice.py    # Testes de TTS online seguro
├── test_local_voice.py     # Testes de TTS offline
├── test_enhanced_voice.py  # Testes do sistema completo
├── test_voice_debug.py     # Testes de debug avançado
└── test_fixed_voice.py     # Testes de correções específicas
```

**Responsabilidades:**
- Validação de funcionalidades críticas
- Testes de integração entre módulos
- Verificação de qualidade de voz
- Testes de segurança e performance

### 📚 docs/ - Documentação Técnica
```
docs/
├── ARCHITECTURE.md         # Arquitetura detalhada
└── API.md                 # Referência da API
```

### 🎯 examples/ - Exemplos de Uso
```
examples/
├── basic_usage.py         # Uso básico do sistema
└── custom_commands.py     # Comandos personalizados
```

### 🔧 scripts/ - Scripts de Instalação
```
scripts/
├── install.py            # Instalação completa
└── install_simple.py     # Instalação simplificada
```

## 🔄 Fluxo de Execução

### 1. Inicialização (main.py)
```python
main.py → JarvisAssistant() → Inicialização dos módulos
```

### 2. Processamento de Voz
```python
Microfone → RecognitionEngine → CommandProcessor → Resposta → SpeechEngine → Alto-falante
```

### 3. Engines de TTS (Prioridade)
```
1. Microsoft Edge TTS (Online) - Melhor qualidade
2. Google TTS Free (Online) - Backup confiável  
3. Coqui TTS (Local) - Melhor qualidade offline
4. eSpeak-NG (Local) - Fallback sempre disponível
5. pyttsx3 (Local) - Fallback final
```

## ⚙️ Configurações (config.json)

```json
{
  "voice": {
    "rate": 200,
    "volume": 0.9,
    "language": "pt-BR"
  },
  "recognition": {
    "timeout": 5,
    "phrase_limit": 10
  },
  "cloud_voice": {
    "prefer_microsoft": true,
    "prefer_google": true
  },
  "local_voice": {
    "use_local_tts": true
  },
  "natural_speech": {
    "use_fillers": true,
    "use_hesitations": true,
    "use_breathing": true,
    "emotion_detection": true
  }
}
```

## 🛡️ Segurança

### Comunicação Segura
- **HTTPS obrigatório** para todos os serviços em nuvem
- **Verificação SSL** com certificados atualizados
- **Domínios confiáveis** pré-definidos
- **Timeouts** para evitar travamentos
- **Validação de URLs** antes de requisições

### Domínios Confiáveis
- `translate.google.com` (Google TTS)
- `speech.platform.bing.com` (Microsoft Edge TTS)
- `texttospeech.googleapis.com` (Google Cloud TTS)

## 🚀 Performance

### Otimizações Implementadas
- **Cache inteligente** de síntese de voz
- **Processamento assíncrono** para TTS em nuvem
- **Fallback automático** entre engines
- **Adaptação dinâmica** online/offline
- **Compressão de áudio** otimizada

### Métricas de Performance
- **Latência de resposta**: < 2 segundos (online)
- **Qualidade de voz**: Neural TTS (online), Otimizada (offline)
- **Uso de memória**: < 100MB em operação normal
- **CPU**: Otimizado para processamento em tempo real

## 🔧 Manutenção

### Logs do Sistema
- **Localização**: `.cursor/debug.log`
- **Formato**: NDJSON estruturado
- **Níveis**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotação**: Automática por tamanho

### Monitoramento
- Estatísticas de uso por engine
- Métricas de performance em tempo real
- Detecção automática de falhas
- Relatórios de qualidade de voz

## 📈 Extensibilidade

### Adicionando Novos Engines TTS
1. Implementar interface base em `voice/`
2. Registrar no `SpeechEngine`
3. Adicionar configurações em `config.json`
4. Criar testes específicos

### Adicionando Novos Comandos
1. Implementar em `commands/`
2. Registrar no `CommandProcessor`
3. Adicionar documentação
4. Criar testes de validação

---

**Esta estrutura garante:**
- ✅ Modularidade e manutenibilidade
- ✅ Testabilidade completa
- ✅ Segurança robusta
- ✅ Performance otimizada
- ✅ Extensibilidade futura