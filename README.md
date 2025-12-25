# 🤖 JARVIS 5.0 - Assistente de Voz Inteligente

## 📋 Sobre o Projeto

JARVIS 5.0 é um assistente de voz inteligente desenvolvido em Python que permite interação natural por comandos de voz. O sistema oferece síntese de voz de alta qualidade tanto online quanto offline, com processamento inteligente de linguagem natural.

## ✨ Características Principais

- 🎙️ **Reconhecimento de Voz**: Processamento avançado de comandos por voz
- 🔊 **Síntese de Voz Natural**: Múltiplos engines TTS (Microsoft Edge, Google, engines locais)
- 🧠 **Processamento Inteligente**: Adaptação automática entre modos online/offline
- 🔒 **Segurança**: Comunicação segura com serviços em nuvem
- 🎯 **Modular**: Arquitetura limpa e extensível
- 🌐 **Multilíngue**: Suporte otimizado para português brasileiro

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8+
- Microfone funcional
- Conexão com internet (opcional, para melhor qualidade)

### Instalação Automática
```bash
python scripts/install.py
```

### Instalação Manual
```bash
pip install -r requirements.txt
python main.py
```

## 🎯 Como Usar

### Inicialização Básica
```bash
python main.py
```

### Comandos de Teste
```bash
# Testar reconhecimento de voz
python main.py --test

# Calibrar microfone
python main.py --calibrate

# Modo debug
python main.py --debug
```

### Testes do Sistema
```bash
# Testar voz online (Microsoft Edge TTS)
python tests/test_secure_voice.py

# Testar engines locais
python tests/test_local_voice.py

# Teste completo do sistema
python tests/test_basic.py
```

## 🏗️ Arquitetura

```
jarvis/
├── core/           # Núcleo do sistema
│   ├── assistant.py    # Classe principal
│   ├── config.py       # Gerenciamento de configuração
│   └── logger.py       # Sistema de logging
├── voice/          # Processamento de voz
│   ├── speech_engine.py        # Engine principal de síntese
│   ├── recognition_engine.py   # Reconhecimento de voz
│   ├── secure_cloud_tts.py     # TTS seguro em nuvem
│   ├── enhanced_local_tts.py   # TTS local otimizado
│   ├── smart_natural_speech.py # Processamento inteligente
│   └── natural_speech.py       # Processamento natural
└── commands/       # Processamento de comandos
    ├── command_processor.py    # Processador principal
    ├── system_commands.py      # Comandos do sistema
    └── utility_commands.py     # Comandos utilitários
```

## ⚙️ Configuração

O arquivo `config.json` permite personalizar:

- **Voz**: Velocidade, volume, idioma
- **Reconhecimento**: Timeout, sensibilidade
- **Engines**: Preferências online/offline
- **Segurança**: Domínios confiáveis

## 🔧 Engines de Voz Disponíveis

### Online (Requer Internet)
- **Microsoft Edge TTS** ⭐ (Recomendado)
  - Vozes neurais de alta qualidade
  - Suporte a emoções
  - Processamento rápido

- **Google TTS Free**
  - Boa qualidade
  - Gratuito
  - Backup confiável

### Offline (Local)
- **Coqui TTS**
  - Melhor qualidade offline
  - Modelo específico para português
  - Processamento local

- **eSpeak-NG**
  - Leve e rápido
  - Sempre disponível
  - Boa compatibilidade

## 🛠️ Desenvolvimento

### Estrutura de Testes
```bash
tests/
├── test_basic.py           # Testes fundamentais
├── test_secure_voice.py    # Testes de TTS online
├── test_local_voice.py     # Testes de TTS offline
└── test_enhanced_voice.py  # Testes do sistema completo
```

### Executar Testes
```bash
# Todos os testes
python -m pytest tests/

# Teste específico
python tests/test_basic.py
```

## 📚 Documentação

- [Arquitetura Detalhada](docs/ARCHITECTURE.md)
- [Referência da API](docs/API.md)
- [Exemplos de Uso](examples/)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique a documentação
2. Execute os testes de diagnóstico
3. Consulte os logs em `.cursor/debug.log`
4. Abra uma issue no GitHub

## 🎯 Roadmap

- [ ] Interface gráfica
- [ ] Plugins personalizados
- [ ] Integração com APIs externas
- [ ] Suporte a múltiplos idiomas
- [ ] Modo servidor/cliente

---

**JARVIS 5.0** - Desenvolvido com ❤️ para interação natural por voz