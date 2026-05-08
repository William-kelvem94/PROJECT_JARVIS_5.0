# Protocolo 89 — Sandbox Híbrido de Segurança

## Visão Geral

Sistema de execução isolada para código gerado pelo LLM, implementado em `security/holodeck.py`.

## Camadas de Proteção

### Camada 1 — Processo Isolado
- Subprocessos com privilégios reduzidos
- `seccomp` (Linux) / `Job Objects` (Windows)
- Uso: Scripts simples, cálculos

### Camada 2 — Validação Semântica (AST)
- Análise de Árvore de Sintaxe Abstrata antes da execução
- Detecta: `os.system()`, `eval()`, `exec()`, imports perigosos
- Implementado em `security/sentinel_parser.py`

### Camada 3 — Container Docker (Planejado)
- Isolamento completo para código de terceiros
- Rede isolada via bridge privada
- Status: Roadmap Fase 2

## SentinelParser — Blocklist

```python
DANGEROUS_PATTERNS = [
    r"rm\s+-rf", r"mkfs\.", r"format\s+[a-z]:",
    r"dd\s+if=", r"shutdown", r"chmod\s+777"
]
DANGEROUS_IMPORTS = ["os", "sys", "shutil", "subprocess", "socket", "pty"]
```

## Referência
- `docs/archive/research/OMEGA_RESEARCH/docs/protocol_89_v2.md`
- `docs/archive/research/PROJECT_SOPHISTICATION/docs/protocolo_seguranca_89.md`
