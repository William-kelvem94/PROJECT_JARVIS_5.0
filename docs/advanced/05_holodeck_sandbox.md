# Holodeck — Ambiente de Teste Isolado

## Visão Geral

O `security/holodeck.py` fornece um ambiente sandbox para execução de código autogerado.

## Fluxo de Execução

```
Código Gerado pelo LLM
    ↓
SentinelParser (AST Validation)
    ↓ aprovado
Holodeck.run(code)
    ↓
Diretório temporário isolado
    ↓
subprocess com timeout (30s)
    ↓
Resultado + telemetria
    ↓ aprovado pelo usuário
Promoção ao core (manual)
```

## Implementação

```python
holodeck = Holodeck()
result = holodeck.run_code(generated_code, timeout=30)
# result: {"stdout": ..., "stderr": ..., "returncode": ...}
```

## Limitações Atuais
- Isolamento de processo (não container)
- Sem rede isolada (Fase 2)
- Aprovação manual para promoção ao core

## Referência
- `OMEGA_RESEARCH/docs/protocol_89_v2.md` (seção Holodeck)
- Implementação: `backend/app/security/holodeck.py`
