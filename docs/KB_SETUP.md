# Guia de Configuração da KB do Jarvis

Este documento explica como organizar e configurar a base de conhecimento do Jarvis usando o seu vault Obsidian.

## Visão geral

O Jarvis usa duas configurações principais:

- `JARVIS_KB_PATH`: caminho absoluto para a pasta específica de notes do Jarvis.
- `JARVIS_VAULT_ROOT`: raiz geral do vault Obsidian (`D:\OBSIDIAN\Will`).

A ideia é separar o que é conteúdo específico do Jarvis (KB) do restante da organização pessoal do vault.

## Estrutura recomendada

```text
D:\OBSIDIAN\Will
├── Projetos
│   └── Privados
│       └── PROJECT_JARVIS_5.0-KnowledgeBase
│           ├── README.md
│           ├── CONFIG.md
│           ├── notas-de-setup.md
│           └── ...
├── Vault Geral
│   └── ...
└── Outros
    └── ...
```

### Definições

- `JARVIS_KB_PATH`
  - Deve apontar para a pasta `PROJECT_JARVIS_5.0-KnowledgeBase` ou outra pasta dedicada ao Jarvis.
  - O Jarvis carrega arquivos `.md` dessa pasta durante o startup e transforma o conteúdo em fatos de memória local.
  - Isso garante que a KB seja enxuta e focada no projeto Jarvis.

- `JARVIS_VAULT_ROOT`
  - Deve apontar para `D:\OBSIDIAN\Will`.
  - É a raiz do seu vault Obsidian geral e serve como referência de organização.
  - Não é usada como ingestão principal, apenas como fallback e contexto.

## Por que separar KB e vault raiz?

- `JARVIS_KB_PATH` é a fonte de ingestão real do Jarvis.
- `JARVIS_VAULT_ROOT` pode conter notas pessoais, projetos não relacionados e outras pastas.
- Ao separar, você evita que Jarvis leia conteúdo irrelevante ou muito grande.

## Configuração recomendada

No arquivo `env/.env` ou `backend/.env`:

```env
JARVIS_KB_PATH=D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase
JARVIS_VAULT_ROOT=D:\OBSIDIAN\Will
```

## Como o Jarvis carrega a KB

No backend, o startup chama `backend/app/kb_loader.py`. O loader:

1. Lê `settings.jarvis_kb_path`.
2. Se o caminho existir, escaneia arquivos `.md` recursivamente.
3. Remove frontmatter e títulos, limpa o texto e trunca o conteúdo.
4. Salva cada arquivo como um fato local na memória SQLite.

### Fallback opcional

Se `JARVIS_KB_PATH` estiver vazio, o loader tenta um fallback a partir de `JARVIS_VAULT_ROOT`:

- `D:\OBSIDIAN\Will\Projetos\Privados\PROJECT_JARVIS_5.0-KnowledgeBase`

Use isso apenas quando você quiser manter um valor opcional de `JARVIS_VAULT_ROOT`.

## Boas práticas de organização

- Use a pasta `PROJECT_JARVIS_5.0-KnowledgeBase` apenas para notas importantes do Jarvis.
- Mantenha notas de configuração, instruções, comandos e procedimentos relacionados ao Jarvis.
- Não coloque notas pessoais ou conteúdo irrelevante dentro dessa pasta.
- Estruture a KB com subpastas por tema quando necessário, por exemplo:
  - `config/`
  - `workflows/`
  - `scripts/`
  - `docs/`

## Exemplo de arquivo dentro da KB

```md
# Como configurar o Jarvis

- Defina `JARVIS_KB_PATH` apontando para esta pasta.
- Não use o vault inteiro como KB.
- Atualize `README.md` do projeto e `config/README.md` com as mesmas instruções.
```

## Verificando a configuração

Execute o backend e veja o log de startup:

- `JARVIS carrega automaticamente os arquivos .md dessa KB durante o startup.`
- `KB carregada (X fatos).`

Se o caminho estiver errado, o log exibirá:

- `[KB] Caminho inválido: ... Pulando.`

## Checklist final

- [ ] `JARVIS_KB_PATH` aponta para `PROJECT_JARVIS_5.0-KnowledgeBase`
- [ ] `JARVIS_VAULT_ROOT` aponta para `D:\OBSIDIAN\Will`
- [ ] O diretório KB contém apenas notas relevantes ao Jarvis
- [ ] O backend está carregando a KB no startup
- [ ] A documentação principal e de configuração estão alinhadas
