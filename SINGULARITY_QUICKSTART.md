# 🚀 JARVIS SINGULARITY - GUIA DE INÍCIO RÁPIDO

## 📋 Índice
1. [Instalação](#instalação)
2. [Configuração](#configuração)
3. [Uso Básico](#uso-básico)
4. [Módulos Principais](#módulos-principais)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 Instalação

### Pré-requisitos
- Python 3.10+
- Windows 10/11
- 4GB RAM (8GB recomendado)
- 10GB espaço em disco

### Instalação Automática

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0
cd PROJECT_JARVIS_5.0

# 2. Execute o setup
python setup_singularity.py
```

O setup irá:
- ✅ Verificar Python 3.10+
- ✅ Instalar dependências
- ✅ Verificar Rclone
- ✅ Executar migração de estrutura
- ✅ Criar configuração

### Instalação Manual

```bash
# 1. Instalar dependências
pip install -r requirements_singularity.txt

# 2. Executar migração
python migrate_structure.py

# 3. Configurar APIs (editar config.yaml)
```

---

## ⚙️ Configuração

### 1. APIs Gratuitas

Edite `config.yaml`:

```yaml
brain:
  groq_api_key: "sua_chave_aqui"  # https://console.groq.com
  gemini_api_key: "sua_chave_aqui"  # https://makersuite.google.com
```

### 2. Rclone (Opcional - para Hive Mind)

```bash
# Instalar Rclone
# Windows: choco install rclone
# Ou: https://rclone.org/downloads/

# Configurar Google Drive
rclone config
# Escolha: Google Drive
# Nome: gdrive
```

### 3. Configurar Dispositivo

```yaml
device_id: "desktop_main"  # ou "notebook", "pc_trabalho", etc
```

---

## 🚀 Uso Básico

### Iniciar JARVIS

```bash
# Opção 1: Direto
python main_singularity.py

# Opção 2: Com watchdog (auto-restart)
watchdog_launcher.bat
```

### Testar Módulos

**UI Automation**:
```python
from jarvis_core.senses import neural_touch

# Clicar em botão (sem coordenadas!)
neural_touch.click_element("Spotify", "Play", "button")

# Digitar texto
neural_touch.type_text("Notepad", "Text Editor", "Hello JARVIS!")
```

**Neural Router**:
```python
from jarvis_core.brain import get_router
import asyncio

router = get_router(
    groq_key="sua_chave",
    gemini_key="sua_chave"
)

response = await router.process("Explique física quântica")
print(response)
```

**TTS**:
```python
from jarvis_core.mouth import get_tts
import asyncio

tts = get_tts()
await tts.speak("Olá, senhor! Sistema operacional.")
```

**Hive Mind**:
```python
from jarvis_core.hive_mind import hybrid_memory

# Armazenar memória
hybrid_memory.store_short_term("user", "Lembre-se: reunião às 15h")

# Buscar memória
results = hybrid_memory.search_memory("reunião")
print(results)
```

---

## 📦 Módulos Principais

### 🌐 Hive Mind - Consciência Distribuída

**Sync com Google Drive**:
```python
from jarvis_core.hive_mind import rclone_sync

# Sync no startup
await rclone_sync.startup_sync()

# Sync periódico
await rclone_sync.heartbeat_sync()

# Sync no shutdown
await rclone_sync.shutdown_sync()
```

**Lockfile (evita conflitos)**:
```python
from jarvis_core.hive_mind import LockfileManager

lock = LockfileManager("desktop_main")
await lock.acquire_lock()  # Adquire controle
# ... usar JARVIS ...
await lock.release_lock()  # Libera
```

---

### 👁️ Senses - Visão e Controle

**UI Automation**:
```python
from jarvis_core.senses import neural_touch

# Encontrar janela
window = neural_touch.find_window("Chrome")

# Clicar em elemento
neural_touch.click_element("Chrome", "New Tab", "button")

# Esperar elemento aparecer
neural_touch.wait_for_element("VSCode", "Run", timeout=10)
```

**Vision Hybrid**:
```python
from jarvis_core.senses.vision_hybrid import vision_system

# Análise automática
result = vision_system.analyze("screenshot.png", level="auto")

# Nível rápido (< 100ms)
result = vision_system.analyze("screenshot.png", level="fast")

# Nível profundo (Gemini Vision)
result = vision_system.analyze("screenshot.png", level="deep")
```

---

### 🧠 Brain - Cérebro Híbrido

**Router Inteligente**:
```python
from jarvis_core.brain import get_router

router = get_router(groq_key="...", gemini_key="...")

# Conversa simples → Groq (rápido)
response = await router.process("Olá!")

# Análise profunda → Gemini Pro
response = await router.process("Analise este código: ...")

# Com imagem → Gemini Vision
response = await router.process(
    "O que há nesta imagem?",
    context={"has_image": True, "image_path": "foto.jpg"}
)
```

---

### 🗣️ Mouth - Comunicação

**TTS com Interrupção**:
```python
from jarvis_core.mouth import get_tts, BargeIn

tts = get_tts(engine="edge", voice="pt-BR-FranciscaNeural")

# Falar com possibilidade de interrupção
barge_in = BargeIn(tts)
await barge_in.speak_with_interrupt("Texto longo aqui...")
# Se usuário falar, para automaticamente!
```

---

### 🏠 World - IoT Reverso

**Integração Alexa**:
```python
from jarvis_core.world import alexa_bridge

# Registrar dispositivo
def party_mode():
    print("🎉 FESTA!")
    # spotify.play()
    # lights.rainbow()

alexa_bridge.register_device("Protocolo Festa", party_mode)
alexa_bridge.start_server()

# Agora diga: "Alexa, liga Protocolo Festa"
```

---

### 🛡️ Guardian - Auto-Preservação

**Privacy Filter**:
```python
from jarvis_core.guardian import privacy_filter

text = "Meu CPF é 123.456.789-00 e email teste@example.com"
filtered, types = privacy_filter.filter_text(text)

print(filtered)  # [CPF_REDACTED] e [EMAIL_REDACTED]
print(types)     # ['cpf', 'email']
```

**Watchdog**:
```python
from jarvis_core.guardian import system_watchdog

# Verificar saúde
health = system_watchdog.get_system_health()
print(f"CPU: {health['cpu_percent']}%")
print(f"RAM: {health['memory_percent']}%")
```

---

## 🐛 Troubleshooting

### Erro: "Rclone não encontrado"
```bash
# Windows
choco install rclone

# Ou baixe: https://rclone.org/downloads/
```

### Erro: "ChromaDB não instalado"
```bash
pip install chromadb sentence-transformers
```

### Erro: "PyQt6 não disponível"
```bash
pip install PyQt6 PyQt6-WebEngine
```

### Erro: "UI Automation não funciona"
```bash
# Instalar uiautomation
pip install uiautomation

# Windows: Pode precisar de permissões de administrador
```

### JARVIS não inicia
```bash
# Verificar logs
cat jarvis_singularity.log

# Modo seguro (sem GUI/voz)
python main_singularity.py --safe-mode
```

---

## 📚 Documentação Adicional

- [Roadmap Completo](docs/singularity_roadmap.md)
- [Walkthrough de Implementação](docs/singularity_walkthrough.md)
- [Arquitetura Técnica](docs/singularity_plan.md)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- OpenAI (Whisper)
- Google (Gemini)
- Groq (Llama 3)
- Microsoft (Edge-TTS)
- Comunidade Open Source

---

**JARVIS Singularity** - *Just A Rather Very Intelligent System*  
Desenvolvido com ❤️ para o futuro da IA assistiva
