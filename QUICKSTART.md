# 🚀 JARVIS SINGULARITY - GUIA RÁPIDO

## ⚡ INÍCIO RÁPIDO

### Duplo clique aqui:
```
JARVIS_SINGULARITY.bat
```

---

## 🎤 MODO DE VOZ

1. **Aguarde** a mensagem: `🔊 Aguardando wake word 'Jarvis'...`
2. **Diga**: "Jarvis"
3. **HUD fica VERDE** (listening)
4. **Fale seu comando**: Ex: "Qual é a capital do Brasil?"
5. **HUD fica AZUL** (thinking)
6. **Aguarde resposta** (5-30s)
7. **Repita!**

### Comandos de Teste
- "Jarvis, que horas são?"
- "Jarvis, abra o navegador"
- "Jarvis, tire um screenshot"

---

## 🎨 HUD - ESTADOS VISUAIS

| Cor | Estado | Quando |
|-----|--------|--------|
| **CINZA** (pulsando) | IDLE | Aguardando wake word |
| **VERDE** (sólido) | LISTENING | Capturando voz |
| **AZUL** (pulsando) | THINKING | Processando AI |
| **VERDE** (sólido) | SPEAKING | Falando resposta |
| **VERMELHO** | ERROR | Erro detectado |

---

## 📹 VISÃO (Camera)

**SIM!** O JARVIS pode te ver se você tiver webcam:
- ✅ Detecção de presença
- ✅ Reconhecimento facial (se `face_recognition` instalado)
- ✅ Análise de contexto visual

**Ativar visão em comandos:**
- "Jarvis, o que você está vendo?"
- "Jarvis, descreva a tela"
- "Jarvis, tire uma foto"

---

## 🛑 ENCERRAR

- **Ctrl+C** no terminal
- **Fechar janela** do HUD
- **Dizer**: "sair" (modo texto)

**NOTA**: Agora encerra em 2-3 segundos (corrigido!)

---

## ❌ TROUBLESHOOTING

### "Voice mode não implementado"
→ Você rodou o arquivo ANTIGO
→ **SOLUÇÃO**: Execute `JARVIS_SINGULARITY.bat` ou `py main_singularity.py`

### Processo trava ao encerrar
→ **CORRIGIDO!** Agora força exit após 2-3s

### Sem resposta de voz
→ Verifique microfone
→ Diga "Jarvis" mais alto
→ Fallback: use modo texto (digite comandos)

### HUD não aparece
→ Verifique se PyQt6 está instalado: `py -m pip install PyQt6`

---

## 📊 LOGS

Verifique erros em:
- `jarvis_singularity.log`
- Console do terminal
