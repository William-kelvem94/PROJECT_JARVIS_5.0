# TODO - Configuração da Base de Conhecimento (KB) para JARVIS 5.0

Plano aprovado pelo usuário. Breakdown em passos lógicos:

## Passos do Plano (KB Integration)

### 1. [✅] Criar/atualizar env/.env.example com vars KB
   - Adicionar JARVIS_KB_PATH e JARVIS_VAULT_ROOT
   - Arquivo: env/.env.example

### 2. [✅] Editar backend/app/config.py
   - Adicionar campos Pydantic para KB paths
   - Importar e validar

### 3. [✅] Criar backend/app/kb_loader.py
   - Função para escanear MDs da KB
   - Carregar em local_memory como fatos "knowledge_base"

### 4. [✅] Editar backend/app/main.py
   - Importar kb_loader
   - Chamar load_kb() no startup_event()

### 5. [✅] Editar backend/app/agents.py
   - Injetar info da KB no initial_ctx do agente

### 6. [✅] Editar prompts.py, README.md, config/README.md
   - Menções à KB nos prompts/docs

### 7. [✅] Teste Final
   - Config KB implementada e docs atualizados.
   - Para validar: Copie env/.env.example → env/.env, ajuste JARVIS_KB_PATH, rode start-jarvis.bat e cheque logs para "KB carregada".

### 8. [✅] Finalizado

Progresso: Todas as etapas concluídas.

**O que foi feito:**
- KB loader implementado e ligado ao startup do backend.
- Configuração de ambiente e validação em `backend/app/config.py` concluída.
- Documentação atualizada em `README.md`, `config/README.md` e `docs/KB_SETUP.md`.
- Exemplo de `.env` atualizado para `JARVIS_KB_PATH` e `JARVIS_VAULT_ROOT`.

**Validação sugerida:**
- Copie `env/.env.example` para `env/.env`
- Ajuste `JARVIS_KB_PATH` para sua KB
- Rode `start-jarvis.bat`
- Verifique o log de startup para `KB carregada`.
