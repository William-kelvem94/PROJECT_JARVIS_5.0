"""
JARVIS Vault Memory — Escreve memórias persistentes no vault Obsidian.

Responsabilidades:
- Salvar memórias episódicas em JARVIS/Memorias/Episodicas/
- Salvar/atualizar diário diário em JARVIS/Memorias/Diario/YYYY-MM-DD.md
- Atualizar JARVIS/Contexto-Atual/Estado.md ao fim de cada sessão
- Registrar aprendizados em JARVIS/Aprendizado/
- Registrar decisões importantes em JARVIS/Decisoes/INDEX.md
- Atualizar preferências em JARVIS/Sobre-Will/Preferencias.md
"""

import os
import re
import datetime
from pathlib import Path
from loguru import logger

# ── Caminhos ────────────────────────────────────────────────────────────────
_VAULT_ROOT = os.getenv("JARVIS_VAULT_ROOT", r"D:\OBSIDIAN\Will")
_JARVIS_DIR = os.path.join(_VAULT_ROOT, "JARVIS")

PATHS = {
    "episodicas":    os.path.join(_JARVIS_DIR, "Memorias", "Episodicas"),
    "diario":        os.path.join(_JARVIS_DIR, "Memorias", "Diario"),
    "aprendizado":   os.path.join(_JARVIS_DIR, "Aprendizado"),
    "decisoes":      os.path.join(_JARVIS_DIR, "Decisoes"),
    "contexto":      os.path.join(_JARVIS_DIR, "Contexto-Atual"),
    "sobre_will":    os.path.join(_JARVIS_DIR, "Sobre-Will"),
}


def _ensure_dirs():
    for path in PATHS.values():
        os.makedirs(path, exist_ok=True)


def _now() -> tuple[str, str]:
    """Retorna (data ISO, hora HH:MM)."""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")


def _slugify(text: str) -> str:
    """Gera slug para nome de arquivo."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:60]


# ── Memórias Episódicas ──────────────────────────────────────────────────────

def save_episodic(
    title: str,
    content: str,
    project: str = "",
    keywords: list[str] | None = None,
    importance: str = "MEDIA",
    initiated_by: str = "JARVIS",
) -> str:
    """
    Salva uma memória episódica em JARVIS/Memorias/Episodicas/YYYY-MM-DD-slug.md
    Retorna o path do arquivo criado.
    """
    _ensure_dirs()
    date, hora = _now()
    tags = keywords or []
    tags_str = ", ".join(tags)
    slug = _slugify(title)
    filename = f"{date}-{slug}.md"
    filepath = os.path.join(PATHS["episodicas"], filename)

    # Se já existe, acrescentar ao final ao invés de sobrescrever
    if os.path.exists(filepath):
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n*Adicionado em {date} às {hora}*\n\n{content}")
        logger.info(f"[VaultMemory] Memória episódica atualizada: {filename}")
        return filepath

    body = f"""---
title: "{title}"
date: "{date}"
hora: "{hora}"
tags: [jarvis, memoria, episodica{', ' + tags_str if tags else ''}]
keywords: [{tags_str}]
importancia: "{importance}"
projeto: "{project}"
---

# {title}

## 📅 Contexto
- **Data/Hora:** {date} às {hora}
- **Projeto:** {project or 'N/A'}
- **Iniciado por:** {initiated_by}

## 📝 Conteúdo

{content}

---
*Salvo pelo Jarvis em: {date} {hora}*
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(body)
    logger.success(f"[VaultMemory] Memória episódica salva: {filename}")
    return filepath


# ── Diário ───────────────────────────────────────────────────────────────────

def append_diary(
    summary: str,
    project: str = "",
    facts_saved: int = 0,
    decisions: str = "",
    session_n: int = 1,
) -> str:
    """
    Acrescenta (ou cria) entrada no diário do dia em JARVIS/Memorias/Diario/YYYY-MM-DD.md
    Retorna o path do arquivo.
    """
    _ensure_dirs()
    date, hora = _now()
    filepath = os.path.join(PATHS["diario"], f"{date}.md")

    entry = f"""
### Sessão {session_n} — {hora}
- **Projeto/Tema:** {project or 'N/A'}
- **Resumo:** {summary}
- **Fatos salvos:** {facts_saved}
- **Decisões:** {decisions or 'Nenhuma'}
"""

    if not os.path.exists(filepath):
        header = f"""---
title: "Diário — {date}"
date: "{date}"
tags: [jarvis, diario, {date}]
---

# Diário — {date}

"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + entry)
        logger.success(f"[VaultMemory] Diário criado: {date}.md")
    else:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(f"[VaultMemory] Entrada adicionada ao diário: {date}.md")

    return filepath


# ── Estado Atual ─────────────────────────────────────────────────────────────

def update_current_state(
    project: str,
    done: str,
    next_action: str,
    notes: str = "",
    mode: str = "Desenvolvimento/Engenharia",
) -> str:
    """
    Atualiza JARVIS/Contexto-Atual/Estado.md com o estado da sessão atual.
    """
    _ensure_dirs()
    date, hora = _now()
    filepath = os.path.join(PATHS["contexto"], "Estado.md")

    body = f"""---
title: "Estado Atual — Jarvis"
description: "O que está acontecendo agora: projeto em foco, modo de operação, último contexto."
tags: [jarvis, contexto, estado, atual]
updated: {date}
---

# Estado Atual — Jarvis

> Atualizado automaticamente pelo Jarvis após cada sessão relevante.

## 📅 Última Sessão

- **Data:** {date} às {hora}
- **Projeto em foco:** {project}
- **O que foi feito:** {done}

## 🎯 Foco Atual

- Projeto: **{project}**
- Próxima ação: {next_action}

## 🧠 Contexto Carregado

- Perfil de Will: [[../Sobre-Will/Perfil]]
- Projetos ativos: [[../Sobre-Will/Projetos-Ativos]]
- Objetivos: [[../Sobre-Will/Objetivos]]

## ⚡ Modo de Operação

- **Modo:** {mode}

## 📝 Notas de Continuidade

{notes or '*(sem notas extras)*'}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(body)
    logger.info(f"[VaultMemory] Estado atualizado: {date} {hora}")
    return filepath


# ── Aprendizado ───────────────────────────────────────────────────────────────

def save_learning(fact: str, category: str = "tecnico", source: str = "conversa") -> bool:
    """
    Adiciona uma linha de aprendizado ao arquivo de índice de aprendizado.
    category: 'tecnico' | 'pessoal' | 'padrao' | 'erro'
    """
    _ensure_dirs()
    date, hora = _now()
    index_path = os.path.join(PATHS["aprendizado"], "INDEX.md")

    new_row = f"| {date} | {category} | {fact[:120]} |\n"

    if os.path.exists(index_path):
        content = Path(index_path).read_text(encoding="utf-8")
        # Insere antes da linha de rodapé (## 🔍) se existir, senão acrescenta
        if "## 🆕 Últimos Aprendizados" in content:
            # Encontra a tabela e adiciona nova linha
            table_marker = "| Data | Categoria | Fato |"
            if table_marker in content:
                # Adicionar após o cabeçalho da tabela e separador
                lines = content.split("\n")
                insert_after = -1
                for i, line in enumerate(lines):
                    if "|---|---|---|" in line:
                        insert_after = i
                        break
                if insert_after >= 0:
                    lines.insert(insert_after + 1, f"| {date} | {category} | {fact[:120]} |")
                    Path(index_path).write_text("\n".join(lines), encoding="utf-8")
                    logger.info(f"[VaultMemory] Aprendizado registrado: {fact[:60]}")
                    return True

        # Fallback: append section
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(f"\n| {date} | {category} | {fact[:120]} |")
        return True
    return False


# ── Decisão ───────────────────────────────────────────────────────────────────

def save_decision(
    title: str,
    decision: str,
    project: str = "",
    rationale: str = "",
    alternatives: str = "",
    impact: str = "",
) -> bool:
    """
    Acrescenta uma decisão ao JARVIS/Decisoes/INDEX.md
    """
    _ensure_dirs()
    date, _ = _now()
    index_path = os.path.join(PATHS["decisoes"], "INDEX.md")

    entry = f"""
### [{date}] {title}
- **Projeto/Contexto:** {project or 'Geral'}
- **Decisão:** {decision}
- **Alternativas consideradas:** {alternatives or 'N/A'}
- **Raciocínio:** {rationale or 'N/A'}
- **Impacto:** {impact or 'N/A'}
- **Status:** Ativa
"""
    if os.path.exists(index_path):
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(f"[VaultMemory] Decisão registrada: {title}")
        return True
    return False


# ── Preferência de Will ───────────────────────────────────────────────────────

def update_will_preference(section: str, key: str, value: str) -> bool:
    """
    Insere ou atualiza uma preferência em JARVIS/Sobre-Will/Preferencias.md
    section: nome da seção (ex: '⏰ Horários e Ritmo')
    key: nome da preferência
    value: valor descoberto
    """
    _ensure_dirs()
    date, _ = _now()
    pref_path = os.path.join(PATHS["sobre_will"], "Preferencias.md")

    if not os.path.exists(pref_path):
        logger.warning(f"[VaultMemory] Arquivo não encontrado: {pref_path}")
        return False

    content = Path(pref_path).read_text(encoding="utf-8")

    # Substitui linha com "[ ] A preencher" se section existir
    new_entry = f"- **{key}:** {value} *(descoberto em {date})*"
    placeholder = f"- [ ] A preencher conforme"

    if section in content:
        lines = content.split("\n")
        in_section = False
        for i, line in enumerate(lines):
            if section in line:
                in_section = True
            if in_section and placeholder in line:
                lines[i] = new_entry
                Path(pref_path).write_text("\n".join(lines), encoding="utf-8")
                logger.info(f"[VaultMemory] Preferência atualizada: {key}")
                return True

    # Fallback: append at end of file
    with open(pref_path, "a", encoding="utf-8") as f:
        f.write(f"\n- **{key}:** {value} *(descoberto em {date})*")
    return True


# ── Singleton / Helpers públicos ─────────────────────────────────────────────

def is_vault_available() -> bool:
    """Verifica se o vault Obsidian está acessível."""
    return os.path.isdir(_JARVIS_DIR)


def get_vault_stats() -> dict:
    """Retorna estatísticas rápidas do vault."""
    stats = {"available": is_vault_available()}
    if stats["available"]:
        for name, path in PATHS.items():
            try:
                files = [f for f in os.listdir(path) if f.endswith(".md")] if os.path.isdir(path) else []
                stats[name] = len(files)
            except Exception:
                stats[name] = 0
    return stats
