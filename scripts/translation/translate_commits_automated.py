#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script automatizado para traduzir commits em inglês para português brasileiro
Mantém ordem cronológica e datas originais
"""

import subprocess

# Dicionário de traduções profissionais
TRANSLATIONS = {
    "Initial project structure for Jarvis IA": "🎯 Estrutura inicial do projeto Jarvis IA",
    "Initial plan": "📋 Plano inicial",
    "Add comprehensive training infrastructure with orchestrator": "🚀 Adicionar infraestrutura abrangente de treinamento com orquestrador",
    "Add web search and research capabilities with integrated context": "🔍 Adicionar capacidades de pesquisa web e research com contexto integrado",
    "Add complete JARVIS system: multi-platform control + continuous training": "✨ Adicionar sistema JARVIS completo: controle multiplataforma + treinamento contínuo",
    "Add comprehensive JARVIS complete usage guide": "📚 Adicionar guia completo de uso do JARVIS",
    "Fix security and quality issues from code review": "🔒 Corrigir problemas de segurança e qualidade da revisão de código",
    "Final: Complete JARVIS project summary and documentation": "🎉 Final: Resumo completo do projeto JARVIS e documentação",
    "Replace DuckDuckGo/Wikipedia with secure Google Search + security measures": "🔐 Substituir DuckDuckGo/Wikipedia por Google Search seguro + medidas de segurança",
    "Clean up backup files": "🧹 Limpar arquivos de backup",
    "Improve security and robustness based on code review feedback": "🛡️ Melhorar segurança e robustez baseado no feedback da revisão de código",
    "Update documentation to reflect Google Search implementation": "📝 Atualizar documentação para refletir implementação do Google Search",
    "Remove obsolete documentation and scripts related to JARVIS 5.0, including analysis, API documentation, architecture, and various setup scripts, to streamline the project structure and focus on essential components.": "🗑️ Remover documentação e scripts obsoletos relacionados ao JARVIS 5.0, incluindo análise, documentação de API, arquitetura e vários scripts de configuração, para simplificar a estrutura do projeto e focar em componentes essenciais",
    "Add session_stats.json with session metrics": "📊 Adicionar session_stats.json com métricas de sessão",
    "Add autonomous launcher and project validator": "🚀 Adicionar launcher autônomo e validador de projeto",
    "Add quick setup checkers and improve documentation": "⚡ Adicionar verificadores de configuração rápida e melhorar documentação",
    "Add comprehensive implementation summary": "📋 Adicionar resumo abrangente de implementação",
    "Fix critical dependencies: add mss, edge-tts, mediapipe, face-recognition, PyYAML and upgrade torch to 2.5.1": "🔧 Corrigir dependências críticas: adicionar mss, edge-tts, mediapipe, face-recognition, PyYAML e atualizar torch para 2.5.1",
    "Address PR review comments: fix admin privileges, error handling, validation, and documentation": "✅ Abordar comentários de revisão do PR: corrigir privilégios de admin, manipulação de erros, validação e documentação",
    "Add graceful fallbacks for optional dependencies (mss, edge-tts, pygame, PIL)": "🛡️ Adicionar fallbacks graciosos para dependências opcionais (mss, edge-tts, pygame, PIL)",
    "Address code review feedback: simplify encoding handling, fix spelling, specify Python 3.11": "📝 Abordar feedback de revisão de código: simplificar manipulação de encoding, corrigir ortografia, especificar Python 3.11",
    "Add comprehensive CHANGELOG documenting all fixes and improvements": "📋 Adicionar CHANGELOG abrangente documentando todas as correções e melhorias",
    "SECURITY: Upgrade torch to 2.6.0, Pillow to 10.3.0, aiohttp to 3.9.4 - patch 6 CVEs": "🔒 SEGURANÇA: Atualizar torch para 2.6.0, Pillow para 10.3.0, aiohttp para 3.9.4 - corrigir 6 CVEs",
    "SECURITY: Upgrade aiohttp to 3.13.3 to fully patch all zip bomb vulnerabilities": "🔐 SEGURANÇA: Atualizar aiohttp para 3.13.3 para corrigir completamente todas as vulnerabilidades de zip bomb",
    "SECURITY: Update ALL requirements files and docs - remove all torch 2.1.2 references": "🛡️ SEGURANÇA: Atualizar TODOS os arquivos de requisitos e docs - remover todas as referências ao torch 2.1.2",
    "Fix main_singularity.py imports and create modern enhanced HUD": "🔧 Corrigir imports do main_singularity.py e criar HUD moderno aprimorado",
    "Fix indentation errors in hud.py - ensure proper class nesting": "🐛 Corrigir erros de indentação em hud.py - garantir aninhamento adequado de classes",
    "Add comprehensive documentation for Modern HUD and revalidation report": "📚 Adicionar documentação abrangente para HUD Moderno e relatório de revalidação",
    "Add final revalidation summary - project complete and production ready": "✅ Adicionar resumo final de revalidação - projeto completo e pronto para produção",
    "Implement JARVIS Singularity architecture: dual interface, vision system, and God Mode": "🚀 Implementar arquitetura JARVIS Singularity: interface dupla, sistema de visão e God Mode",
    "Add comprehensive Singularity architecture documentation": "📖 Adicionar documentação abrangente da arquitetura Singularity",
    "Implement auto-installer, Control Dashboard, and enhanced audio system": "⚙️ Implementar auto-instalador, Painel de Controle e sistema de áudio aprimorado",
    "Complete integration: Zero-error main entry, updated requirements, comprehensive quick start guide": "✨ Integração completa: entrada principal sem erros, requisitos atualizados, guia de início rápido abrangente",
    "Implement AGI Machine Learning Core: dataset builder, trainer, dream cycle, and autonomy": "🧠 Implementar AGI Machine Learning Core: construtor de dataset, treinador, ciclo de sonhos e autonomia",
    "Add comprehensive JARVIS AGI Machine Learning Core modules": "🤖 Adicionar módulos abrangentes do JARVIS AGI Machine Learning Core",
    "Implement Adaptive Mode: All-in-one intelligent behavior combining all modes dynamically": "🎯 Implementar Modo Adaptativo: comportamento inteligente tudo-em-um combinando todos os modos dinamicamente",
    "Add comprehensive AGI Learning Core documentation with all features and adaptive mode": "📚 Adicionar documentação abrangente do AGI Learning Core com todos os recursos e modo adaptativo",
    "Complete Chameleon Installer: adaptive setup, dependency manager, launcher, and profile requirements": "🦎 Completar Instalador Chameleon: configuração adaptativa, gerenciador de dependências, launcher e requisitos de perfil",
    "Add comprehensive Chameleon Installer documentation with examples and troubleshooting": "📖 Adicionar documentação abrangente do Instalador Chameleon com exemplos e solução de problemas",
    "Fix import errors in learning modules with proper mock fallbacks": "🔧 Corrigir erros de importação nos módulos de aprendizagem com fallbacks mock adequados",
    "Fix import errors in core modules with proper conditional imports": "🐛 Corrigir erros de importação nos módulos principais com importações condicionais adequadas",
    "Complete validation: fix directory creation, add validation script, 100% success rate": "✅ Validação completa: corrigir criação de diretório, adicionar script de validação, 100% de taxa de sucesso",
    "Final verification complete: comprehensive implementation report with 100% validation": "🎉 Verificação final completa: relatório de implementação abrangente com 100% de validação",
    "Add comprehensive PROJECT_STATUS_FINAL.md with complete implementation summary": "📋 Adicionar PROJECT_STATUS_FINAL.md abrangente com resumo de implementação completa",
    "Clean up project structure - keep only complete hybrid version": "🧹 Limpar estrutura do projeto - manter apenas versão híbrida completa",
    "Add organization guide and update changelog": "📚 Adicionar guia de organização e atualizar changelog",
    "Add final summary of project organization": "📝 Adicionar resumo final da organização do projeto",
    "Fix JARVIS.bat and handle Windows installation issues": "🔧 Corrigir JARVIS.bat e lidar com problemas de instalação do Windows",
    "Start comprehensive JARVIS.bat revalidation": "🔍 Iniciar revalidação abrangente do JARVIS.bat",
    "Complete JARVIS.bat rewrite - robust, clean and intelligent launcher": "✨ Reescrita completa do JARVIS.bat - launcher robusto, limpo e inteligente",
    "Add comprehensive resolution guide - project ready to use": "📚 Adicionar guia de resolução abrangente - projeto pronto para uso",
    "Final commit: Complete project resolution with quick start guide": "🎉 Commit final: Resolução completa do projeto com guia de início rápido",
    "v5.0.0 (Singularity Core) - Final Polish & Validate": "✨ v5.0.0 (Singularity Core) - Polimento Final e Validação",
    "Organize: Moved validation reports to docs/reports/ for cleaner root.": "📁 Organizar: Movidos relatórios de validação para docs/reports/ para raiz mais limpa",
    "v5.0.0 (Singularity Core) - Final Validation & Singularity Protocol Enabled": "🎯 v5.0.0 (Singularity Core) - Validação Final e Protocolo Singularity Habilitado",
}


def translate_message(msg):
    """Traduz mensagem de commit"""
    # Verifica tradução direta
    if msg in TRANSLATIONS:
        return TRANSLATIONS[msg]

    # Remove comentário # empty se existir
    msg = msg.replace(" # empty", "").strip()

    # Se já está em português, retorna sem alteração
    portuguese_words = [
        "feat",
        "fix",
        "refactor",
        "docs",
        "chore",
        "style",
        "Implementação",
        "Correção",
        "Atualiza",
        "Adiciona",
        "Remove",
        "Migração",
        "feat(",
    ]
    if any(word in msg for word in portuguese_words):
        return msg

    # Traduções parciais
    translations_map = {
        "Add ": "📚 Adicionar ",
        "Fix ": "🔧 Corrigir ",
        "Update ": "🔄 Atualizar ",
        "Implement ": "✨ Implementar ",
        "Remove ": "🗑️ Remover ",
        "Clean up": "🧹 Limpar",
        "Complete ": "✅ Completar ",
        "Initial ": "🎯 Inicial ",
        "Final ": "🎉 Final ",
        "SECURITY:": "🔒 SEGURANÇA:",
    }

    translated = msg
    for eng, pt in translations_map.items():
        if msg.startswith(eng):
            translated = msg.replace(eng, pt, 1)
            break

    # Se não foi traduzido, adiciona emoji baseado em palavras-chave
    if translated == msg:
        if "security" in msg.lower() or "patch" in msg.lower():
            translated = "🔒 " + msg
        elif "fix" in msg.lower() or "error" in msg.lower():
            translated = "🔧 " + msg
        elif "add" in msg.lower() or "implement" in msg.lower():
            translated = "✨ " + msg
        elif "documentation" in msg.lower() or "doc" in msg.lower():
            translated = "📚 " + msg

    return translated


def main():
    print("🔄 Iniciando tradução automática de commits...")
    print("📋 Processando branch: dev-new-version")

    # Obtém todos os commits
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H|||%s|||%ai|||%an|||%ae", "--reverse"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        print(f"❌ Erro ao obter commits: {result.stderr}")
        return False

    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|||" in line:
            parts = line.split("|||")
            if len(parts) >= 5:
                hash_c, msg, date, author, email = parts
                commits.append(
                    {
                        "hash": hash_c.strip(),
                        "message": msg.strip(),
                        "date": date.strip(),
                        "author": author.strip(),
                        "email": email.strip(),
                    }
                )

    print(f"📊 Total de commits: {len(commits)}")

    # Identifica commits em inglês
    english_commits = []
    for commit in commits:
        msg = commit["message"]
        # Verifica se está em inglês
        english_patterns = [
            "Initial project",
            "Add ",
            "Fix ",
            "Update ",
            "Implement ",
            "Remove ",
            "Complete ",
            "Final ",
            "Clean up",
            "Improve ",
            "Address ",
            "SECURITY:",
            "Organize:",
            "Merge pull request",
        ]

        # Ignora se já tem emoji ou se está em português
        if msg.startswith("🎯") or msg.startswith("📋") or msg.startswith("✨"):
            continue
        if any(
            word in msg
            for word in [
                "Implementação",
                "Correção",
                "Atualiza",
                "feat(",
                "fix(",
                "refactor(",
            ]
        ):
            continue
        if any(msg.startswith(pattern) for pattern in english_patterns):
            english_commits.append(commit)

    print(f"🌍 Commits em inglês encontrados: {len(english_commits)}")

    # Mostra preview
    print("\n📝 Preview das traduções:")
    for c in english_commits[:5]:
        translated = translate_message(c["message"])
        print(f"  {c['hash'][:8]}: {c['message']}")
        print(f"  ➜ {translated}\n")

    if len(english_commits) > 5:
        print(f"  ... e mais {len(english_commits) - 5} commits\n")

    response = input("✅ Prosseguir com a tradução? (s/N): ").strip().lower()
    if response not in ["s", "sim", "y", "yes"]:
        print("❌ Tradução cancelada pelo usuário")
        return False

    print("\n🔄 Aplicando traduções usando filter-branch...")

    # Cria arquivo de mapeamento
    mapping_file = "commit_translations_map.txt"
    with open(mapping_file, "w", encoding="utf-8") as f:
        for c in english_commits:
            translated = translate_message(c["message"])
            f.write(f"{c['hash']}|||{translated}\n")

    # Cria script de filtro
    filter_script = f"""#!/usr/bin/env python3
import sys
translations = {{}}
with open('{mapping_file}', 'r', encoding='utf-8') as f:
    for line in f:
        if '|||' in line:
            hash_c, trans = line.strip().split('|||', 1)
            translations[hash_c] = trans

commit_msg = sys.stdin.read().strip()

# Tenta obter hash do commit atual (não disponível diretamente no msg-filter)
# Mas podemos comparar a mensagem
for hash_c, trans in translations.items():
    if hash_c in commit_msg or True:  # Aplica para todos
        print(trans)
        sys.exit(0)

print(commit_msg)
"""

    with open("msg_filter.py", "w", encoding="utf-8") as f:
        f.write(filter_script)

    # Executa filter-branch para toda a branch
    cmd = ["git", "filter-branch", "-f", "--msg-filter", "python msg_filter.py", "--"]
    print(f"🚀 Executando: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Traduções aplicadas com sucesso!")
        print("\n🎉 Histórico reescrito com mensagens em português brasileiro")
        print("📌 Para aplicar no repositório remoto:")
        print("   git push --force-with-lease origin dev-new-version")
    else:
        print(f"❌ Erro durante filter-branch: {result.stderr}")
        return False

    # Limpa arquivos temporários
    import os

    try:
        os.remove(mapping_file)
        os.remove("msg_filter.py")
    except BaseException:
        pass

    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback

        traceback.print_exc()
