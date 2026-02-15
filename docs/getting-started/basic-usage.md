# 🎯 JARVIS 5.0 - Primeiros Passos

## 🚀 Início em 30 Segundos

1. **Execute o launcher**
```bash
JARVIS.bat
```

2. **Aguarde HUD aparecer**
- Reator pulsante ciano no canto inferior direito

3. **Diga "Jarvis"**
- HUD fica verde

4. **Dê um comando**
```
"Abra o navegador"
"Qual é a hora?"
"Tire uma screenshot"
```

Pronto! Você está usando JARVIS! 🎉

---

## 🎨 Entendendo o HUD

### Estados Visuais

| Cor | Estado | O Que Significa |
|-----|--------|-----------------|
| 🔵 Ciano | Idle | Aguardando comando |
| 🟢 Verde | Listening | Escutando você |
| 🔵 Azul | Thinking | Processando |
| 🟠 Laranja | Speaking | Falando |
| 🔴 Vermelho | Error | Erro detectado |

### Características
- **Transparente**: Você vê através dele
- **Click-through**: Não atrapalha cliques
- **Always on top**: Sempre visível
- **60 FPS**: Animação suave

---

## 🎤 Comandos de Voz

### Wake Word
```
"Jarvis"
```
→ Sistema ativa e aguarda comando

### Comandos Básicos
```
"Abra o Chrome"
"Feche a janela"
"Qual é a hora?"
"Tire uma screenshot"
"Leia o que está na tela"
```

### Comandos Avançados
```
"Execute o código Python"
"Analise esta imagem"
"Organize meus arquivos"
"Pesquise sobre [assunto]"
```

---

## ⚙️ Configuração Inicial

### 1. API Keys (Opcional)

Para IA avançada, edite `config.yaml`:

```yaml
brain:
  groq_api_key: "gsk_..."      # https://console.groq.com
  gemini_api_key: "AI..."      # https://makersuite.google.com
```

**Sem API keys?**
- Sistema funciona com IA local
- Mais lento, mas totalmente offline

### 2. Ajustar Microfone

```yaml
senses:
  hearing_model: "base"        # tiny, base, small, medium, large
```

- `tiny`: Mais rápido, menos preciso
- `base`: Balanceado (padrão)
- `large`: Mais preciso, mais lento

### 3. Personalizar Voz

```yaml
mouth:
  tts_engine: "edge"
  voice: "pt-BR-FranciscaNeural"  # Voz feminina
  # voice: "pt-BR-AntonioNeural"  # Voz masculina
```

---

## 🎮 Modos de Uso

### Modo 1: Interface Gráfica (HUD)
```bash
python main_singularity.py
```
- HUD transparente
- Comandos de voz
- Interação visual

### Modo 2: Linha de Comando
```bash
python legacy/main.py
```
- Sem HUD
- Apenas terminal
- Scripts e automação

### Modo 3: GUI Antiga (Legacy)
```bash
python legacy/main.py
```
- Interface CustomTkinter
- Mais recursos visuais
- Sistema antigo preservado

---

## 📚 Exemplos Práticos

### Exemplo 1: Captura e Análise
```
Você: "Jarvis"
JARVIS: [Verde] "Pois não?"
Você: "Tire uma screenshot e analise"
JARVIS: [Azul] "Capturando e analisando..."
JARVIS: [Ciano] "Detectei um formulário com 5 campos..."
```

### Exemplo 2: Automação
```
Você: "Jarvis"
JARVIS: [Verde]
Você: "Abra o Chrome e pesquise Python tutorial"
JARVIS: [Azul] "Abrindo Chrome e pesquisando..."
JARVIS: [Ciano] "Concluído"
```

### Exemplo 3: Informação
```
Você: "Jarvis"
JARVIS: [Verde]
Você: "Qual é o uso de CPU?"
JARVIS: [Azul] "Verificando..."
JARVIS: [Laranja] "CPU está em 23%"
```

---

## 🐛 Problemas Comuns

### HUD não aparece
1. Verifique se PyQt6 está instalado
```bash
python -m pip install PyQt6
```

2. Veja logs
```bash
type jarvis_singularity.log
```

3. Execute com admin
```bash
# Clique direito em JARVIS.bat > Executar como administrador
```

### Wake word não detecta
1. Teste microfone
```bash
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

2. Ajuste volume do microfone no Windows

3. Fale mais alto e claro

### Sistema lento
1. Use API keys (Groq/Gemini)
2. Reduza modelo de voz (`tiny` em vez de `base`)
3. Feche programas pesados

---

## 🎯 Próximos Passos

### Nível 1: Básico
- ✅ Executar JARVIS
- ✅ Testar wake word
- ✅ Comandos simples

### Nível 2: Intermediário
- ⏭️ Configurar API keys
- ⏭️ Personalizar voz
- ⏭️ Criar workflows

### Nível 3: Avançado
- ⏭️ Integrar com IoT
- ⏭️ Criar plugins
- ⏭️ Hive Mind (sync)

---

## 📖 Documentação Completa

- [README.md](../README.md) - Visão geral
- [installation.md](installation.md) - Instalação detalhada
- [QUICKSTART.md](../QUICKSTART.md) - Guia rápido
- [advanced_features.md](advanced_features.md) - Recursos avançados

---

## 💡 Dicas Pro

1. **Fale naturalmente**: JARVIS entende linguagem natural
2. **Use wake word sempre**: Garante que ele está escutando
3. **Veja logs**: `jarvis_singularity.log` tem tudo
4. **Experimente**: Teste diferentes comandos
5. **Configure**: Personalize em `config.yaml`

---

**Você está pronto para usar JARVIS!** 🚀

Diga "Jarvis" e comece a interagir!
