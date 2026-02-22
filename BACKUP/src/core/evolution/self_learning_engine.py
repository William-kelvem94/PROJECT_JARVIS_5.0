"""
JARVIS 5.0 - Self-Learning Evolution Engine
Sistema de aprendizado contínuo e auto-melhoria
"""

import json
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import hashlib
import re

logger = logging.getLogger(__name__)


class SelfLearningEngine:
    """Engine de aprendizado contínuo do JARVIS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.learning_data_path = project_root / "data" / "learning" / "self_knowledge"
        self.learning_data_path.mkdir(parents=True, exist_ok=True)

        # Estado de aprendizado
        self.knowledge_base = {}
        self.learning_sessions = []
        self.current_session = None
        self.auto_improvements = []

        # Estatísticas
        self.analysis_count = 0
        self.files_analyzed = 0
        self.insights_generated = 0
        self.improvements_suggested = 0

        # Sistema de aprendizado contínuo
        self.learning_thread = None
        self.is_learning = False
        self.learning_interval = 300  # 5 minutos

        # Carregar conhecimento existente
        self._load_knowledge_base()

    def start_continuous_learning(self):
        """Inicia o aprendizado contínuo em background"""
        if self.is_learning:
            logger.info("🧠 Self-Learning já está ativo")
            return

        self.is_learning = True
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "session_id": hashlib.md5(f"session_{time.time()}".encode()).hexdigest()[
                :8
            ],
            "activities": [],
            "insights": [],
            "improvements": [],
        }

        self.learning_thread = threading.Thread(
            target=self._continuous_learning_loop,
            daemon=True,
            name="SelfLearningEngine",
        )
        self.learning_thread.start()

        logger.info(
            "🧠 Self-Learning Engine iniciado - JARVIS aprendendo sobre si mesmo"
        )

    def stop_continuous_learning(self):
        """Para o aprendizado contínuo e salva o conhecimento"""
        if not self.is_learning:
            return

        self.is_learning = False

        if self.learning_thread:
            self.learning_thread.join(timeout=10)

        # Finalizar sessão atual
        if self.current_session:
            self.current_session["end_time"] = datetime.now().isoformat()
            self.current_session["duration_seconds"] = (
                datetime.fromisoformat(self.current_session["end_time"])
                - datetime.fromisoformat(self.current_session["start_time"])
            ).total_seconds()

            self.learning_sessions.append(self.current_session)

        # Salvar tudo
        self._save_knowledge_base()
        self._generate_learning_report()

        logger.info("🧠 Self-Learning Engine parado - Conhecimento salvo")

    def _continuous_learning_loop(self):
        """Loop principal de aprendizado contínuo"""
        while self.is_learning:
            try:
                # Análise completa do sistema
                self._analyze_entire_system()

                # Gerar insights baseados na análise
                self._generate_insights()

                # Sugerir melhorias
                self._suggest_improvements()

                # Gerar documentação automática
                self._generate_auto_documentation()

                # Salvar progresso periodicamente
                self._save_progress()

                # Aguardar próximo ciclo
                time.sleep(self.learning_interval)

            except Exception as e:
                logger.error(f"Erro no loop de aprendizado: {e}")
                time.sleep(60)  # Aguardar 1 minuto em caso de erro

    def _analyze_entire_system(self):
        """Análise completa de todo o sistema JARVIS"""
        logger.info("🔍 Iniciando análise completa do sistema...")

        analysis_start = time.time()

        # 🚀 DISPARAR AUTO-EVOLUÇÃO (Correção Real de Código)
        try:
            from src.core.intelligence.ai_agent import ai_agent
            if ai_agent:
                logger.info("🦾 JARVIS tentando se auto-corrigir via IA...")
                ai_agent.analyze_codebase(str(self.project_root))
        except Exception as e:
            logger.debug(f"Falha ao disparar auto-evolução: {e}")

        # Analisar código fonte (Estatísticas)
        self._analyze_source_code()

        # Analisar logs
        self._analyze_logs()

        # Analisar configurações
        self._analyze_configurations()

        # Analisar dados de aprendizado
        self._analyze_learning_data()

        # Analisar performance
        self._analyze_performance()

        analysis_time = time.time() - analysis_start
        self.analysis_count += 1

        # Registrar atividade
        if self.current_session:
            self.current_session["activities"].append(
                {
                    "type": "system_analysis",
                    "timestamp": datetime.now().isoformat(),
                    "duration": analysis_time,
                    "files_analyzed": self.files_analyzed,
                }
            )

            self.analysis_count += 1

        logger.info(f"🔍 Análise completa em {analysis_time:.2f} segundos")

    def _analyze_source_code(self):
        """Analisa todo o código fonte do JARVIS"""
        src_path = self.project_root / "src"

        if not src_path.exists():
            return

        code_stats = {
            "python_files": 0,
            "total_lines": 0,
            "classes": 0,
            "functions": 0,
            "imports": {},
            "complexity_indicators": [],
        }

        for py_file in src_path.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                code_stats["python_files"] += 1
                lines = len(content.split("\n"))
                code_stats["total_lines"] += lines

                # Contar classes e funções
                code_stats["classes"] += len(
                    re.findall(r"^class\s+\w+", content, re.MULTILINE)
                )
                code_stats["functions"] += len(
                    re.findall(r"^def\s+\w+", content, re.MULTILINE)
                )

                # Analisar imports
                imports = re.findall(
                    r"^(?:from\s+[\w.]+\s+import|import\s+[\w.]+)",
                    content,
                    re.MULTILINE,
                )
                for imp in imports:
                    module = imp.split()[1].split(".")[0]
                    code_stats["imports"][module] = (
                        code_stats["imports"].get(module, 0) + 1
                    )

                # Indicadores de complexidade
                if lines > 500:
                    code_stats["complexity_indicators"].append(
                        {
                            "file": str(py_file.relative_to(self.project_root)),
                            "lines": lines,
                            "issue": "Arquivo muito grande (>500 linhas)",
                        }
                    )

                # Funções muito longas
                functions = re.findall(
                    r"def\s+\w+.*?:.*?(?=\n\s*(?:def|class|$))", content, re.DOTALL
                )
                for func in functions:
                    if len(func.split("\n")) > 50:
                        code_stats["complexity_indicators"].append(
                            {
                                "file": str(py_file.relative_to(self.project_root)),
                                "function": func.split("\n")[0].strip(),
                                "lines": len(func.split("\n")),
                                "issue": "Função muito longa (>50 linhas)",
                            }
                        )

            except Exception as e:
                logger.debug(f"Erro analisando {py_file}: {e}")

        self.knowledge_base["code_analysis"] = code_stats
        self.files_analyzed = code_stats["python_files"]

    def _analyze_logs(self):
        """Analisa logs para identificar padrões e problemas"""
        logs_path = self.project_root / "data" / "logs"

        if not logs_path.exists():
            return

        log_analysis = {
            "error_patterns": {},
            "warning_patterns": {},
            "performance_issues": [],
            "crash_reports": [],
            "memory_usage": [],
            "recent_activity": [],
        }

        # Analisar arquivos de log recentes
        for log_file in logs_path.glob("*.txt"):
            try:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Procurar por erros
                errors = re.findall(r"ERROR.*?:\s*(.+)", content)
                for error in errors:
                    error_key = error[:100]  # Primeiros 100 chars como chave
                    log_analysis["error_patterns"][error_key] = (
                        log_analysis["error_patterns"].get(error_key, 0) + 1
                    )

                # Procurar por warnings
                warnings = re.findall(r"WARNING.*?:\s*(.+)", content)
                for warning in warnings:
                    warn_key = warning[:100]
                    log_analysis["warning_patterns"][warn_key] = (
                        log_analysis["warning_patterns"].get(warn_key, 0) + 1
                    )

                # Procurar por uso de memória
                memory_matches = re.findall(
                    r"memory.*?:?\s*(\d+(?:\.\d+)?)%", content, re.IGNORECASE
                )
                for mem in memory_matches:
                    log_analysis["memory_usage"].append(float(mem))

            except Exception as e:
                logger.debug(f"Erro analisando log {log_file}: {e}")

        self.knowledge_base["log_analysis"] = log_analysis

    def _analyze_configurations(self):
        """Analisa configurações do sistema"""
        config_analysis = {}

        # Analisar arquivos de configuração
        config_files = [
            "config/ai_config.yaml",
            "config/network_mesh_config.yaml",
            "config/vector_store_config.yaml",
        ]

        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Análise básica de configuração
                    config_analysis[config_file] = {
                        "exists": True,
                        "size": len(content),
                        "lines": len(content.split("\n")),
                        "last_modified": datetime.fromtimestamp(
                            config_path.stat().st_mtime
                        ).isoformat(),
                    }

                except Exception as e:
                    config_analysis[config_file] = {"exists": True, "error": str(e)}

        self.knowledge_base["config_analysis"] = config_analysis

    def _analyze_learning_data(self):
        """Analisa dados de aprendizado existentes"""
        learning_analysis = {
            "total_sessions": len(self.learning_sessions),
            "knowledge_entries": len(self.knowledge_base),
            "auto_improvements": len(self.auto_improvements),
            "insights_generated": self.insights_generated,
        }

        self.knowledge_base["learning_analysis"] = learning_analysis

    def _analyze_performance(self):
        """Analisa performance do sistema"""
        performance_data = {
            "analysis_count": self.analysis_count,
            "files_analyzed": self.files_analyzed,
            "avg_analysis_time": 0,  # Será calculado
            "memory_usage_trend": [],
            "cpu_usage_trend": [],
        }

        self.knowledge_base["performance_analysis"] = performance_data

    def _generate_insights(self):
        """Gera insights baseados na análise"""
        insights = []

        # Insights sobre código
        if "code_analysis" in self.knowledge_base:
            code = self.knowledge_base["code_analysis"]

            if code["total_lines"] > 10000:
                insights.append(
                    {
                        "type": "code_complexity",
                        "priority": "high",
                        "title": "Base de código muito grande",
                        "description": f"Sistema tem {code['total_lines']} linhas de código. Considerar modularização.",
                        "suggestion": "Quebrar em módulos menores e mais especializados",
                    }
                )

            if code["complexity_indicators"]:
                insights.append(
                    {
                        "type": "code_quality",
                        "priority": "medium",
                        "title": f"Problemas de complexidade encontrados: {len(code['complexity_indicators'])}",
                        "description": "Arquivos/funções muito grandes detectados",
                        "suggestion": "Refatorar código para melhorar manutenibilidade",
                    }
                )

        # Insights sobre logs
        if "log_analysis" in self.knowledge_base:
            logs = self.knowledge_base["log_analysis"]

            if logs["error_patterns"]:
                top_errors = sorted(
                    logs["error_patterns"].items(), key=lambda x: x[1], reverse=True
                )[:3]
                insights.append(
                    {
                        "type": "error_analysis",
                        "priority": "high",
                        "title": f"Erros mais frequentes: {len(logs['error_patterns'])} padrões",
                        "description": f"Top 3 erros: {', '.join([f'{err[:50]}...' for err, count in top_errors])}",
                        "suggestion": "Implementar correções para erros recorrentes",
                    }
                )

            if logs["memory_usage"] and max(logs["memory_usage"]) > 90:
                insights.append(
                    {
                        "type": "memory_optimization",
                        "priority": "critical",
                        "title": "Uso excessivo de memória detectado",
                        "description": f"Uso máximo de memória: {max(logs['memory_usage']):.1f}%",
                        "suggestion": "Otimizar gerenciamento de memória e implementar limpeza automática",
                    }
                )

        # Salvar insights
        if self.current_session:
            self.current_session["insights"].extend(insights)

        self.insights_generated += len(insights)
        self.knowledge_base["insights"] = insights

    def _suggest_improvements(self):
        """Sugere melhorias baseadas nos insights"""
        improvements = []

        # Melhorias baseadas em insights
        if "insights" in self.knowledge_base:
            for insight in self.knowledge_base["insights"]:
                if insight["priority"] == "critical":
                    improvements.append(
                        {
                            "type": "critical_fix",
                            "title": f"Correção crítica: {insight['title']}",
                            "description": insight["description"],
                            "implementation": insight["suggestion"],
                            "estimated_effort": "high",
                            "priority": "immediate",
                        }
                    )
                elif insight["priority"] == "high":
                    improvements.append(
                        {
                            "type": "optimization",
                            "title": f"Otimização: {insight['title']}",
                            "description": insight["description"],
                            "implementation": insight["suggestion"],
                            "estimated_effort": "medium",
                            "priority": "high",
                        }
                    )

        # Melhorias proativas
        improvements.extend(
            [
                {
                    "type": "monitoring",
                    "title": "Implementar monitoramento avançado",
                    "description": "Adicionar métricas detalhadas de performance e saúde do sistema",
                    "implementation": "Criar dashboard de monitoramento em tempo real",
                    "estimated_effort": "medium",
                    "priority": "medium",
                },
                {
                    "type": "documentation",
                    "title": "Gerar documentação automática",
                    "description": "Sistema deve gerar documentação técnica automaticamente",
                    "implementation": "Implementar geração automática de docs baseada em análise de código",
                    "estimated_effort": "low",
                    "priority": "medium",
                },
            ]
        )

        # Salvar melhorias
        if self.current_session:
            self.current_session["improvements"].extend(improvements)

        self.improvements_suggested += len(improvements)
        self.auto_improvements.extend(improvements)

    def _generate_auto_documentation(self):
        """Gera documentação automática baseada no aprendizado"""
        docs_path = self.project_root / "docs" / "auto_generated"
        docs_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Gerar relatório de sistema
        self._generate_system_report(docs_path, timestamp)

        # Gerar análise de código
        self._generate_code_analysis(docs_path, timestamp)

        # Gerar relatório de melhorias
        self._generate_improvements_report(docs_path, timestamp)

        # Gerar guia de troubleshooting
        self._generate_troubleshooting_guide(docs_path, timestamp)

    def _generate_system_report(self, docs_path: Path, timestamp: str):
        """Gera relatório completo do sistema"""
        report_path = docs_path / f"system_report_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório do Sistema JARVIS 5.0\n\n")
            f.write(
                f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            # Estatísticas gerais
            f.write("## 📊 Estatísticas Gerais\n\n")
            if "code_analysis" in self.knowledge_base:
                code = self.knowledge_base["code_analysis"]
                f.write(f"- **Arquivos Python:** {code['python_files']}\n")
                f.write(f"- **Linhas totais:** {code['total_lines']}\n")
                f.write(f"- **Classes:** {code['classes']}\n")
                f.write(f"- **Funções:** {code['functions']}\n\n")

            # Status de aprendizado
            f.write("## 🧠 Status de Aprendizado\n\n")
            f.write(f"- **Sessões de aprendizado:** {len(self.learning_sessions)}\n")
            f.write(f"- **Análises realizadas:** {self.analysis_count}\n")
            f.write(f"- **Insights gerados:** {self.insights_generated}\n")
            f.write(f"- **Melhorias sugeridas:** {self.improvements_suggested}\n\n")

            # Problemas críticos
            if "insights" in self.knowledge_base:
                critical_insights = [
                    i
                    for i in self.knowledge_base["insights"]
                    if i["priority"] == "critical"
                ]
                if critical_insights:
                    f.write("## 🚨 Problemas Críticos\n\n")
                    for insight in critical_insights:
                        f.write(f"### {insight['title']}\n")
                        f.write(f"{insight['description']}\n\n")
                        f.write(f"**Sugestão:** {insight['suggestion']}\n\n")

    def _generate_code_analysis(self, docs_path: Path, timestamp: str):
        """Gera análise detalhada do código"""
        analysis_path = docs_path / f"code_analysis_{timestamp}.md"

        with open(analysis_path, "w", encoding="utf-8") as f:
            f.write("# Análise de Código - JARVIS 5.0\n\n")
            f.write(
                f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            if "code_analysis" in self.knowledge_base:
                code = self.knowledge_base["code_analysis"]

                f.write("## 📁 Estrutura do Código\n\n")
                f.write(f"- **Total de arquivos:** {code['python_files']}\n")
                f.write(f"- **Linhas de código:** {code['total_lines']}\n")
                f.write(f"- **Classes definidas:** {code['classes']}\n")
                f.write(f"- **Funções definidas:** {code['functions']}\n\n")

                # Imports mais usados
                if code["imports"]:
                    f.write("## 📦 Módulos Mais Importados\n\n")
                    sorted_imports = sorted(
                        code["imports"].items(), key=lambda x: x[1], reverse=True
                    )[:10]
                    for module, count in sorted_imports:
                        f.write(f"- `{module}`: {count} importações\n")
                    f.write("\n")

                # Problemas de complexidade
                if code["complexity_indicators"]:
                    f.write("## ⚠️ Problemas de Complexidade\n\n")
                    for issue in code["complexity_indicators"][:10]:  # Top 10
                        f.write(f"### {issue['file']}\n")
                        f.write(f"- **Problema:** {issue['issue']}\n")
                        if "lines" in issue:
                            f.write(f"- **Linhas:** {issue['lines']}\n")
                        if "function" in issue:
                            f.write(f"- **Função:** `{issue['function']}`\n")
                        f.write("\n")

    def _generate_improvements_report(self, docs_path: Path, timestamp: str):
        """Gera relatório de melhorias sugeridas"""
        improvements_path = docs_path / f"improvements_{timestamp}.md"

        with open(improvements_path, "w", encoding="utf-8") as f:
            f.write("# Melhorias Sugeridas - JARVIS 5.0\n\n")
            f.write(
                f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            if self.auto_improvements:
                # Agrupar por prioridade
                by_priority = {"immediate": [], "high": [], "medium": [], "low": []}

                for imp in self.auto_improvements:
                    priority = imp.get("priority", "medium")
                    by_priority[priority].append(imp)

                for priority in ["immediate", "high", "medium", "low"]:
                    improvements = by_priority[priority]
                    if improvements:
                        f.write(f"## {priority.upper()} PRIORITY\n\n")
                        for imp in improvements:
                            f.write(f"### {imp['title']}\n")
                            f.write(f"{imp['description']}\n\n")
                            f.write(f"**Implementação:** {imp['implementation']}\n")
                            f.write(
                                f"**Esforço estimado:** {imp.get('estimated_effort', 'unknown')}\n\n"
                            )

    def _generate_troubleshooting_guide(self, docs_path: Path, timestamp: str):
        """Gera guia de troubleshooting baseado em análise de logs"""
        guide_path = docs_path / f"troubleshooting_{timestamp}.md"

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write("# Guia de Troubleshooting - JARVIS 5.0\n\n")
            f.write(
                f"**Gerado automaticamente em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            if "log_analysis" in self.knowledge_base:
                logs = self.knowledge_base["log_analysis"]

                # Erros comuns
                if logs["error_patterns"]:
                    f.write("## 🚨 Erros Mais Comuns\n\n")
                    sorted_errors = sorted(
                        logs["error_patterns"].items(), key=lambda x: x[1], reverse=True
                    )[:10]
                    for error, count in sorted_errors:
                        f.write(f"### Erro (ocorrências: {count})\n")
                        f.write(f"```\n{error}\n```\n\n")

                        # Sugestões básicas de correção
                        if "memory" in error.lower():
                            f.write(
                                "**Solução sugerida:** Verificar uso de memória e implementar limpeza automática\n\n"
                            )
                        elif "thread" in error.lower():
                            f.write(
                                "**Solução sugerida:** Revisar gerenciamento de threads e sincronização\n\n"
                            )
                        elif "import" in error.lower():
                            f.write(
                                "**Solução sugerida:** Verificar dependências e instalação de pacotes\n\n"
                            )
                        else:
                            f.write(
                                "**Solução sugerida:** Analisar logs detalhados e contexto do erro\n\n"
                            )

                # Problemas de performance
                if logs["memory_usage"]:
                    avg_memory = sum(logs["memory_usage"]) / len(logs["memory_usage"])
                    max_memory = max(logs["memory_usage"])

                    f.write("## 📊 Performance\n\n")
                    f.write(f"- **Uso médio de memória:** {avg_memory:.1f}%\n")
                    f.write(f"- **Uso máximo de memória:** {max_memory:.1f}%\n\n")

                    if max_memory > 90:
                        f.write(
                            "⚠️ **ALERTA:** Uso excessivo de memória detectado!\n\n"
                        )
                        f.write("**Ações recomendadas:**\n")
                        f.write("1. Implementar descarga automática de modelos\n")
                        f.write("2. Otimizar gerenciamento de cache\n")
                        f.write("3. Monitorar vazamentos de memória\n")
                        f.write("4. Considerar limpeza periódica de dados\n\n")

    def _save_progress(self):
        """Salva progresso do aprendizado periodicamente"""
        progress_file = self.learning_data_path / "learning_progress.json"

        progress_data = {
            "last_update": datetime.now().isoformat(),
            "analysis_count": self.analysis_count,
            "insights_generated": self.insights_generated,
            "improvements_suggested": self.improvements_suggested,
            "current_session": (
                self.current_session["session_id"] if self.current_session else None
            ),
        }

        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)

    def _load_knowledge_base(self):
        """Carrega base de conhecimento existente"""
        knowledge_file = self.learning_data_path / "knowledge_base.json"
        sessions_file = self.learning_data_path / "learning_sessions.json"

        # Carregar conhecimento
        if knowledge_file.exists():
            try:
                with open(knowledge_file, "r", encoding="utf-8") as f:
                    self.knowledge_base = json.load(f)
            except Exception as e:
                logger.warning(f"Erro carregando knowledge base: {e}")
                self.knowledge_base = {}

        # Carregar sessões
        if sessions_file.exists():
            try:
                with open(sessions_file, "r", encoding="utf-8") as f:
                    self.learning_sessions = json.load(f)
            except Exception as e:
                logger.warning(f"Erro carregando learning sessions: {e}")
                self.learning_sessions = []

    def _save_knowledge_base(self):
        """Salva base de conhecimento"""
        knowledge_file = self.learning_data_path / "knowledge_base.json"
        sessions_file = self.learning_data_path / "learning_sessions.json"

        # Salvar conhecimento
        with open(knowledge_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)

        # Salvar sessões
        with open(sessions_file, "w", encoding="utf-8") as f:
            json.dump(self.learning_sessions, f, indent=2, ensure_ascii=False)

    def _generate_learning_report(self):
        """Gera relatório final da sessão de aprendizado"""
        if not self.current_session:
            return

        report_path = (
            self.learning_data_path
            / f"session_report_{self.current_session['session_id']}.md"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório da Sessão de Aprendizado\n\n")
            f.write(f"**ID da Sessão:** {self.current_session['session_id']}\n")
            f.write(f"**Início:** {self.current_session['start_time']}\n")
            f.write(
                f"**Fim:** {self.current_session.get('end_time', 'Em andamento')}\n"
            )
            f.write(
                f"**Duração:** {self.current_session.get('duration_seconds', 0):.1f} segundos\n\n"
            )

            # Atividades realizadas
            if self.current_session["activities"]:
                f.write("## 📋 Atividades Realizadas\n\n")
                for activity in self.current_session["activities"]:
                    f.write(f"- **{activity['type']}** ({activity['timestamp']})\n")
                    f.write(f"  - Duração: {activity.get('duration', 0):.2f}s\n")
                    if "files_analyzed" in activity:
                        f.write(
                            f"  - Arquivos analisados: {activity['files_analyzed']}\n"
                        )
                    f.write("\n")

            # Insights gerados
            if self.current_session["insights"]:
                f.write("## 💡 Insights Gerados\n\n")
                for insight in self.current_session["insights"]:
                    f.write(f"### {insight['title']} ({insight['priority'].upper()})\n")
                    f.write(f"{insight['description']}\n\n")

            # Melhorias sugeridas
            if self.current_session["improvements"]:
                f.write("## 🚀 Melhorias Sugeridas\n\n")
                for improvement in self.current_session["improvements"]:
                    f.write(f"### {improvement['title']}\n")
                    f.write(f"{improvement['description']}\n\n")
                    f.write(f"**Implementação:** {improvement['implementation']}\n")
                    f.write(
                        f"**Prioridade:** {improvement.get('priority', 'medium')}\n\n"
                    )

    def get_learning_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do aprendizado"""
        return {
            "total_sessions": len(self.learning_sessions),
            "current_session_active": self.is_learning,
            "analysis_count": self.analysis_count,
            "insights_generated": self.insights_generated,
            "improvements_suggested": self.improvements_suggested,
            "knowledge_entries": len(self.knowledge_base),
            "last_analysis": self.knowledge_base.get("last_analysis"),
        }

    def force_save_knowledge(self):
        """Força salvamento imediato do conhecimento"""
        self._save_knowledge_base()
        logger.info("🧠 Conhecimento salvo forçadamente")
