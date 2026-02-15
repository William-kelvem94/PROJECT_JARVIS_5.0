#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Auto Healer (Diagnostic & Strategy Layer)
======================================================
Recebe relatórios de observação e decide como corrigir problemas.
Usa LLM local para interpretar erros e gerar soluções.

Responsibilities:
- Análise de relatórios de saúde
- Gestão da base de conhecimento de erros
- Consulta à LLM para geração de fixes
- Priorização de ações corretivas
- Geração de planos para execução

Author: JARVIS 5.0 Evolution Layer
"""

import json
import logging
import asyncio
import sqlite3
import hashlib
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.core.config.system_manifest import system_manifest
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority
from src.core.infrastructure.async_event_bus import Event

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "learning" / "knowledge.db"

class AutoHealer:
    """
    Mente Analítica do sistema de autocorreção.
    """
    
    def __init__(self):
        self.running = False
        self.ollama_url = f"http://{system_manifest.ai.ollama_host}:{system_manifest.ai.ollama_port}/api/generate"
        self.model = system_manifest.ai.ollama_model
        
    async def start(self):
        """Inicia o Auto Healer"""
        if self.running:
            return
            
        self.running = True
        
        # Inscreve-se no relatório do observador
        await event_bus.subscribe(
            EventType.SYSTEM_OBSERVER_REPORT,
            self._handle_observer_report,
            priority_filter=[EventPriority.NORMAL]
        )
        
        logger.info("🧠 Auto-Healer operational")

    async def stop(self):
        self.running = False
        logger.info("🧠 Auto-Healer stopped")

    async def _handle_observer_report(self, event: Event):
        """Processa o relatório de saúde"""
        if not self.running:
            return
            
        report = event.data
        problems = self._identify_problems(report)
        
        if not problems:
            logger.debug("✨ System healthy, no healing needed.")
            return

        logger.info(f"🤒 Detected {len(problems)} health issues")
        
        plan = await self._create_healing_plan(problems)
        
        if plan:
            event_bus.publish(
                EventType.SYSTEM_DIAGNOSTIC_PLAN,
                data={"plan": plan},
                priority=EventPriority.HIGH,
                source="auto_healer"
            )

    def _identify_problems(self, report: Dict) -> List[Dict]:
        """Extrai problemas acionáveis do relatório"""
        problems = []
        
        # 1. Config Missing Keys
        if report.get("config_health", {}).get("missing_keys"):
            for key in report["config_health"]["missing_keys"]:
                problems.append({
                    "type": "config_missing",
                    "details": key,
                    "severity": "high"
                })

        # 2. Syntax Errors / Static Analysis
        code_health = report.get("code_health", {})
        if code_health.get("bare_excepts"):
            for item in code_health["bare_excepts"]:
                problems.append({
                    "type": "code_quality",
                    "subtype": "bare_except",
                    "file": item["file"],
                    "line": item["line"],
                    "severity": "low"
                })
                
        # 3. Runtime Errors (from logs)
        if report.get("recent_errors"):
            for err in report["recent_errors"]:
                problems.append({
                    "type": "runtime_error",
                    "message": err.get("message"),
                    "component": err.get("component"),
                    "severity": "medium",
                    "hash": self._hash_error(err)
                })
                
        return problems

    def _hash_error(self, error: Dict) -> str:
        """Gera um hash único para o erro"""
        s = f"{error.get('component')}:{error.get('message')}"
        return hashlib.sha256(s.encode()).hexdigest()

    async def _create_healing_plan(self, problems: List[Dict]) -> List[Dict]:
        """Gera um plano de ação para os problemas"""
        plan = []
        
        for problem in problems:
            # Check knowledge base first
            solution = self._check_knowledge_base(problem)
            
            if not solution:
                # Ask LLM
                solution = await self._consult_llm(problem)
            
            if solution:
                plan.append(solution)
                
        return plan

    def _check_knowledge_base(self, problem: Dict) -> Optional[Dict]:
        """Verifica se já sabemos resolver este problema"""
        if "hash" not in problem:
            return None
            
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT action_type, description, files_modified, code_diff 
                    FROM solutions 
                    JOIN problems ON solutions.problem_hash = problems.hash
                    WHERE problems.hash = ? AND solutions.success = 1
                    ORDER BY solutions.impact_score DESC
                    LIMIT 1
                """, (problem["hash"],))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "type": row[0],
                        "description": row[1],
                        "files": json.loads(row[2]) if row[2] else [],
                        "diff": row[3],
                        "source": "knowledge_base"
                    }
        except Exception as e:
            logger.error(f"KB Lookup failed: {e}")
            
        return None

    async def _consult_llm(self, problem: Dict) -> Optional[Dict]:
        """Consulta o LLM para sugerir correção"""
        prompt = self._build_prompt(problem)
        
        try:
            # Call Ollama
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "")
                
                # Parse JSON
                try:
                    action = json.loads(text)
                    # Validate schema basics
                    if "tipo" in action and "descricao" in action:
                        return action
                except json.JSONDecodeError:
                    logger.warning("LLM returned invalid JSON")
                    
        except Exception as e:
            logger.error(f"LLM consultation failed: {e}")
            
        return None

    def _build_prompt(self, problem: Dict) -> str:
        """Constrói o prompt para o LLM"""
        return f"""
        Você é um engenheiro de software sênior mantendo o sistema JARVIS.
        Analise o seguinte problema e sugira uma correção.
        
        PROBLEMA:
        {json.dumps(problem, indent=2)}
        
        REGRAS:
        1. Responda APENAS com um JSON válido.
        2. O JSON deve ter os campos: "tipo" (codigo/configuracao), "descricao", "arquivo" (caminho), "codigo_corrigido" (conteudo completo ou trecho), "linha_inicio" (opcional).
        3. Se for um erro de configuração, sugira o valor correto.
        4. Se for 'bare except', sugira 'except Exception as e: logger.error(e)'.
        """

# Singleton
auto_healer = AutoHealer()
