# TODO.md - Plano de Correções JARVIS 5.0 (PT-BR)

## 📋 Phase 1: Tornar Funcional AGORA (Workers + Scripts)
- [ ] 1. ✅ Criado este TODO.md
- [x] 2. ✅ Corrigir `backend/agents_worker.py` → CLI LiveKit completo
- [x] 3. ✅ Remover `backend/agents_worker_fixed.py` (truncado)\n- [x] 4. ✅ Fix `start-jarvis.bat` → chamar `python agents_worker.py`

- [ ] 6. Criar `.env.example` com chaves (LIVEKIT/GEMINI)
- [ ] 7. `python backend/setup.py` → validar deps
- [ ] 8. `start-jarvis.bat` → Backend 8000 + Frontend 3000 + Worker UP
- [ ] 9. Teste: localhost:3000 → Conectar agente voz/video

## 🔧 Phase 2: Otimizações
- [ ] Screenshot gallery: 30s poll + cache
- [ ] agents.py: Fix imports menores (datetime/GPUtil)
- [ ] Testes: pytest backend/tests/
- [ ] Docker: compose up
- [ ] Monitoring: scripts/monitor-heartbeat.ps1

## 📊 Status
- **Atual**: Phase 1 iniciada
- **Próximo**: Aguardar confere edits → marcar [x]

**Comando para testar após edits**: `start-jarvis.bat`

