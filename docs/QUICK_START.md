# 🚀 JARVIS 5.0 - Guia de Início Rápido

## 📋 Pré-requisitos

- Python 3.9 ou superior
- Windows 10/11
- 4GB RAM mínimo
- Conexão com internet (para recursos de nuvem)

## ⚡ Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/PROJECT_JARVIS_5.0.git
cd PROJECT_JARVIS_5.0
```

### 2. Instale as Dependências
```bash
# Dependências básicas
pip install -r requirements.txt

# Dependências avançadas (Evolution)
pip install -r requirements_advanced.txt
```

### 3. Configure as Variáveis de Ambiente
```bash
# Crie um arquivo .env na raiz do projeto
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 4. Execute o JARVIS
```bash
python start_jarvis.py
```

## 🎯 Uso Básico

### Comandos de Voz
Diga "Jarvis" para ativar e depois:
- "Analise esta tela"
- "Leia o que está escrito aqui"
- "Abra o Chrome"
- "Pesquise sobre IA"
- "Tire uma captura de tela"

### Interface Gráfica
1. **Captura**: Clique em "Capturar Tela" ou use `Ctrl+Shift+S`
2. **Análise**: O JARVIS analisa automaticamente
3. **Ações**: Use comandos de voz ou texto
4. **Histórico**: Veja todas as capturas no painel lateral

## 🧠 Recursos Avançados

### Brain Router (Decisão Inteligente)
```python
from src.core.brain_router import brain_router, PrivacyLevel, LatencyRequirement

# Escolher onde processar uma tarefa
choice = brain_router.choose_brain(
    task_complexity=0.7,
    privacy_level=PrivacyLevel.HIGH,
    latency_requirement=LatencyRequirement.LOW
)
# Retorna: "local", "cloud_flash", "cloud_pro", ou "hybrid"
```

### Visão Avançada (3 Níveis)
```python
from src.core.advanced_vision_pipeline import advanced_vision_pipeline

# Análise automática (escolhe nível baseado na complexidade)
result = advanced_vision_pipeline.analyze("screenshot.png", complexity="auto")

# Extrair tabela de imagem
table = advanced_vision_pipeline.extract_table("table.png")
# Retorna: [["Header1", "Header2"], ["Cell1", "Cell2"], ...]

# Analisar documento
doc = advanced_vision_pipeline.analyze_document("invoice.png")
# Retorna: {"document_type": "invoice", "text": "...", "tables": [...]}
```

### Processamento de Voz
```python
from src.core.advanced_speech_processor import advanced_speech_processor

# Transcrever áudio com Whisper
result = advanced_speech_processor.transcribe("audio.wav", language="pt")
print(result["text"])

# Falar texto (TTS)
advanced_speech_processor.speak("Olá, senhor", speed=1.0, async_mode=True)

# Upgrade do modelo Whisper
advanced_speech_processor.upgrade_model("small")  # tiny, base, small, medium, large
```

### Controle do PC
```python
from src.core.advanced_action_controller import advanced_action_controller

# Abrir aplicação
advanced_action_controller.open_application("chrome")

# Digitar texto
advanced_action_controller.type_text("Hello, JARVIS!")

# Executar atalho
advanced_action_controller.hotkey("ctrl", "c")

# Clicar em posição
advanced_action_controller.click(x=500, y=300)

# Gravar macro
advanced_action_controller.record_macro("minha_macro", [
    {"type": "click", "x": 100, "y": 200},
    {"type": "type", "text": "teste"},
    {"type": "key", "key": "enter"}
])

# Executar macro
advanced_action_controller.play_macro("minha_macro")
```

### Workflows
```python
from src.core.workflow_engine import workflow_engine, WorkflowStep

# Criar workflow
wf = workflow_engine.create_workflow(
    name="abrir_vscode",
    description="Abre VSCode e cria novo arquivo"
)

# Adicionar passos
workflow_engine.add_step("abrir_vscode", WorkflowStep(
    type="open_app",
    params={"app_name": "code"},
    description="Abrir VSCode"
))

workflow_engine.add_step("abrir_vscode", WorkflowStep(
    type="wait",
    params={"duration": 2},
    description="Aguardar carregamento"
))

workflow_engine.add_step("abrir_vscode", WorkflowStep(
    type="hotkey",
    params={"keys": ["ctrl", "n"]},
    description="Novo arquivo"
))

# Salvar workflow
workflow_engine.save_workflow("abrir_vscode")

# Executar workflow
workflow_engine.execute_workflow("abrir_vscode")
```

### Segurança
```python
from src.core.security_manager_advanced import security_manager

# Criptografar dados sensíveis
encrypted = security_manager.encrypt_data("senha123")
decrypted = security_manager.decrypt_data(encrypted)

# Ativar modo privado
security_manager.enable_private_mode()
# Efeitos: sem gravação, sem rede, apenas local

# Desativar modo privado
security_manager.disable_private_mode()

# Ver audit log
events = security_manager.get_audit_log(limit=50)
for event in events:
    print(f"{event['timestamp']}: {event['type']} - {event['description']}")

# Verificar status de segurança
status = security_manager.get_security_status()
print(f"Modo privado: {status['private_mode']}")
print(f"Criptografia: {status['encryption_enabled']}")
```

## 🔧 Auto-Reparo

O JARVIS possui sistema de auto-reparo que:
- Instala CMake automaticamente (via Chocolatey/Winget)
- Baixa modelos de IA necessários (Vosk PT-BR)
- Reinstala dependências com problemas

```python
from src.core.maintenance_manager import maintenance_manager

# Executar verificação completa
maintenance_manager.check_and_repair_all()
```

## 🧪 Testes

```bash
# Executar suite de testes completa
python tests/test_evolution_complete.py

# Testar auto-reparo
python tests/test_auto_repair.py
```

## 📊 Monitoramento

### Logs
Os logs são salvos em `logs/jarvis_YYYYMMDD.log`

### Audit Log de Segurança
Todas as ações são registradas em `.jarvis_security/audit.log`

## ⚙️ Configuração Avançada

### Ajustar Modelo Whisper
Edite `src/core/advanced_speech_processor.py`:
```python
self.whisper_model_size = "small"  # tiny, base, small, medium, large
```

### Ajustar Brain Router
Edite `src/core/brain_router.py` para modificar regras de roteamento.

### Adicionar Workflows Personalizados
Crie workflows em `workflows/*.json` ou via código.

## 🆘 Solução de Problemas

### JARVIS não inicia
```bash
# Verificar dependências
python -c "import numpy, cv2, customtkinter; print('OK')"

# Reinstalar dependências
pip install -r requirements_advanced.txt --force-reinstall
```

### CMake não encontrado
```bash
# Executar auto-reparo
python -c "from src.core.maintenance_manager import maintenance_manager; maintenance_manager._check_and_install_cmake()"
```

### Whisper muito lento
```bash
# Usar modelo menor
python -c "from src.core.advanced_speech_processor import advanced_speech_processor; advanced_speech_processor.upgrade_model('tiny')"
```

### Erro de permissão
Execute como administrador ou ajuste permissões em:
```python
from src.core.security_manager_advanced import security_manager
security_manager.permissions["file_write"] = True
```

## 📚 Documentação Completa

- [Implementation Plan](../brain/implementation_plan.md)
- [Walkthrough](../brain/walkthrough.md)
- [Evolution Summary](../brain/evolution_summary.md)
- [Task List](../brain/task.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja LICENSE para detalhes

## 🙏 Agradecimentos

- OpenAI (Whisper)
- Google (Gemini)
- Ultralytics (YOLO)
- JaidedAI (EasyOCR)
- E toda a comunidade open source!

---

**Desenvolvido com ❤️ para o futuro da IA assistiva**
