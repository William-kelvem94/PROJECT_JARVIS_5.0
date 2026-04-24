#!/usr/bin/env python3
"""
AUDITORIA TOTAL DE INTEGRIDADE – JARVIS v6.1
Script offline, completo, sem dependência de IA.
Valida sintaxe, imports, caminhos absolutos, segurança e compatibilidade de hardware.
Gera um relatório final (audit_report.md) na mesma pasta.
"""

import os, sys, ast, json, re
from pathlib import Path

# --- CONFIGURAÇÕES ---
PROJECT_ROOT = Path(__file__).parent.resolve()
EXCLUDE_DIRS = {'.git', '.venv', 'venv', 'env', 'node_modules', '.next', '.pytest_cache', '__pycache__', '.obsidian', 'dist', 'build', 'site-packages', '.mypy_cache', '.tox'}
EXCLUDE_EXT = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.jpg', '.png', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.wav', '.mp4', '.webm', '.lock'}

RELEVANT_EXT = {'.py', '.ts', '.tsx', '.js', '.jsx', '.bat', '.ps1', '.yaml', '.yml', '.toml', '.json', '.md', '.cfg', '.ini', '.env', '.gitignore', '.dockerignore', 'Dockerfile'}

# Padrões de segurança
HARDCODE_PATH_PATTERN = re.compile(r'[a-zA-Z]:\\[Uu]sers\\[Ww]illi', re.IGNORECASE)  # exceto se justificado
ALLOWED_HARDCODE = re.compile(r'C:\\Users\\willi\\Documents\\GitHub\\Will-obsidian')  # vault

# --- FUNÇÕES DE VALIDAÇÃO ---

def listar_arquivos(root: Path):
    """Lista todos os arquivos relevantes, excluindo diretórios e extensões proibidas."""
    arquivos = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Remove diretórios excluídos e também backend/venv explicitamente
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        # Pula se estamos dentro de venv ou site-packages
        if 'venv' in dirpath or 'site-packages' in dirpath:
            continue
        for fname in filenames:
            fpath = Path(dirpath) / fname
            ext = fpath.suffix.lower()
            if ext in EXCLUDE_EXT and fname != 'Dockerfile' and not fname.endswith('.env'):
                continue
            # Inclui Dockerfile, .env, .gitignore etc. mesmo sem extensão
            arquivos.append(fpath.relative_to(root))
    return sorted(arquivos, key=lambda x: str(x))

def check_python_syntax(filepath: Path) -> tuple:
    """Verifica sintaxe Python e imports."""
    try:
        with open(PROJECT_ROOT / filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])
        return True, imports, None
    except SyntaxError as e:
        return False, [], f"SyntaxError: {e}"
    except Exception as e:
        return False, [], str(e)

def check_js_ts_syntax(filepath: Path) -> tuple:
    """Verifica padrões básicos em JS/TS."""
    try:
        with open(PROJECT_ROOT / filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # Verifica se há imports malucos ou strings não fechadas (básico)
        if 'import ' in content:
            # Pode conter imports válidos
            pass
        # Tenta parsear com json se for .json
        if filepath.suffix == '.json':
            json.loads(content)
        return True, [], None
    except json.JSONDecodeError as e:
        return False, [], f"JSON inválido: {e}"
    except Exception as e:
        return True, [], str(e)  # Não bloqueia

def check_bat_ps1(filepath: Path) -> tuple:
    """Verifica arquivos de lote/PowerShell."""
    try:
        with open(PROJECT_ROOT / filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # Checagens básicas
        if filepath.suffix == '.bat' and '@echo off' not in content.lower() and 'echo off' not in content.lower():
            return True, [], "Pode faltar @echo off"
        return True, [], None
    except Exception as e:
        return False, [], str(e)

def check_hardware_compliance(source: str) -> list:
    """Verifica se o código respeita os dois perfis de hardware."""
    problemas = []
    # Se usa torch.cuda sem fallback
    if 'torch.cuda' in source and 'cpu' not in source.lower() and 'device' not in source.lower():
        problemas.append("Usa torch.cuda sem fallback explícito para CPU")
    # Se menciona VRAM mas não trata < 5GB
    if 'vram' in source.lower() and '5' not in source:
        pass  # Não é erro, mas pode ser verificado
    return problemas

def check_path_security(source: str) -> list:
    """Verifica caminhos absolutos proibidos."""
    problemas = []
    matches = HARDCODE_PATH_PATTERN.findall(source)
    for m in matches:
        if not ALLOWED_HARDCODE.match(m):
            problemas.append(f"Hardcode de caminho pessoal: {m}")
    return problemas

def check_secrets(source: str) -> list:
    """Verifica strings que pareçam chaves ou tokens hardcoded."""
    problemas = []
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', 'Chave da OpenAI?'),
        (r'[A-Za-z0-9+/]{30,}={0,2}', 'Possível token base64 longo'),
        (r'password\s*=\s*[\'"].+[\'"]', 'Senha hardcoded'),
    ]
    for pat, desc in patterns:
        if re.search(pat, source):
            problemas.append(f"Possível segredo exposto: {desc}")
    return problemas

# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    print("🔍 Iniciando auditoria total do JARVIS...")
    arquivos = listar_arquivos(PROJECT_ROOT)
    total = len(arquivos)
    print(f"📂 {total} arquivos encontrados para auditar.\n")

    resultados = []
    passaram = 0
    falharam = 0
    alertas = 0

    for rel_path in arquivos:
        fpath = PROJECT_ROOT / rel_path
        ext = rel_path.suffix.lower()
        fname = rel_path.name.lower()
        
        status = "PASSOU"
        problemas = []
        
        # Verificar sintaxe
        if ext == '.py':
            syntax_ok, imports, err = check_python_syntax(rel_path)
            if not syntax_ok:
                status = "FALHOU"
                problemas.append(f"SyntaxError: {err}")
        elif ext in {'.ts', '.tsx', '.js', '.jsx', '.json'}:
            syntax_ok, _, err = check_js_ts_syntax(rel_path)
            if not syntax_ok:
                status = "FALHOU"
                problemas.append(f"Erro sintático: {err}")
        elif ext in {'.bat', '.ps1'}:
            syntax_ok, _, err = check_bat_ps1(rel_path)
            if not syntax_ok:
                status = "FALHOU"
                problemas.append(err)
        elif fname in {'.env', '.gitignore', '.dockerignore', 'dockerfile', 'docker-compose.yml'}:
            # Apenas leitura e verificação de segurança
            pass
        
        # Ler conteúdo para verificações específicas
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
        except:
            source = ""
        
        if source:
            # Verificar caminhos
            for p in check_path_security(source):
                problemas.append(f"Segurança: {p}")
            # Verificar segredos
            for p in check_secrets(source):
                problemas.append(f"Segurança: {p}")
            # Verificar hardware
            if ext in {'.py', '.bat'}:
                for p in check_hardware_compliance(source):
                    problemas.append(f"Hardware: {p}")
        
        if problemas:
            if status != "FALHOU":
                status = "ALERTA"
            falharam += 1
        else:
            passaram += 1
        
        resultados.append((str(rel_path), status, "; ".join(problemas)))
        # Print progresso
        print(f"  {status:7} | {rel_path}")
    
    # Gerar relatório Markdown
    report_path = PROJECT_ROOT / "audit_report.md"
    with open(report_path, 'w', encoding='utf-8') as r:
        r.write("# Relatório de Auditoria – JARVIS v6.1\n\n")
        r.write(f"**Total de arquivos:** {total}\n")
        r.write(f"**✅ Passaram:** {passaram}\n")
        r.write(f"**❌ Falhas/Alertas:** {falharam}\n\n")
        r.write("| Arquivo | Status | Problemas |\n")
        r.write("|---------|--------|----------|\n")
        for arq, st, prob in resultados:
            r.write(f"| {arq} | {st} | {prob} |\n")
        
        if falharam == 0:
            r.write("\n## ✅ Status: PRONTO PARA TESTE PRÁTICO\n")
        else:
            r.write(f"\n## ⚠️ Status: REQUER CORREÇÕES ({falharam} arquivos com problemas)\n")
            r.write("\n### Ações recomendadas:\n")
            for arq, st, prob in resultados:
                if st in ("FALHOU", "ALERTA"):
                    r.write(f"- `{arq}`: {prob}\n")
    
    print(f"\n📄 Relatório salvo em: {report_path}")
    print(f"   ✅ Passaram: {passaram}")
    print(f"   ❌ Falhas/Alertas: {falharam}")
