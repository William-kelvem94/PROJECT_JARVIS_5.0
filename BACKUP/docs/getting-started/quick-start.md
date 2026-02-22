# 🚀 JARVIS 5.0 - Guia de Início Rápido

**Tempo estimado:** 10 minutos  
**Pré-requisito:** [Instalação completa](installation.md)

---

## ✅ Verificação Rápida

Antes de começar, certifique-se de que:
- ✅ JARVIS está instalado (`START_JARVIS.bat` existe)
- ✅ Python 3.10+ instalado
- ✅ Ambiente virtual criado (`venv/` existe)

---

## 🎬 Primeira Execução

### 1. Iniciar JARVIS

**Windows:**
```bash
START_JARVIS.bat
```

Você verá:
```
[STAGE 0] Infrastructure Synchronization
[STAGE 1] Environment Validation
[STAGE 2] Model Checks
[STAGE 2.7] Learning Systems Initialization
✅ SINGULARITY CORE ENGAGED
```

### 2. Aguarde Inicialização

Primeira vez demora ~30-60 segundos:
- Carrega modelos de IA
- Inicializa câmera/microfone
- Prepara sistemas de aprendizado

---

## 🎤 Primeiros Comandos

### Comandos Básicos de Voz

1. **Ativar JARVIS:**
   ```
   "Olá JARVIS"
   ```
   Resposta esperada: *"Sim, senhor. Como posso ajudar?"*

2. **Status do Sistema:**
   ```
   "Status do sistema"
   ```
   Resposta: Info sobre CPU, GPU, sistema operacional

3. **Abrir Programas:**
   ```
   "Abrir Chrome"
   "Abrir Notepad"
   "Abrir Spotify"
   ```

4. **Pesquisar na Web:**
   ```
   "Pesquise sobre Python"
   "Busque notícias do Brasil"
   ```

5. **Controle de Sistema:**
   ```
   "Aumentar volume"
   "Diminuir brilho"
   ```

---

## 🖥️ Interface Gráfica

### Acessar Dashboard

O JARVIS tem 2 interfaces:

**1. HUD Overlay (Modo Transparente)**
- Aparece automaticamente na tela
- Minimalista e futurista
- Botão: "Switch to Dashboard"

**2. Control Dashboard (Modo Completo)**
- Painel de controle total
- Configurações avançadas
- Tabs: Brain, Voice, Vision, **Learning**, Logs, System

### Trocar entre Modos

- No HUD: Clique em **"Switch to Dashboard"**
- No Dashboard: Clique em **"Switch to HUD Overlay"**

---

## 🧠 Ativar Aprendizado (Opcional mas Recomendado)

### Passo 1: Verificar Status

1. Abra **Control Dashboard**
2. Vá para tab **🎓 Learning**
3. Clique em **🔄 Refresh Status**

Deve aparecer:
```
✅ ONLINE - 4/4 systems active
✅ Feedback Loop
✅ Continual Learner
✅ Knowledge Distiller
✅ Dream Cycle
```

### Passo 2: Dar Primeiro Feedback

Use JARVIS normalmente por alguns minutos, depois:

1. Dashboard → Learning tab
2. Após um comando bem-sucedido: **👍 Good Response**
3. Após um erro: **👎 Bad Response**

Isso acelera o aprendizado!

---

## ⚙️ Configurações Essenciais

### API Keys (Para usar nuvem)

Se quiser usar modelos da nuvem (Gemini, OpenAI):

1. Abra: `config/settings.json`
2. Adicione suas chaves:
```json
{
  "GOOGLE_API_KEY": "sua-chave-aqui",
  "OPENAI_API_KEY": "sua-chave-aqui"
}
```

Ou use variáveis de ambiente do Windows.

**Guia completo:** [api-keys-setup.md](api-keys-setup.md)

---

## 🎯 Checklist Pós-Instalação

- [ ] JARVIS iniciou sem erros
- [ ] Comando de voz funcionou ("Olá JARVIS")
- [ ] Dashboard abriu corretamente
- [ ] Learning Systems estão ONLINE
- [ ] (Opcional) API keys configuradas

---

## 🔧 Problemas Comuns

### "Microfone não detectado"
**Solução:**
1. Dashboard → Voice tab
2. Selecione seu microfone na lista
3. Clique "Save Voice Config"

### "Câmera falhou"
**Solução:**
1. Dashboard → Vision tab
2. Desmarque "FaceID Enabled" temporariamente
3. Teste sem câmera primeiro

### "Learning systems HIBERNATING"
**Solução:**
1. Abra: `config/ai_config.yaml`
2. Encontre: `continual_learning:`
3. Mude: `enabled: false` → `enabled: true`
4. Reinicie JARVIS

---

## 📚 Próximos Passos

### Nível Iniciante
1. ✅ **Você está aqui!**
2. 📖 [Comandos de Voz Completos](../user-guide/voice-commands.md)
3. 👁️ [Sistema de Visão (FaceID)](../user-guide/vision-system.md)

### Nível Intermediário
1. 🧠 [Sistema de Aprendizado](../ai-systems/learning-system.md)
2. 🤖 [Criar Automações](../user-guide/automation.md)
3. 📊 [Dashboard Avançado](../user-guide/dashboard.md)

### Nível Avançado
1. 🏗️ [Arquitetura do Sistema](../architecture/overview.md)
2. 🔧 [Guia do Desenvolvedor](../technical/developer-guide.md)
3. 🧬 [Treinar Modelos](../ai-systems/model-training.md)

---

## 🆘 Ajuda

- **Problemas técnicos:** [troubleshooting.md](../maintenance/troubleshooting.md)
- **Perguntas sobre IA:** [learning-system.md](../ai-systems/learning-system.md) (FAQ)
- **Issues:** GitHub Issues

---

<div align="center">

**Pronto para começar sua jornada com JARVIS! 🚀**

*Próximo: [Comandos de Voz](../user-guide/voice-commands.md)*

</div>
