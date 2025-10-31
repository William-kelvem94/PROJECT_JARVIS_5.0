# 🏗️ Arquitetura Modular do JARVIS v2

Este documento descreve a arquitetura modular completa do JARVIS v2, baseada na visão de um assistente IA local, auto-adaptativo e containerizado.

## 📊 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Módulos de Entrada                        │
├──────────────────────┬──────────────────────────────────────┤
│  Módulo de Voz       │    Módulo de Texto                   │
│  (STT/TTS)           │    (Interface Chat)                  │
│  - Whisper/VOSK      │    - Web/CLI                         │
│  - Coqui/Piper       │                                      │
└──────────┬───────────┴──────────┬───────────────────────────┘
           │                      │
           │ Transcrição/Intenção │
           └──────────┬───────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│          Núcleo de Orquestração                             │
│  - Análise de Intenção                                      │
│  - Sistema de Skills                                        │
│  - Gerenciamento de Contexto                                │
│  - Memória de Curto Prazo                                   │
└──────────┬───────────────────────────────────────────────────┘
           │
           │ Consulta/Contexto
           │
┌──────────▼───────────────────────────────────────────────────┐
│       Servidor de Modelos LLM                                │
│  - Ollama (Local)                                            │
│  - LM Studio / Text Generation WebUI                         │
│  - Compatível com API OpenAI                                 │
└──────────┬───────────────────────────────────────────────────┘
           │
           │ Resposta/Plano de Ação
           │
┌──────────▼───────────────────────────────────────────────────┐
│                    Módulos de Ação                           │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Automação    │ Gerenciador  │ Gerenciador  │ Servidor API   │
│ Desktop      │ de Arquivos  │ de Tarefas   │ (Para IDEs)    │
│ (RPA)        │              │              │                │
│              │              │              │                │
│ - pyautogui  │ - PDF/DOCX   │ - Agenda     │ - FastAPI      │
│ - Controle   │ - Busca      │ - Alarmes    │ - WebSocket    │
│   de Apps    │ - Organizar  │ - Lembretes  │ - REST API     │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

## 🧩 Componentes Principais

### 1. Módulos de Entrada (`modules/input/`)

#### `voice_module.py`
- **Speech-to-Text (STT)**: Reconhecimento de voz
  - Google Speech Recognition (padrão)
  - VOSK (offline, opcional)
  - Whisper (offline, alta qualidade)
- **Text-to-Speech (TTS)**: Síntese de voz
  - pyttsx3 (local, padrão)
  - Coqui TTS (alta qualidade, opcional)
  - Piper (leve, opcional)

#### `text_module.py`
- Interface de chat via texto
- Suporta múltiplos handlers
- Processamento assíncrono

### 2. Módulos de Processamento (`modules/processing/`)

#### `orchestrator.py`
**Núcleo de Orquestração** - Coração do sistema:
- Analisa intenções usando LLM
- Gerencia sistema de Skills (habilidades)
- Mantém memória de curto prazo
- Coordena comunicação entre módulos
- Decisão sobre qual ação executar

**Sistema de Skills:**
- Skills são funções registradas que executam ações específicas
- Cada skill recebe: mensagem, parâmetros extraídos, contexto
- Skills podem ser síncronas ou assíncronas
- Exemplos: `open_app`, `read_file`, `add_task`, etc.

### 3. Módulos de Ação (`modules/action/`)

#### `rpa_module.py`
**Automação Desktop:**
- Abrir/fechar aplicativos
- Controle de mouse e teclado
- Screenshots
- Template matching (busca por imagem)
- Hotkeys

#### `file_manager.py`
**Gerenciador de Arquivos:**
- Leitura de múltiplos formatos (PDF, DOCX, TXT, JSON, etc.)
- Listagem de diretórios
- Organização automática por tipo
- Busca de arquivos

#### `task_manager.py`
**Gerenciador de Tarefas:**
- Agenda de tarefas
- Alarmes
- Lembretes
- Prioridades

### 4. Sistema RAG (`modules/rag/`)

#### `vector_store.py`
**Banco de Dados Vetorial:**
- Armazena documentos e conhecimento
- Busca semântica
- Integração com ChromaDB
- Embeddings com sentence-transformers
- Injeção de contexto no LLM

**Uso:**
```python
# Adicionar conhecimento
jarvis.add_knowledge("Texto importante", {"source": "documento.pdf"})

# Buscar contexto relevante
context = jarvis.vector_store.get_context_for_query("pergunta do usuário")
```

### 5. Módulos de Sistema (`modules/system/`)

#### `capability_detector.py`
**Auto-Detecção de Capacidades:**
- Detecta CPU (cores, frequência)
- Detecta RAM (total, disponível)
- Detecta GPU (NVIDIA CUDA, AMD ROCm)
- Detecta armazenamento disponível
- Calcula score geral do sistema
- Recomenda modelo LLM apropriado

**Exemplo de Saída:**
```
💻 CPU: 8 cores
🧠 RAM: 16.0 GB total, 8.5 GB disponível
🎮 GPU: ✅ CUDA disponível
📈 Score: 80%
🤖 Modelo Recomendado: llama3:70b (GPU disponível e RAM suficiente)
```

## 🔄 Fluxo de Processamento

1. **Entrada**: Usuário envia mensagem (voz ou texto)
2. **Transcrição**: Se voz, converte para texto
3. **Análise de Intenção**: Orquestrador analisa usando LLM
4. **Decisão**: Identifica skill apropriada ou usa LLM para resposta geral
5. **Execução**: Executa skill ou gera resposta do LLM
6. **Resposta**: Retorna resposta (texto ou voz)

### Com RAG:
1. **Busca de Contexto**: Vector Store busca documentos relevantes
2. **Injeção**: Contexto é injetado no prompt do LLM
3. **Geração**: LLM gera resposta com conhecimento personalizado

## 🚀 Inicialização e Uso

### Modo Básico
```python
from core.jarvis_v2 import JarvisV2

jarvis = JarvisV2()

# Processar mensagem
result = await jarvis.process("Abrir Chrome")
print(result["response"])
```

### Com Detecção Automática
```python
jarvis = JarvisV2(auto_detect_capabilities=True)
# Sistema detecta hardware e ajusta modelo automaticamente
```

### Modo Voz
```python
# Escutar e processar
result = jarvis.listen_and_process()
# Resposta será falada automaticamente
```

## 📦 Dependências Principais

- **FastAPI**: Servidor web e API
- **Ollama**: Servidor LLM local
- **ChromaDB**: Banco vetorial
- **sentence-transformers**: Embeddings
- **pyautogui**: Automação desktop
- **PyPDF2**: Leitura de PDFs
- **python-docx**: Leitura de Word

## 🔧 Configuração

### Variáveis de Ambiente
- `OLLAMA_MODEL`: Modelo LLM a usar
- `OLLAMA_BASE_URL`: URL do Ollama (padrão: http://ollama:11434)
- `VOSK_MODEL_PATH`: Caminho do modelo VOSK (opcional)

### Docker Compose
O `docker-compose.yml` já configura:
- Serviço Ollama para modelos LLM
- Serviço JARVIS com toda a arquitetura modular

## 📈 Expansibilidade

### Adicionar Nova Skill

```python
async def minha_skill(message: str, params: Dict, context: Dict):
    # Sua lógica aqui
    return {
        "response": "Resposta",
        "actions": []
    }

jarvis.orchestrator.register_skill("minha_skill", minha_skill)
```

### Adicionar Novo Módulo de Ação

1. Crie classe em `modules/action/`
2. Implemente métodos necessários
3. Registre no `jarvis_v2.py`
4. Crie skill correspondente

## 🎯 Benefícios da Arquitetura Modular

1. **Separação de Responsabilidades**: Cada módulo tem função clara
2. **Fácil Expansão**: Adicionar novas funcionalidades é simples
3. **Testabilidade**: Cada módulo pode ser testado isoladamente
4. **Manutenibilidade**: Código organizado e fácil de entender
5. **Reutilização**: Módulos podem ser usados em outros projetos
6. **Auto-Adaptação**: Sistema se ajusta ao hardware disponível

## 🔮 Melhorias Futuras

- [ ] Suporte a Whisper offline para STT
- [ ] Integração com Coqui TTS para voz natural
- [ ] Suporte a AMD ROCm para GPU
- [ ] Melhor integração com IDEs (extensões)
- [ ] Sistema de memória persistente (longo prazo)
- [ ] Aprendizado contínuo via fine-tuning

## 📚 Referências

- [Ollama](https://ollama.ai/)
- [ChromaDB](https://www.trychroma.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)

