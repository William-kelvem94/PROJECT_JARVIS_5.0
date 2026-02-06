# 🚀 JARVIS 5.0 - Como Iniciar

## ⚡ Método Mais Rápido (Recomendado)

### 🤖 Launcher Autônomo

**Execute com um único clique!**

```
# Windows - Clique duplo ou execute:
JARVIS.bat
```

### ✅ O que o Launcher Autônomo faz?

1. ✅ **Solicita privilégios de administrador**
2. ✅ **Detecta Python** - Instala automaticamente se necessário
3. ✅ **Cria ambiente virtual** - Isolamento de dependências
4. ✅ **Instala dependências** - Todos os pacotes necessários
5. ✅ **Valida estrutura** - Verifica integridade do projeto
6. ✅ **Inicia JARVIS** - Sistema pronto para uso
7. ✅ **Auto-restart** - Recuperação automática de falhas
8. ✅ **Logs detalhados** - Tudo em `jarvis_launcher.log`

**Não precisa fazer NADA manualmente!** O launcher é 100% autônomo.

---

## 🔍 Verificação Rápida

### Antes de iniciar, verifique se está tudo OK:

```bash
# Windows:
check_setup.bat

# Python (qualquer plataforma):
python check_setup.py
```

Este script verifica:
- ✅ Python instalado e versão correta
- ✅ Ambiente virtual configurado
- ✅ Arquivos críticos presentes
- ✅ Estrutura de pastas OK
- ✅ Sistema pronto para executar

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

## 🛠️ Ferramentas de Diagnóstico

### Verificação Rápida

Execute antes de reportar problemas:

```bash
# Windows:
check_setup.bat

# Python (qualquer plataforma):
python check_setup.py
```

### Validação Completa

Para diagnóstico detalhado:

```bash
python validate_project.py
```

**O que valida:**
- ✅ Estrutura de diretórios (7 pastas essenciais)
- ✅ Arquivos críticos (7 arquivos)
- ✅ Sintaxe Python (todos os .py)
- ✅ Imports e dependências (37 pacotes)
- ✅ Configurações (config.yaml)
- ✅ Entry points (main.py)
- ✅ Testes (se existirem)

### Logs

**Onde encontrar:**
- `jarvis_launcher.log` - Log do launcher
- `jarvis_singularity.log` - Log da aplicação

**Como ver:**
```bash
# Windows:
type jarvis_launcher.log

# Unix/Linux:
cat jarvis_launcher.log
```

---

## 🐛 Problemas Comuns

### "Python não encontrado"
O launcher tentará instalar automaticamente. Se falhar:
1. Instale Python 3.10+ de [python.org](https://www.python.org/downloads/)
2. Marque "Add to PATH" durante instalação
3. Reinicie o terminal
4. Execute novamente `JARVIS.bat`

### "PyQt6 não instalado"
```bash
pip install PyQt6==6.6.1
```

### "NumPy incompatível"
```bash
pip uninstall numpy -y
pip install numpy==1.26.4
```

### "HUD não aparece"
1. Execute `check_setup.py` para diagnosticar
2. Verifique logs em `jarvis_launcher.log`
3. Execute como administrador
4. Teste isoladamente: `python src/interface/hud.py`

### "Wake word não funciona"
1. Verifique microfone em Configurações do Windows
2. Execute `check_setup.py` para verificar dependências
3. Ajuste sensibilidade em `config.yaml`:
```yaml
voice:
  energy_threshold: 300  # Diminuir = mais sensível
```

### Para problemas complexos:

Veja o **[Guia Completo de Troubleshooting](TROUBLESHOOTING.md)** com:
- 📖 Problemas de instalação
- 📦 Problemas de dependências
- 🎮 Problemas de execução
- 🖥️ Problemas de interface
- 🎤 Problemas de voz
- 🤖 Problemas de IA
- 📊 Códigos de erro

---

## 📁 Estrutura Básica

```
PROJECT_JARVIS_5.0/
├── JARVIS.bat              ← Execute este arquivo
├── main.py     ← Entry point
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
python main.py --verbose

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
