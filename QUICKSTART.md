# 🚀 JARVIS SINGULARITY - Guia de Início Rápido

## ⚡ Início em 3 Passos

### 1. Instalar Dependências
```bash
python -m pip install PyQt6
```

### 2. Executar JARVIS
```bash
python main_singularity.py
```

OU use o launcher:
```bash
JARVIS.bat
```

### 3. Usar
- **HUD aparece**: Reator pulsante no canto inferior direito
- **Diga "Jarvis"**: Wake word ativa o sistema
- **Dê seu comando**: Sistema processa e responde
- **HUD muda de cor**:
  - 🟢 Verde = Escutando
  - 🔵 Azul = Pensando
  - 🟠 Laranja = Falando
  - 🔴 Vermelho = Erro
  - 🔵 Ciano = Idle

---

## 🎯 O Que Foi Implementado

### ✅ HUD Transparente
- Overlay click-through (você pode clicar através dele)
- Reator pulsante estilo Iron Man
- Animação 60 FPS
- Estados visuais dinâmicos

### ✅ Integração com Código Existente
- **AI Agent** (`src/core/ai_agent.py`) - Cérebro funcional
- **Voice Controller** (`src/core/voice_controller.py`) - Wake word + comandos
- **Camera Controller** (`src/core/camera_controller.py`) - FaceID (opcional)

### ✅ Arquitetura Moderna
- Threading para GUI + Brain separados
- Asyncio para processamento assíncrono
- Callbacks para eventos de voz
- Logging completo

---

## 📁 Estrutura

```
PROJECT_JARVIS_5.0/
├── src/
│   ├── interface/
│   │   ├── hud.py              # HUD transparente ⭐ NOVO
│   │   └── __init__.py
│   ├── core/
│   │   ├── ai_agent.py         # Cérebro (existente)
│   │   ├── voice_controller.py # Voz (existente)
│   │   └── ...
│   └── ...
│
├── main_singularity.py         # Orquestrador ⭐ NOVO
├── JARVIS.bat                  # Launcher
└── config.yaml                 # Configuração
```

---

## 🔧 Configuração (Opcional)

Edite `config.yaml` para adicionar API keys:

```yaml
brain:
  groq_api_key: "gsk_..."      # https://console.groq.com
  gemini_api_key: "AI..."      # https://makersuite.google.com
```

---

## 🐛 Troubleshooting

### "PyQt6 não encontrado"
```bash
python -m pip install PyQt6
```

### "Voice Controller não disponível"
Verifique se as dependências de voz estão instaladas:
```bash
pip install SpeechRecognition pyaudio
```

### "HUD não aparece"
1. Verifique se PyQt6 está instalado
2. Execute com `python main_singularity.py`
3. Veja logs em `jarvis_singularity.log`

### "Wake word não funciona"
1. Verifique microfone
2. Veja logs para erros de áudio
3. Teste com `python -c "import speech_recognition"`

---

## 📊 Fluxo de Execução

```
1. main_singularity.py inicia
   ↓
2. HUD aparece (Thread Principal)
   ↓
3. Brain Loop inicia (Thread Secundária)
   ↓
4. Voice Controller inicia (Thread de Voz)
   ↓
5. Sistema escuta wake word
   ↓
6. Wake word detectado → HUD verde
   ↓
7. Comando recebido → HUD azul
   ↓
8. AI Agent processa → HUD laranja
   ↓
9. Resposta completa → HUD ciano
```

---

## 🎮 Próximos Passos

1. ✅ **Testar HUD**: Execute e veja o reator
2. ✅ **Testar Voice**: Diga "Jarvis" e dê um comando
3. ⏭️ **Adicionar TTS**: Resposta falada
4. ⏭️ **Integrar Hive Mind**: Sync entre dispositivos
5. ⏭️ **Adicionar mais features**: Gestos, automação, etc.

---

## 💡 Dicas

- **HUD sempre visível**: Fica por cima de todas as janelas
- **Click-through**: Você pode clicar através do HUD
- **Performance**: Animação otimizada para 60 FPS
- **Logs**: Veja `jarvis_singularity.log` para debug

---

**Sistema pronto para uso!** 🎉

Execute `python main_singularity.py` e comece a interagir com JARVIS!
