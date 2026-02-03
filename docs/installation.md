# 📦 Guia de Instalação - Leitor de Tela Inteligente

Este guia fornece instruções detalhadas para instalar e configurar o Leitor de Tela Inteligente no Windows.

## 📋 Pré-requisitos do Sistema

### Requisitos Mínimos
- **Sistema Operacional:** Windows 10 ou superior
- **Processador:** Dual-core 2.5GHz ou superior
- **Memória RAM:** 4GB (8GB recomendado)
- **Espaço em Disco:** 500MB para instalação + espaço para dados
- **Python:** 3.9 ou superior

### Requisitos Recomendados
- **Sistema Operacional:** Windows 11
- **Processador:** Quad-core ou superior
- **Memória RAM:** 8GB ou mais
- **Espaço em Disco:** 2GB ou mais
- **GPU:** Para aceleração de OCR (opcional)

## 🔧 Instalação do Python

### Verificar Python Instalado
```bash
python --version
# ou
python3 --version
```

Se Python não estiver instalado ou for uma versão inferior a 3.9, faça o download em:
https://www.python.org/downloads/

### Durante a Instalação do Python
✅ **Marque a opção:** "Add Python to PATH"
✅ **Selecione:** "Install for all users" (recomendado)
✅ **Marque:** "Install launcher for all users"

## 📥 Instalação do Leitor de Tela

### Método 1: Instalação Automática (Recomendado)

```bash
# 1. Clonar ou baixar o repositório
git clone https://github.com/username/leitor-tela.git
cd leitor-tela

# 2. Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar aplicação
pip install -e .
```

### Método 2: Instalação Manual

```bash
# 1. Baixar e extrair o código fonte

# 2. Instalar dependências básicas
pip install pillow mss pyautogui sqlalchemy customtkinter

# 3. Instalar dependências de OCR
pip install pytesseract easyocr opencv-python

# 4. Instalar dependências de processamento
pip install pandas numpy spacy
```

## 🔍 Instalação de Dependências Opcionais

### Tesseract OCR (Altamente Recomendado)

O Tesseract é o engine OCR principal e fornece melhor qualidade de extração de texto.

```bash
# 1. Baixar instalador do Tesseract
# Acesse: https://github.com/UB-Mannheim/tesseract/wiki

# 2. Durante instalação, selecione:
# - Linguagem: Portuguese
# - Instalar no caminho padrão

# 3. Verificar instalação
tesseract --version
```

### Modelo de Linguagem Portuguesa (spaCy)

Melhora o processamento de linguagem natural em português.

```bash
# Instalar modelo
python -m spacy download pt_core_news_sm

# Verificar instalação
python -c "import spacy; nlp = spacy.load('pt_core_news_sm'); print('Modelo carregado com sucesso!')"
```

### PyTorch com CUDA (GPU)

Para aceleração de OCR com GPU (opcional, requer GPU NVIDIA).

```bash
# Instalar PyTorch com CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verificar instalação
python -c "import torch; print('CUDA disponível:', torch.cuda.is_available())"
```

## 🧪 Verificação da Instalação

Execute os testes para verificar se tudo está funcionando:

```bash
# Executar testes básicos
python -m pytest tests/ -v

# Ou testar manualmente
python -c "
from src.utils.config import config
from src.core.ocr_processor import ocr_processor
print('Configuração:', config.get_setting('app.name'))
print('Engines OCR disponíveis:', ocr_processor.get_available_engines())
print('Instalação OK!')
"
```

## 🚀 Primeiro Uso

### Interface Gráfica
```bash
# Executar aplicação
python main.py

# Ou após instalação completa:
leitor-tela
```

### Linha de Comando
```bash
# Testar captura básica
python main.py capture

# Ver ajuda
python main.py --help
```

## ⚙️ Configuração Inicial

### Arquivo de Configurações

Após primeira execução, o arquivo `config/settings.json` será criado. Principais configurações:

```json
{
  "app": {
    "theme": "dark",
    "language": "pt-BR"
  },
  "capture": {
    "hotkey": "ctrl+shift+s",
    "default_format": "PNG",
    "quality": 95
  },
  "ocr": {
    "engine": "tesseract",
    "languages": ["por", "eng"],
    "confidence_threshold": 60
  }
}
```

### Atalhos de Teclado

- **Ctrl+N:** Nova captura
- **Ctrl+O:** Abrir imagem
- **Ctrl+E:** Exportar dados
- **Ctrl+S:** Salvar
- **F5:** Atualizar lista

## 🔧 Solução de Problemas

### Problema: "ModuleNotFoundError"
```
pip install -r requirements.txt
```

### Problema: "Tesseract not found"
```bash
# Instalar Tesseract e verificar PATH
tesseract --version

# Ou especificar caminho manualmente em config/settings.json
"tesseract": {
  "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

### Problema: "CUDA not available"
```bash
# Instalar versão CPU do PyTorch
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Problema: "Permission denied"
```bash
# Executar como administrador ou verificar permissões das pastas
# data/, config/, docs/
```

### Problema: Interface não abre
```bash
# Verificar se todas as dependências de GUI estão instaladas
pip install customtkinter pystray

# Verificar se há erros no console
python main.py 2>&1
```

## 📁 Estrutura de Diretórios Após Instalação

```
LEITOR-TELA/
├── src/                    # Código fonte
├── data/                   # Dados da aplicação (criado automaticamente)
│   ├── captures/          # Screenshots
│   ├── processed/         # Dados processados
│   ├── exports/           # Arquivos exportados
│   └── database.db        # Banco de dados
├── config/                 # Configurações (criado automaticamente)
│   └── settings.json      # Configurações do usuário
├── venv/                   # Ambiente virtual (se criado)
├── __pycache__/           # Cache Python
└── ...                    # Outros arquivos
```

## 🔄 Atualização

Para atualizar para uma nova versão:

```bash
# Parar aplicação se estiver rodando

# Fazer backup de dados importantes
cp config/settings.json config/settings.json.backup
cp data/database.db data/database.db.backup

# Atualizar código
git pull origin main

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Testar
python -m pytest tests/
```

## 🆘 Suporte

Se encontrar problemas durante a instalação:

1. Verifique os logs em `leitor_tela.log`
2. Execute `python main.py --debug` para mais informações
3. Abra uma issue no GitHub com:
   - Versão do Python
   - Sistema operacional
   - Logs de erro completos
   - Passos para reproduzir o problema

## ✅ Verificação Final

Para confirmar que tudo está funcionando:

```bash
# 1. Executar aplicação
python main.py

# 2. Testar captura básica
# Pressione o botão "Capturar Tela"

# 3. Verificar se arquivo foi criado em data/captures/

# 4. Testar processamento
# Selecione a captura e clique em "Processar"

# 5. Verificar dados extraídos na aba "Dados Extraídos"
```

🎉 **Instalação concluída! O Leitor de Tela Inteligente está pronto para uso.**
