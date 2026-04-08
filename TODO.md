# TODO - Organização BATs para JARVIS 5.0

## Passos do Plano Aprovado (DEVOPS branch)

### 1. [x] Criar start-jarvis.bat unificado completo
   - Verificações: .env, venv, playwright, models
   - Iniciar 4 janelas paralelas:
     * Backend API (uvicorn)
     * Agents Worker (livekit agents)
     * LiveKit Worker (agents CLI)
     * Frontend (npm dev)

### 2. [x] Renomear arquivos antigos para .bak
   - start-all.bat -> start-all.bat.bak
   - run-agent-worker.bat -> run-agent-worker.bat.bak  
   - run-livekit-worker.bat -> run-livekit-worker.bat.bak

### 3. [] Testar start-jarvis.bat novo
   - Executar e verificar serviços (8000, 7880 workers?, 3000 frontend)

### 4. [x] Commit e push
   - Mensagem PTBR: "Launcher único BAT completo + organização arquivos"

### 5. [ ] Atualizar README.md com instruções novas

Progresso: Iniciando passo 1...

