# 🚀 Guia Rápido - JARVIS v2

## Início Rápido

### 1. Usando a Versão Modular (Recomendado)

A nova arquitetura modular está em `core/main_v2.py`. Para usar:

```bash
# Via Docker (recomendado)
docker-compose up

# Ou diretamente
python -m uvicorn core.main_v2:app --host 0.0.0.0 --port 8000
```

### 2. API Endpoints

#### Status do Sistema
```bash
GET http://localhost:8000/api/status
```

Retorna:
- Status dos módulos
- Capacidades detectadas
- Modelo LLM atual
- Estatísticas do RAG

#### Chat
```bash
POST http://localhost:8000/api/chat
Content-Type: application/json

{
  "message": "Abrir Chrome"
}
```

#### Adicionar Conhecimento ao RAG
```bash
POST http://localhost:8000/api/knowledge
Content-Type: application/json

{
  "text": "JARVIS é um assistente inteligente que ajuda com tarefas do dia a dia.",
  "metadata": {
    "source": "documento.pdf",
    "category": "geral"
  }
}
```

#### Buscar no RAG
```bash
GET http://localhost:8000/api/knowledge/search?query=assistente&n_results=5
```

#### Capacidades do Sistema
```bash
GET http://localhost:8000/api/capabilities
```

### 3. WebSocket para Chat em Tempo Real

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
};

ws.send(JSON.stringify({
  content: "Olá JARVIS!",
  type: "text"
}));
```

## 🎯 Skills Disponíveis

O sistema já vem com várias skills pré-configuradas:

1. **`open_app`** - Abrir aplicativos
   - "Abrir Chrome"
   - "Abrir aplicativo Photoshop"

2. **`read_file`** - Ler arquivos
   - "Ler arquivo documento.txt"
   - "Mostrar conteúdo de relatorio.pdf"

3. **`list_files`** - Listar arquivos
   - "Listar arquivos"
   - "Mostrar arquivos em C:/Users"

4. **`organize_files`** - Organizar arquivos
   - "Organizar arquivos"
   - "Organizar arquivos em Downloads"

5. **`add_task`** - Adicionar tarefa
   - "Adicionar tarefa: Revisar código"
   - "Criar tarefa importante para amanhã"

6. **`list_tasks`** - Listar tarefas
   - "Mostrar minhas tarefas"
   - "Listar tarefas pendentes"

7. **`set_alarm`** - Definir alarme
   - "Alarme às 15:00"
   - "Lembrar de chamar às 10:30"

## 📝 Adicionar Nova Skill

```python
# Em core/jarvis_v2.py, método _register_skills()

async def minha_nova_skill(message: str, params: Dict[str, Any], context: Optional[Dict] = None):
    # Sua lógica aqui
    resultado = fazer_algo(params)
    
    return {
        "response": f"Resultado: {resultado}",
        "actions": [{"success": True, "result": resultado}]
    }

jarvis.orchestrator.register_skill("minha_skill", minha_nova_skill)
```

## 🧠 Uso do RAG (Sistema de Conhecimento)

### Adicionar Documentos

```python
from core.jarvis_v2 import JarvisV2

jarvis = JarvisV2()

# Adicionar conhecimento
jarvis.add_knowledge(
    "Python é uma linguagem de programação de alto nível.",
    {"source": "curso_python.pdf", "topico": "introducao"}
)
```

### Buscar Contexto

O sistema automaticamente busca contexto relevante quando você faz perguntas. Mas você pode buscar manualmente:

```python
# Buscar documentos relevantes
resultados = jarvis.vector_store.search("Python", n_results=3)

# Obter contexto formatado para LLM
contexto = jarvis.vector_store.get_context_for_query("Como usar Python?")
```

## 🎙️ Usando Voz

```python
from core.jarvis_v2 import JarvisV2

jarvis = JarvisV2()

# Escutar e processar (resposta será falada automaticamente)
resultado = jarvis.listen_and_process()

if resultado:
    print(f"Você disse: {resultado.get('response')}")
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Modelo LLM
OLLAMA_MODEL=llama3:8b

# URL do Ollama
OLLAMA_BASE_URL=http://ollama:11434

# Caminho do modelo VOSK (opcional)
VOSK_MODEL_PATH=/path/to/vosk/model
```

### Detecção Automática de Capacidades

O sistema detecta automaticamente:
- CPU (cores, frequência)
- RAM (total, disponível)
- GPU (NVIDIA CUDA, AMD ROCm)
- Armazenamento

E recomenda o modelo LLM apropriado.

### Desabilitar Detecção Automática

```python
jarvis = JarvisV2(auto_detect_capabilities=False)
```

## 📦 Dependências Opcionais

Algumas funcionalidades requerem dependências opcionais:

```bash
# VOSK (melhor STT offline)
pip install vosk

# PyTorch com CUDA (para GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# GPUtil (detecção de GPU NVIDIA)
pip install gputil
```

## 🐛 Troubleshooting

### Módulo de Voz não funciona
- Verifique se o microfone está conectado
- No Windows, pode precisar instalar `pyaudio`: `pip install pyaudio`
- Para melhor STT offline, use VOSK

### RPA não funciona
- Verifique se `pyautogui` está instalado: `pip install pyautogui`
- No Linux, pode precisar instalar dependências: `sudo apt-get install python3-tk python3-dev`

### ChromaDB não funciona
- Instale: `pip install chromadb`
- Pode ser necessário instalar dependências adicionais para sentence-transformers

### GPU não detectada
- Instale PyTorch com CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu118`
- Verifique se drivers NVIDIA estão instalados

## 📚 Próximos Passos

1. Leia `ARCHITETURA.md` para entender a estrutura completa
2. Explore os módulos em `modules/`
3. Crie suas próprias skills
4. Adicione conhecimento ao RAG para personalizar o assistente

## 🤝 Contribuindo

Para adicionar novas funcionalidades:
1. Crie módulo em `modules/action/` ou `modules/input/`
2. Registre skill no `jarvis_v2.py`
3. Teste e documente

