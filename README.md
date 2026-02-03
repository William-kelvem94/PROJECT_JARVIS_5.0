# JARVIS 5.0 - Inteligência Artificial de Elite

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-stable-green.svg)]()

O núcleo do **Jarvis 5.0**, integrando um sistema avançado para **captura**, **processamento** e **análise inteligente** de dados da tela. Esta é a base para a "Visão Computacional" do Jarvis.

O **Jarvis 5.0** é um assistente virtual autônomo projetado para Windows que integra:
- 👁️ **Visão Computacional**: Reconhecimento facial (FaceID) e detecção de gestos (Hand Landmarks).
- 👂 **Audição Inteligente**: Wake Word "Jarvis" e processamento de fala offline/online.
- 🧠 **Cérebro Evolutivo**: Memória neural semântica e aprendizado por feedback ("Ensinar Modo").
- 🤖 **Agente de Ação**: Controle real de mouse/teclado para automação de tarefas.

**Ideal para:** extrair dados de sistemas legados, aplicações web que bloqueiam APIs, documentos digitalizados, formulários e qualquer conteúdo visual.

## ✨ **Características Principais**

### 📸 **Captura Avançada**
- ✅ Captura de tela completa
- ✅ Seleção de áreas específicas
- ✅ Captura de janelas individuais
- ✅ Gravação de tela com compressão
- ✅ Captura por timer automático
- ✅ Atalhos de teclado globais

### 🔍 **OCR Inteligente**
- ✅ Suporte multilíngue (Português, Inglês, +)
- ✅ Engines híbridos (Tesseract + EasyOCR)
- ✅ Pré-processamento automático de imagens
- ✅ Correção inteligente de erros
- ✅ Detecção de regiões de texto

### 🧠 **Análise Inteligente**
- ✅ Extração automática de dados estruturados
- ✅ Reconhecimento de documentos (NF, faturas, contratos)
- ✅ Identificação de entidades (CPF, CNPJ, emails, valores)
- ✅ Categorização automática por tipo
- ✅ Análise de sentimento (opcional)

### 📊 **Organização e Exportação**
- ✅ Múltiplos formatos de saída
- ✅ Organização automática por pastas
- ✅ Sistema de tags e metadados
- ✅ Histórico completo de operações
- ✅ API REST local para integrações

### 🖥️ **Interface Moderna**
- ✅ Interface gráfica intuitiva (CustomTkinter)
- ✅ Ícone na bandeja do sistema
- ✅ Modo escuro/claro
- ✅ Notificações inteligentes
- ✅ Configurações avançadas

## 🚀 **Instalação**

### 🎯 **INÍCIO PROFISSIONAL**

**Windows:**
```bash
# Clique duplo no arquivo:
LeitorTela.bat
# OU execute no terminal:
.\LeitorTela.bat
```

**Linux/Mac:**
```bash
# Execute o launcher:
python3 launcher.py
```

**O launcher inteligente irá:**
- ✅ Detectar automaticamente seu sistema
- ✅ Verificar se Python está instalado
- ✅ Instalar todas as dependências necessárias
- ✅ Oferecer menu interativo profissional
- ✅ Executar a aplicação automaticamente

---

### 📋 **Instalação Profissional**

#### Sistema Operacional
- **Windows 10/11** (primário)
- **Linux/macOS** (suportado)

#### Pré-requisitos Técnicos
- **Python 3.9+**
- **4GB RAM** (8GB recomendado)
- **500MB espaço em disco**

#### Instalação Completa
```bash
# Sistema de launcher inteligente
python launcher.py

# Ou launcher direto
pip install -r requirements.txt
python main.py
```

### Instalação Manual

```bash
# Instalar Python 3.9+ se necessário
# Baixar de: https://www.python.org/downloads/

# Instalar dependências
pip install -r requirements.txt

# (Opcional) Instalar Tesseract OCR para melhor qualidade
# Windows: https://github.com/UB-Mannheim/tesseract/wiki

# (Opcional) Baixar modelo de linguagem português
python -m spacy download pt_core_news_sm
```

## 🎮 **Como Usar**

### 🚀 **Modo Automático (Mais Fácil)**

**Clique duplo no arquivo:**
```bash
LeitorTela.bat
```

**O sistema detecta e resolve automaticamente:**
- ✅ Verifica se Python está instalado
- ✅ Instala dependências faltantes
- ✅ Executa a aplicação automaticamente

---

### 🎛️ **Modos Avançados**

**Comandos específicos:**
```bash
# Verificar sistema apenas:
LeitorTela.bat check

# Instalar dependências:
LeitorTela.bat install

# Executar aplicação:
LeitorTela.bat run

# Menu interativo completo:
LeitorTela.bat menu
```

**Python direto:**
```bash
# Modo automático inteligente:
python launcher.py

# Comandos específicos:
python launcher.py check      # Verificar sistema
python launcher.py install    # Instalar dependências
python launcher.py run        # Executar aplicação
python launcher.py diagnostic # Diagnóstico completo
```

---

### 💻 **Interface Gráfica Direta**

**Após primeira configuração:**
```bash
python main.py
```

---

### 💻 **Interface Gráfica**

```bash
# Executar interface gráfica
python main.py

# Ou após instalação:
leitor-tela
```

### Linha de Comando

```bash
# Captura de tela completa
python main.py capture

# Captura de área específica
python main.py capture --area 100,100,800,600 --process --analyze --export --format json

# Processar imagem existente
python main.py process --input imagem.png --analyze --export --format pdf

# Análise de texto
python main.py analyze --text "CPF: 123.456.789-00" --export --format csv

# Processamento em lote
python main.py batch --input-dir ./imagens/

# Ver todas as opções
python main.py --help
```

### Exemplos Práticos

#### 1. Extrair dados de uma nota fiscal
```bash
# Capturar tela da NF
python main.py capture --process --analyze --export --format json
```

#### 2. Digitalizar formulários automaticamente
```bash
# Processar lote de formulários
python main.py batch --input-dir ./formularios/
```

#### 3. Monitorar dados em tempo real
```bash
# Captura automática a cada 30 segundos
python main.py capture --timer 30 --process --analyze
```

## 🏗️ **Arquitetura**

```
LEITOR-TELA/
├── src/                    # Código fonte
│   ├── core/              # Módulos principais
│   │   ├── screen_capture.py    # Captura de tela
│   │   ├── ocr_processor.py     # Processamento OCR
│   │   ├── data_analyzer.py     # Análise inteligente
│   │   └── data_organizer.py    # Organização de dados
│   ├── gui/               # Interface gráfica
│   │   └── main_window.py       # Janela principal
│   ├── database/          # Persistência de dados
│   │   └── models.py            # Modelos SQLAlchemy
│   └── utils/             # Utilitários
│       ├── config.py            # Configurações
│       └── helpers.py           # Funções auxiliares
├── data/                  # Dados da aplicação
│   ├── captures/          # Screenshots capturados
│   ├── processed/         # Dados processados
│   ├── exports/           # Arquivos exportados
│   └── database.db        # Banco SQLite
├── config/                # Configurações do usuário
├── docs/                  # Documentação
├── tests/                 # Testes automatizados
├── main.py                # Ponto de entrada
├── setup.py               # Script de instalação
└── requirements.txt       # Dependências
```

## 🧪 **Testes**

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src

# Executar testes específicos
pytest tests/test_config.py

# Executar apenas testes unitários
pytest -m unit
```

## 📚 **Documentação**

### Guia do Usuário
- [Instalação e Configuração](docs/installation.md)
- [Primeiros Passos](docs/getting_started.md)
- [Funcionalidades Avançadas](docs/advanced_features.md)

### Desenvolvimento
- [Arquitetura do Sistema](docs/architecture.md)
- [API de Integração](docs/api.md)
- [Contribuição](docs/contributing.md)

### Referências
- [Padrões de Extração](docs/extraction_patterns.md)
- [Formatos de Saída](docs/output_formats.md)
- [Solução de Problemas](docs/troubleshooting.md)

## 🔧 **Configuração**

O arquivo `config/settings.json` contém todas as configurações:

```json
{
  "app": {
    "name": "Leitor de Tela Inteligente",
    "version": "1.0.0",
    "language": "pt-BR",
    "theme": "dark"
  },
  "capture": {
    "default_format": "PNG",
    "quality": 95,
    "hotkey": "ctrl+shift+s",
    "auto_save": true,
    "capture_delay": 0.5
  },
  "ocr": {
    "engine": "tesseract",
    "languages": ["por", "eng"],
    "confidence_threshold": 60,
    "preprocessing": true
  }
}
```

## 🔌 **APIs e Integrações**

### API REST Local
```bash
# Iniciar servidor API
python -c "from src.api.server import run_server; run_server()"

# Exemplos de uso
curl -X POST http://localhost:8000/capture
curl -X GET http://localhost:8000/exports
```

### Webhooks
Configure webhooks para notificações automáticas quando dados são extraídos.

### Plugins
Sistema extensível para adicionar novos tipos de documento e padrões de extração.

## 🤝 **Contribuição**

Contribuições são bem-vindas! Por favor, leia o [guia de contribuição](docs/contributing.md).

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 **Licença**

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 **Agradecimentos**

- **Tesseract OCR** - Engine OCR principal
- **EasyOCR** - OCR alternativo com IA
- **spaCy** - Processamento de linguagem natural
- **OpenCV** - Processamento de imagens
- **CustomTkinter** - Interface moderna

## 📞 **Suporte**

- 📧 **Email:** contato@exemplo.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/username/leitor-tela/issues)
- 📖 **Documentação:** [Wiki](https://github.com/username/leitor-tela/wiki)
- 💬 **Discussões:** [GitHub Discussions](https://github.com/username/leitor-tela/discussions)

## 🔄 **Roadmap**

### Próximas Funcionalidades
- [ ] Suporte a macOS e Linux
- [ ] Integração com Google Cloud Vision API
- [ ] Reconhecimento de formulários avançado
- [ ] Extração de tabelas complexas
- [ ] Modo offline aprimorado
- [ ] Suporte a mais idiomas
- [ ] Interface web
- [ ] Aplicativo móvel

### Melhorias Planejadas
- [ ] Performance otimizada para GPUs
- [ ] Cache inteligente de resultados
- [ ] Sincronização com nuvem
- [ ] Análise de imagens médicas
- [ ] Reconhecimento de códigos de barras/QR

---

**⭐ Star este repositório se achou útil!**

**📢 Este projeto está em desenvolvimento ativo. Sua contribuição é muito bem-vinda!**
