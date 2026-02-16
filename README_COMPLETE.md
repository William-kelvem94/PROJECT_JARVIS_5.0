# 🤖 JARVIS 5.0 - Sistema Auto-Organizável e Autocorrigível

## 🎯 Status: 100% Funcional e Pronto para Uso!

**JARVIS 5.0** é um assistente de IA completamente autônomo, capaz de:
- 🔍 Auto-observar seu próprio código e sistema
- 🧠 Auto-diagnosticar problemas usando LLMs
- 🛠️ Auto-corrigir erros automaticamente
- 🌱 Auto-desenvolver novos módulos
- 📚 Aprender com cada intervenção

---

## 🚀 Início Rápido (3 Passos)

### 1️⃣ Instalar Dependências

```bash
# Clone o repositório (se ainda não tiver)
git clone https://github.com/William-kelvem94/PROJECT_JARVIS_5.0
cd PROJECT_JARVIS_5.0

# Execute o assistente de instalação
python3 setup_jarvis.py
```

O script de instalação irá:
- ✅ Verificar Python 3.10+
- ✅ Criar estrutura de diretórios
- ✅ Instalar todas as dependências
- ✅ Validar imports
- ✅ Testar funcionalidade básica
- ✅ Criar scripts de inicialização

### 2️⃣ (Opcional) Instalar Ollama para Self-Healing

Para recursos de auto-cura com IA, instale o Ollama:

```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Windows
# Baixe de: https://ollama.ai

# Depois, baixe um modelo
ollama pull llama2
```

### 3️⃣ Iniciar JARVIS

```bash
# Unix/Linux/Mac
./start_jarvis.sh

# Windows
start_jarvis.bat

# Ou diretamente
python3 main.py
```

---

## 🧬 Camada de Evolução (Evolution Layer)

A inovação principal do JARVIS 5.0 é sua capacidade de auto-manutenção:

### Componentes Principais

#### 1. **Self Observer** (`self_observer.py`)
Monitora continuamente:
- 📊 Métricas do sistema (CPU, memória, GPU)
- 📝 Logs de erro
- 🔍 Estrutura do código (AST scanning)
- ⚙️ Integridade de configurações
- 🏥 Saúde dos subsistemas

#### 2. **Auto Healer** (`auto_healer.py`)
Diagnostica problemas:
- 🧠 Usa LLM (Ollama) para análise inteligente
- 📋 Consulta base de conhecimento
- 🎯 Prioriza ações corretivas
- 📨 Publica planos de ação

#### 3. **Safe Executor** (`safe_executor.py`)
Executa correções com segurança:
- 🛡️ Sandbox isolado
- 💾 Backup automático
- ✅ Validação de código
- ↩️ Rollback em caso de falha
- 📚 Registro de aprendizado

#### 4. **Knowledge Database** (`knowledge_db.py`)
Aprende com experiência:
- 💾 SQLite para persistência
- 🔗 Relaciona problemas → soluções
- 📈 Rastreia taxa de sucesso
- 👤 Integra feedback humano

#### 5. **Authorization Manager** (`authorization_manager.py`)
Controla ações de alto risco:
- 🚦 Classifica risco (LOW/MEDIUM/HIGH/CRITICAL)
- 🔒 Protege arquivos do núcleo
- 👥 Requer aprovação humana para mudanças críticas
- 📊 Rastreia histórico de autorizações

#### 6. **Module Generator** (`module_generator.py`)
Gera novos módulos dinamicamente:
- 🎨 Cria código Python funcional
- 🧪 Testa em sandbox
- 🔌 Hot-swap de plugins
- ⏱️ Monitora por 24h
- ⚡ Auto-desativa se instável

#### 7. **Voice Commands** (`voice_commands.py`)
Comandos de voz inteligentes:
- 🗣️ Entendimento natural de linguagem (via LLM)
- 🌍 Português, inglês ou misto
- 🎯 Extração inteligente de parâmetros
- 🔄 Nada de padrões fixos!

#### 8. **Evolution Manager** (`evolution_manager.py`)
Coordena todos os componentes acima

---

## 🗣️ Comandos de Voz Naturais

**Não há comandos fixos!** JARVIS entende intenção naturalmente.

### Exemplos:

**Mostrar Correções:**
- "show me what you're fixing"
- "mostre o que está corrigindo"
- "what are you working on"
- "deixa eu ver os consertos"

**Autorizar Correção:**
- "authorize correction abc123"
- "autorizo a correção xyz"
- "ok, pode fazer isso"
- "approve that"

**Reverter Mudanças:**
- "undo that"
- "volta atrás"
- "desfaça a última mudança"
- "rollback"

**Desativar Auto-Correção:**
- "pause for 30 minutes"
- "desative por uma hora"
- "stop fixing things"
- "turn off auto-heal"

**Status:**
- "how's it going"
- "status da evolução"
- "show me the system health"

**Manutenção:**
- "do maintenance"
- "faça uma manutenção"
- "check yourself"
- "run diagnostics"

---

## 📁 Estrutura do Projeto

```
PROJECT_JARVIS_5.0/
├── setup_jarvis.py          # Assistente de instalação
├── start_jarvis.sh          # Iniciar (Unix/Linux/Mac)
├── start_jarvis.bat         # Iniciar (Windows)
├── main.py                  # Ponto de entrada principal
├── test_startup.py          # Validação de inicialização
│
├── src/
│   ├── evolution/           # 🧬 Camada de Evolução
│   │   ├── evolution_manager.py
│   │   ├── self_observer.py
│   │   ├── auto_healer.py
│   │   ├── safe_executor.py
│   │   ├── knowledge_db.py
│   │   ├── authorization_manager.py
│   │   ├── module_generator.py
│   │   └── voice_commands.py
│   │
│   ├── core/                # Núcleo do sistema
│   │   ├── infrastructure/  # Event Bus, Boot Manager
│   │   ├── intelligence/    # Cerebro, LLMs
│   │   ├── audio/           # Voz e reconhecimento
│   │   ├── vision/          # Visão computacional
│   │   └── management/      # Orquestração
│   │
│   └── utils/               # Utilitários
│       └── platform_compat.py  # Compatibilidade multi-plataforma
│
├── data/
│   ├── learning/            # Base de conhecimento
│   │   └── knowledge.db     # SQLite database
│   ├── backups/auto/        # Backups automáticos
│   ├── logs/                # Logs do sistema
│   └── database/            # Dados persistentes
│
└── docs/
    ├── EVOLUTION_LAYER.md          # Documentação técnica
    ├── EVOLUTION_QUICK_START.md     # Guia rápido
    └── INTELLIGENT_VOICE_COMMANDS.md # Comandos de voz
```

---

## 🔧 Modos de Operação

### 🎯 Modo Completo (Recomendado)
Com Ollama instalado:
- ✅ Todos os recursos
- ✅ Auto-cura com IA
- ✅ Geração de código
- ✅ Comandos de voz inteligentes

```bash
# Instalar Ollama primeiro
ollama pull llama2

# Iniciar JARVIS
./start_jarvis.sh
```

### 💻 Modo CLI
Sem GUI, apenas terminal:
- ✅ Camada de evolução funcional
- ✅ Coleta de métricas
- ✅ Base de conhecimento
- ⚠️ Sem diagnóstico por LLM (usa heurísticas)

```bash
export JARVIS_EVOLUTION_ENABLED=true
python3 main.py
```

### 🔬 Modo Minimal
Apenas operação básica:
- ✅ Sistema inicializa
- ✅ Módulos centrais funcionam
- ⚠️ Sem auto-cura

```bash
export JARVIS_EVOLUTION_ENABLED=false
python3 main.py
```

---

## 🧪 Testes e Validação

### Executar Todos os Testes

```bash
# Teste de inicialização
python3 test_startup.py

# Testes unitários da Evolution Layer
python3 -m pytest tests/unit/test_evolution_layer.py -v

# Demonstração interativa
python3 demo_evolution.py
```

### Resultados Esperados

```
✅ PASS  Python Syntax (todos os arquivos compilam)
✅ PASS  Critical Imports (módulos da Evolution Layer)
✅ PASS  Evolution Layer (todos os 5 componentes)
✅ PASS  Main Startup (main.py inicia sem erros)

Result: 4/4 tests passed
🎉 All tests passed! JARVIS 5.0 is ready to run!
```

---

## 🐛 Troubleshooting

### Problema: "No module named 'X'"
**Solução:** Execute o setup novamente
```bash
python3 setup_jarvis.py
```

### Problema: "Ollama not detected"
**Solução:** Ollama é opcional para operação básica
```bash
# Para instalar Ollama:
curl https://ollama.ai/install.sh | sh
ollama pull llama2
```

### Problema: "Import error: libEGL"
**Solução:** Bibliotecas GUI faltando (opcional para CLI)
```bash
# Ubuntu/Debian
sudo apt-get install libegl1

# Ou continue sem GUI (funciona perfeitamente)
```

### Problema: "Permission denied"
**Solução:** Dê permissão aos scripts
```bash
chmod +x setup_jarvis.py
chmod +x start_jarvis.sh
chmod +x test_startup.py
```

---

## 📊 Como Funciona a Auto-Cura

### Ciclo de Manutenção

```
1. 🔍 OBSERVAÇÃO
   ↓ Self Observer coleta métricas, logs, estrutura de código
   
2. 🧠 DIAGNÓSTICO  
   ↓ Auto Healer analisa com LLM ou heurísticas
   
3. 🛡️ AUTORIZAÇÃO
   ↓ Authorization Manager valida risco
   
4. 🛠️ CORREÇÃO
   ↓ Safe Executor aplica em sandbox
   
5. ✅ VALIDAÇÃO
   ↓ Testa, se OK → aplica, se FAIL → rollback
   
6. 📚 APRENDIZADO
   ↓ Knowledge DB registra resultado
   
7. 🔄 REPETE se necessário
```

### Exemplo Real

```python
# JARVIS detecta: "função grande com 200 linhas"

# 1. Observer reporta
{
  "code_health": {
    "large_functions": [{
      "file": "src/utils/helpers.py",
      "function": "process_data",
      "lines": 200
    }]
  }
}

# 2. Healer diagnostica via LLM
"Refatorar função em 3 funções menores"

# 3. Authorization Manager
"Risco: MEDIUM - Requer aprovação"

# 4. Executor aplica (após aprovação)
# Cria backup → Aplica mudança → Testa

# 5. Valida
# Testes passam ✅ → Mantém mudança

# 6. Aprende
# Registra: "problema: função grande → solução: refatoração → sucesso: true"
```

---

## 🌟 Recursos Únicos

### 1. Nenhum Comando Fixo
Comandos de voz usam LLM para entender intenção naturalmente. Fale do seu jeito!

### 2. Auto-Desenvolvimento
JARVIS pode criar novos módulos por conta própria quando identifica lacunas.

### 3. Aprendizado Contínuo
Cada ação (sucesso ou falha) é registrada para melhorar decisões futuras.

### 4. Sandbox Seguro
Todas as mudanças são testadas isoladamente antes de serem aplicadas.

### 5. Rollback Automático
Se algo der errado, JARVIS reverte automaticamente.

### 6. Proteção de Núcleo
Arquivos críticos são protegidos e requerem autorização humana.

---

## 📝 Configuração Avançada

### Variáveis de Ambiente

```bash
# Ativar/desativar Evolution Layer
export JARVIS_EVOLUTION_ENABLED=true

# Modo de operação
export JARVIS_MODE=autonomous  # autonomous|semi-autonomous|manual

# Intervalo de observação (segundos)
export JARVIS_OBSERVATION_INTERVAL=300

# Limite de correções por dia
export JARVIS_MAX_CORRECTIONS_PER_DAY=10

# Nível de log
export JARVIS_LOG_LEVEL=INFO
```

### Arquivos Protegidos

Edite `src/core/config/system_manifest.py`:

```python
core_protected_files = [
    "src/core/infrastructure/*",
    "src/core/config/*",
    "main.py",
    "setup_jarvis.py"
]
```

---

## 🤝 Contribuindo

JARVIS 5.0 é um projeto em evolução contínua. Contribuições são bem-vindas!

### Como Contribuir

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

MIT License - Veja LICENSE para detalhes

---

## 🙏 Agradecimentos

- **Ollama** - LLM local para diagnóstico inteligente
- **OpenAI** - Inspiração para arquitetura de agentes
- **Comunidade Python** - Ferramentas incríveis

---

## 📧 Suporte

- **Issues:** https://github.com/William-kelvem94/PROJECT_JARVIS_5.0/issues
- **Documentação:** Veja pasta `docs/`
- **Demos:** Execute `demo_evolution.py`

---

## 🎉 Conclusão

JARVIS 5.0 está **100% funcional e pronto para uso**!

- ✅ Todas as dependências instaladas
- ✅ Todos os testes passando
- ✅ Auto-cura implementada
- ✅ Documentação completa
- ✅ Scripts de inicialização criados

**Basta baixar e executar!**

```bash
git clone https://github.com/William-kelvem94/PROJECT_JARVIS_5.0
cd PROJECT_JARVIS_5.0
python3 setup_jarvis.py
./start_jarvis.sh
```

**Enjoy! 🚀**
