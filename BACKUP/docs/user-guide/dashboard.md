# 🎛️ JARVIS 5.0 - Control Dashboard

**Guia Completo do Painel de Controle**

---

## 📖 Visão Geral

O **Control Dashboard** é a interface gráfica completa do JARVIS, oferecendo:
- 🧠 Monitoramento de IA
- 🎤 Configuração de voz
- 👁️ Controle de visão
- 🎓 Sistema de aprendizado
- 📊 Logs e telemetria
- ⚙️ Configurações de sistema

---

## 🚀 Acesso ao Dashboard

### Método 1: Via HUD Overlay

1. JARVIS inicia com HUD transparente
2. Clique em **"Switch to Dashboard"**
3. Dashboard abre em nova janela

### Método 2: Direto no Launcher

1. Execute `START_JARVIS.bat`
2. Aguarde mensagem: `✅ SINGULARITY CORE ENGAGED`
3. Dashboard abre automaticamente

### Método 3: Via Comando

```python
python -m src.interface.control_dashboard
```

---

## 📑 Tabs do Dashboard

### 1. 🧠 Brain (Cérebro da IA)

**Informações Exibidas:**
- Modelo ativo atual
- Provider (Gemini, OpenAI, Ollama, Local)
- Status: 🟢 ONLINE / 🔴 OFFLINE / 🟡 STANDBY
- Última interação
- Total de interações

**Controles:**
- **Switch Model:** Dropdown com modelos disponíveis
- **Test Brain:** Envia prompt de teste
- **Clear Context:** Limpa histórico de conversa
- **Brain Stats:** Estatísticas detalhadas

**Métricas:**
```
Prompt Tokens: 1,234
Response Tokens: 567
Avg. Response Time: 1.2s
Success Rate: 98.5%
```

---

### 2. 🎤 Voice (Controle de Voz)

**Seções:**

#### 🎙️ STT (Speech-to-Text)

- **Model:** faster-whisper, whisper-large, vosk
- **Language:** pt, en, es
- **VAD Enabled:** ✅ / ❌
- **Microphone:** Dropdown com devices
- **Test Recording:** Botão para testar mic

#### 🔊 TTS (Text-to-Speech)

- **Engine:** pyttsx3, elevenlabs, azure
- **Voice:** pt-BR male/female
- **Rate:** 100-200 (velocidade)
- **Volume:** 0.0-1.0

#### 🎚️ Audio Levels

Barras visuais:
- Input Level (microfone)
- Output Level (speaker)
- Noise Floor (ruído de fundo)

**Botões:**
- **Save Voice Config**
- **Reset to Default**
- **Test Voice:** "Olá senhor, sistemas operacionais"

---

### 3. 👁️ Vision (Sistema de Visão)

**Seções:**

#### 📷 Camera Control

- **Device:** Dropdown com câmeras
- **Resolution:** 480p, 720p, 1080p
- **FPS:** 15, 30, 60
- **📸 Live Preview:** Feed da câmera

#### 🎭 FaceID Management

- **Enable FaceID:** ✅ / ❌
- **Confidence Threshold:** Slider 0.85-0.99
- **Registered Faces:** Lista com opção de delete
- **📷 Capture New Face:** Botão

#### 🤖 YOLO Detection

- **Model:** nano, small, medium, large
- **Confidence:** Slider 0.3-0.9
- **Classes Filter:** Checkboxes (person, car, etc.)
- **Show Bounding Boxes:** ✅ / ❌

---

### 4. 🎓 Learning (Sistema de Aprendizado)

Esta é a **TAB MAIS IMPORTANTE** para IA autônoma!

**Seções:**

#### 📊 System Status

```
✅ ONLINE - 4/4 systems active
✅ Feedback Loop
✅ Continual Learner
✅ Knowledge Distiller
✅ Dream Cycle
```

Botão: **🔄 Refresh Status**

#### 😊 Feedback Controls

Após interação com JARVIS:

- **👍 Good Response:** Registra resposta positiva
- **👎 Bad Response:** Registra resposta negativa
- **Correction Field:** Texto para corrigir erro
- **Submit Correction:** Envia feedback corretivo

#### 📈 Learning Metrics

```
Total Feedbacks: 234
Positive: 198 (84.6%)
Negative: 36 (15.4%)
Golden Commands: 12
Training Epochs: 3
```

#### 🚀 Training Controls

- **🎯 Start Training Now:** Força treinamento manual
- **⏸️ Pause Learning:** Pausa sistemas
- **🔄 Resume Learning:** Retoma
- **💾 Backup Model:** Salva checkpoint

#### 🌙 Dream Cycle Status

```
Status: 🌙 SLEEPING (22:35)
Next Wake: 06:00
Accumulated Feedback: 47
Scheduled Training: ✅ Enabled
```

---

### 5. 📜 Logs (Registros)

**Tipos de Log:**

#### 🔵 System Logs (Azul)

```
[2026-02-10 14:32:10] [INFO] JARVIS started successfully
[2026-02-10 14:32:15] [INFO] Brain initialized: gemini-2.0-flash-exp
[2026-02-10 14:32:20] [INFO] Voice engine ready
```

#### 🟢 AI Logs (Verde)

```
[2026-02-10 14:35:00] [AI] User: "Olá JARVIS"
[2026-02-10 14:35:01] [AI] Assistant: "Sim, senhor. Como posso ajudar?"
[2026-02-10 14:36:10] [AI] Brain switched: gemini → ollama-local
```

#### 🟡 Learning Logs (Amarelo)

```
[2026-02-10 15:00:00] [LEARNING] New feedback: POSITIVE
[2026-02-10 15:30:00] [LEARNING] Feedback threshold reached (100)
[2026-02-10 15:30:05] [LEARNING] Starting training session...
[2026-02-10 15:45:00] [LEARNING] Training complete. Loss: 0.023
```

#### 🔴 Error Logs (Vermelho)

```
[2026-02-10 16:00:00] [ERROR] Camera device not found
[2026-02-10 16:01:00] [ERROR] API rate limit exceeded (Gemini)
[2026-02-10 16:02:00] [ERROR] Model file missing: yolov8n.pt
```

**Controles:**
- **Filter by Level:** Dropdown (INFO, WARNING, ERROR, ALL)
- **Search:** Campo de busca
- **📋 Copy Logs:** Copia para clipboard
- **💾 Export Logs:** Salva em `.txt`
- **🗑️ Clear Logs:** Limpa interface (não deleta arquivo)

---

### 6. ⚙️ System (Informações de Sistema)

**Seções:**

#### 💻 Hardware Info

```yaml
OS: Windows 11 Pro
CPU: Intel i7-10700K (8 cores, 16 threads)
RAM: 16 GB DDR4
GPU: NVIDIA RTX 3060 (12 GB VRAM)
```

#### 📊 Resource Usage

Gráficos em tempo real:
- CPU: 23% 📈
- RAM: 8.2 GB / 16 GB (51%) 📊
- GPU: 15% 📉
- VRAM: 2.1 GB / 12 GB 💾

#### 🌡️ Temperatures

```
CPU: 45°C 🟢
GPU: 52°C 🟢
Disk: 38°C 🟢
```

#### 📦 JARVIS Info

```
Version: 5.0 Singularity
Python: 3.11.5
Uptime: 2h 34m 12s
PID: 12345
```

**Botões:**
- **🔄 Restart JARVIS:** Reinicia sistema
- **🛑 Shutdown JARVIS:** Encerra completamente
- **🧪 Run Diagnostics:** Testa todos os módulos
- **📋 System Report:** Gera relatório completo

---

## 🎨 Personalização

### Temas (Futuro)

```yaml
# config/ui_config.yaml
theme: "dark"  # dark, light, iron-man
accent_color: "#00A8FF"
font: "Segoe UI"
```

### Posição e Tamanho

Dashboard salva posição automaticamente:
- Última posição restaurada ao abrir
- Tamanho ajustável (mínimo: 800x600)

---

## ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + R` | Refresh Status |
| `Ctrl + L` | Limpar Logs |
| `Ctrl + T` | Test Brain |
| `Ctrl + S` | Save Config |
| `Ctrl + Q` | Quit Dashboard |
| `F5` | Refresh Current Tab |
| `Ctrl + Tab` | Próxima Tab |
| `Ctrl + Shift + Tab` | Tab Anterior |

---

## 🔧 Solução de Problemas

### "Dashboard não abre"

**Soluções:**
1. Verificar logs em `data/logs/jarvis.log`
2. Reinstalar dependências UI:
   ```bash
   pip install PySide6 pyqtgraph
   ```
3. Executar diretamente:
   ```bash
   python -m src.interface.control_dashboard
   ```

### "Tabs congeladas"

**Soluções:**
1. Pressione `F5` para refresh
2. Feche e reabra Dashboard
3. Verifique consumo de RAM (pode estar cheio)

### "Métricas não atualizam"

**Verificar:**
- Refresh automático está ativo?
- Sistema de telemetria está ON?
- Arquivo `data/system_health.json` existe?

---

## 📚 Próximos Passos

- **Aprendizado:** [learning-system.md](../ai-systems/learning-system.md)
- **Automação:** [automation.md](automation.md)
- **Comandos:** [voice-commands.md](voice-commands.md)

---

<div align="center">

**Controle total na ponta dos seus dedos. 🎛️**

</div>
