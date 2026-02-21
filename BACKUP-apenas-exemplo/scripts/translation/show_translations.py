#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para traduzir commits um por um usando git commit --amend
"""

import subprocess

# Mapeamento de traduções
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
    "Remove obsolete documentation and scripts related to JARVIS 5.0, including analysis, API documentation, architecture, and various setup scripts, to streamline the project structure and focus on essential components.": "🗑️ Remover documentação e scripts obsoletos do JARVIS 5.0 para simplificar estrutura do projeto",
    "Add session_stats.json with session metrics": "📊 Adicionar session_stats.json com métricas de sessão",
    "Add autonomous launcher and project validator": "🚀 Adicionar launcher autônomo e validador de projeto",
    "Add quick setup checkers and improve documentation": "⚡ Adicionar verificadores de configuração rápida e melhorar documentação",
    "Add comprehensive implementation summary": "📋 Adicionar resumo abrangente de implementação",
    "Fix critical dependencies: add mss, edge-tts, mediapipe, face-recognition, PyYAML and upgrade torch to 2.5.1": "🔧 Corrigir dependências críticas: adicionar mss, edge-tts, mediapipe, face-recognition, PyYAML e atualizar torch para 2.5.1",
    "Address PR review comments: fix admin privileges, error handling, validation, and documentation": "✅ Abordar comentários de revisão do PR: corrigir privilégios de admin, manipulação de erros, validação e documentação",
    "Add graceful fallbacks for optional dependencies (mss, edge-tts, pygame, PIL)": "🛡️ Adicionar fallbacks graciosos para dependências opcionais (mss, edge-tts, pygame, PIL)",
    "Address code review feedback: simplify encoding handling, fix spelling, specify Python 3.11": "📝 Abordar feedback de revisão: simplificar manipulação de encoding, corrigir ortografia, especificar Python 3.11",
    "Add comprehensive CHANGELOG documenting all fixes and improvements": "📋 Adicionar CHANGELOG abrangente documentando correções e melhorias",
    "SECURITY: Upgrade torch to 2.6.0, Pillow to 10.3.0, aiohttp to 3.9.4 - patch 6 CVEs": "🔒 SEGURANÇA: Atualizar torch 2.6.0, Pillow 10.3.0, aiohttp 3.9.4 - corrigir 6 CVEs",
    "SECURITY: Upgrade aiohttp to 3.13.3 to fully patch all zip bomb vulnerabilities": "🔐 SEGURANÇA: Atualizar aiohttp 3.13.3 para corrigir vulnerabilidades de zip bomb",
    "SECURITY: Update ALL requirements files and docs - remove all torch 2.1.2 references": "🛡️ SEGURANÇA: Atualizar todos os arquivos de requisitos e docs - remover referências torch 2.1.2",
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
    "Add comprehensive AGI Learning Core documentation with all features and adaptive mode": "📚 Adicionar documentação abrangente do AGI Learning Core com recursos e modo adaptativo",
    "Complete Chameleon Installer: adaptive setup, dependency manager, launcher, and profile requirements": "🦎 Completar Instalador Chameleon: configuração adaptativa, gerenciador de dependências, launcher e requisitos",
    "Add comprehensive Chameleon Installer documentation with examples and troubleshooting": "📖 Adicionar documentação abrangente do Instalador Chameleon com exemplos e solução de problemas",
    "Fix import errors in learning modules with proper mock fallbacks": "🔧 Corrigir erros de importação nos módulos de aprendizagem com fallbacks mock adequados",
    "Fix import errors in core modules with proper conditional imports": "🐛 Corrigir erros de importação nos módulos principais com importações condicionais adequadas",
    "Complete validation: fix directory creation, add validation script, 100% success rate": "✅ Validação completa: corrigir criação de diretório, adicionar script de validação, 100% de taxa de sucesso",
    "Final verification complete: comprehensive implementation report with 100% validation": "🎉 Verificação final: relatório de implementação abrangente com 100% de validação",
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

print("📊 Total de traduções mapeadas:", len(TRANSLATIONS))
print("\n🔄 Execute manualmente os seguintes comandos para traduzir os commits:\n")

# Obtém lista de commits
result = subprocess.run(
    ["git", "log", "--pretty=format:%H|||%s", "--reverse"],
    capture_output=True,
    text=True,
    encoding="utf-8",
)

for line in result.stdout.strip().split("\n"):
    if "|||" in line:
        hash_c, msg = line.split("|||", 1)
        if msg.strip() in TRANSLATIONS:
            translated = TRANSLATIONS[msg.strip()]
            print(f"# Traduzindo: {msg.strip()}")
            print(f"git show {hash_c[:8]} --no-patch")
            print(f"# Traduzido: {translated}")
            print()
