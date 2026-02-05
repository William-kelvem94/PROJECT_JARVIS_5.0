# 🚀 JARVIS 5.0 - Como Iniciar

## ⚡ Método Mais Rápido

### Windows

**Clique duplo em:**
```
JARVIS.bat
```

**OU execute no terminal:**
```bash
.\JARVIS.bat
```

Pronto! O sistema faz tudo automaticamente.

---

## 🎯 O Que Acontece

O launcher `JARVIS.bat` executa automaticamente:

1. ✅ **Verifica Python** - Confirma instalação
2. ✅ **Instala PyQt6** - Se necessário
3. ✅ **Inicia HUD** - Interface transparente
4. ✅ **Ativa Voz** - Reconhecimento de comandos
5. ✅ **Carrega AI** - Cérebro híbrido

---

## 🖥️ O Que Você Verá

### HUD Transparente
- **Reator pulsante** no canto inferior direito
- **Cor ciano** = Sistema online
- **Click-through** = Você pode clicar através

### Estados Visuais
- 🔵 **Ciano** = Aguardando (Idle)
- 🟢 **Verde** = Escutando você
- 🔵 **Azul** = Pensando/Processando
- 🟠 **Laranja** = Falando
- 🔴 **Vermelho** = Erro

---

## 🎤 Como Usar

### 1. Ative o Sistema
```
Você: "Jarvis"
```
→ HUD fica **verde** (escutando)

### 2. Dê um Comando
```
Você: "Abra o Chrome"
Você: "Qual é a hora?"
Você: "Tire uma screenshot"
```
→ HUD fica **azul** (processando)

### 3. JARVIS Responde
→ HUD volta para **ciano** (idle)

---

## 🔧 Configuração (Opcional)

### API Keys

Para usar IA avançada, edite `config.yaml`:

```yaml
brain:
  groq_api_key: "gsk_..."      # https://console.groq.com
  gemini_api_key: "AI..."      # https://makersuite.google.com
```

**Sem API keys?** Sistema funciona com IA local (mais lento).

---

## 🐛 Problemas Comuns

### "Python não encontrado"
1. Instale Python 3.10+ de [python.org](https://www.python.org/downloads/)
2. Marque "Add to PATH" durante instalação
3. Reinicie o terminal

### "PyQt6 não instalado"
```bash
python -m pip install PyQt6
```

### "HUD não aparece"
1. Verifique logs em `jarvis_singularity.log`
2. Execute como administrador
3. Teste: `python main_singularity.py`

### "Wake word não funciona"
1. Verifique microfone
2. Teste: `python -c "import speech_recognition"`
3. Ajuste volume do microfone

---

## 📁 Estrutura Básica

```
PROJECT_JARVIS_5.0/
├── JARVIS.bat              ← Execute este arquivo
├── main_singularity.py     ← Entry point
├── config.yaml             ← Configurações
├── src/
│   ├── interface/hud.py   ← HUD transparente
│   └── core/              ← Cérebro, voz, visão
└── data/                   ← Dados e cache
```

---

## 🎮 Comandos Avançados

### Linha de Comando

```bash
# Executar com logs detalhados
python main_singularity.py --verbose

# Modo CLI (sem HUD)
python legacy/main.py

# Captura de tela
python legacy/main.py capture

# Processar imagem
python legacy/main.py process --input foto.png
```

---

## 📚 Próximos Passos

1. ✅ **Execute** `JARVIS.bat`
2. ✅ **Teste** dizendo "Jarvis"
3. ✅ **Configure** API keys (opcional)
4. ✅ **Explore** comandos de voz
5. ✅ **Leia** [README.md](README.md) para mais detalhes

---

## 💡 Dicas

- **HUD sempre visível**: Fica por cima de tudo
- **Click-through**: Não atrapalha seu trabalho
- **Performance**: ~2-5% CPU em idle
- **Logs**: Veja `jarvis_singularity.log` para debug

---

**Sistema pronto para uso!** 🎉

Execute `JARVIS.bat` e comece a interagir!
