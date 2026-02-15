#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Self-Observer (Sensors & Metrics)
==============================================
Responsável por coletar dados brutos sobre o estado do sistema e do ambiente.
Funciona como os "sentidos" internos do JARVIS.

Responsibilities:
- Coleta de métricas de hardware (CPU, RAM, GPU)
- Scanning de código (Complexidade, Imports, Tamanho)
- Verificação de Health Checks operacionais
- Validação de integridade de configurações
- Geração de relatório consolidado para análise

Author: JARVIS 5.0 Evolution Layer
"""

import os
import ast
import asyncio
import json
import logging
import platform
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# External Dependencies (Graceful degradation)
try:
    import psutil
except ImportError:
    psutil = None

try:
    import pynvml
    HAS_NVIDIA = True
except ImportError:
    pynvml = None
    HAS_NVIDIA = False

try:
    import requests
except ImportError:
    requests = None

# Internal Dependencies
from src.core.config.system_manifest import system_manifest
from src.core.config.blackbox_logger import blackbox_logger
from src.core.infrastructure.async_event_bus import event_bus, EventType, EventPriority

logger = logging.getLogger(__name__)

class SelfObserver:
    """
    Agente de auto-observação que monitora a saúde e integridade do sistema.
    """
    
    def __init__(self):
        self.project_root = system_manifest.project_root
        self.running = False
        self.task = None
        self.interval = 300  # 5 minutos por padrão
        
        # Cache de observações para detectar tendências
        self.last_metrics = {}
        
    async def start(self, interval: int = 300):
        """Inicia o ciclo de observação"""
        if self.running:
            return
        
        self.running = True
        self.interval = interval
        self.task = asyncio.create_task(self._observation_loop())
        logger.info("👁️ Self-Observer started")

    async def stop(self):
        """Para o ciclo de observação"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Self-Observer stopped")

    async def _observation_loop(self):
        """Loop principal de observação"""
        while self.running:
            try:
                logger.debug("🔎 Starting system observation cycle...")
                report = await self.generate_full_report()
                
                # Publica o relatório no barramento
                event_bus.publish(
                    EventType.SYSTEM_OBSERVER_REPORT,
                    data=report,
                    priority=EventPriority.NORMAL,
                    source="self_observer",
                    ttl_seconds=3600  # Relatório válido por 1h
                )
                
                logger.debug("✅ Observation cycle completed and reported")
                
                # Aguarda próximo ciclo
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"❌ Error in observation loop: {e}")
                await asyncio.sleep(60) # Tenta novamente em 1 min se falhar

    async def generate_full_report(self) -> Dict[str, Any]:
        """Gera um relatório completo do estado do sistema"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self._collect_hardware_metrics(),
            "code_health": await self._scan_codebase(),
            "config_health": self._check_config_integrity(),
            "operational_health": await self._run_health_checks(),
            "recent_errors": self._get_recent_errors()
        }

    def _collect_hardware_metrics(self) -> Dict[str, Any]:
        """Coleta uso de CPU, RAM e GPU"""
        metrics = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "gpu_util": 0.0,
            "gpu_temp": 0.0
        }
        
        if psutil:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            metrics["memory_percent"] = psutil.virtual_memory().percent
        
        if HAS_NVIDIA and pynvml:
            try:
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                
                metrics["gpu_util"] = util.gpu
                metrics["gpu_temp"] = temp
                # pynvml.nvmlShutdown() # Keep initialized might be better for freq calls
            except Exception as e:
                logger.warning(f"Failed to read GPU metrics: {e}")
                
        return metrics

    async def _scan_codebase(self) -> Dict[str, Any]:
        """Analisa o código fonte em busca de problemas estruturais"""
        source_dir = self.project_root / "src"
        health = {
            "scanned_files": 0,
            "large_files": [],
            "huge_functions": [],
            "local_imports": [],
            "bare_excepts": []
        }
        
        loop = asyncio.get_running_loop()
        
        def run_scan():
            for root, _, files in os.walk(source_dir):
                if "archive" in root or "tests" in root:
                    continue
                    
                for file in files:
                    if file.endswith(".py"):
                        path = Path(root) / file
                        rel_path = path.relative_to(self.project_root)
                        health["scanned_files"] += 1
                        
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                content = f.read()
                                
                            # Check file size
                            lines = content.splitlines()
                            if len(lines) > 500:
                                health["large_files"].append(str(rel_path))
                                
                            # AST Parsing
                            tree = ast.parse(content)
                            
                            for node in ast.walk(tree):
                                # Check function size and local imports
                                if isinstance(node, ast.FunctionDef):
                                    func_len = node.end_lineno - node.lineno
                                    if func_len > 50:
                                        health["huge_functions"].append({
                                            "file": str(rel_path),
                                            "function": node.name,
                                            "lines": func_len
                                        })
                                    
                                    # Check for local imports
                                    for child in ast.walk(node):
                                        if isinstance(child, (ast.Import, ast.ImportFrom)):
                                            health["local_imports"].append({
                                                "file": str(rel_path),
                                                "function": node.name,
                                                "line": child.lineno
                                            })
                                            
                                # Check for bare excepts
                                if isinstance(node, ast.ExceptHandler):
                                    if node.type is None:
                                        health["bare_excepts"].append({
                                            "file": str(rel_path),
                                            "line": node.lineno
                                        })
                                        
                        except Exception as e:
                            logger.warning(f"Failed to scan {rel_path}: {e}")
            return health

        # Run CPU-bound task in executor
        return await loop.run_in_executor(None, run_scan)

    def _check_config_integrity(self) -> Dict[str, Any]:
        """Verifica se as configurações essenciais existem"""
        issues = {
            "missing_keys": [],
            "invalid_paths": []
        }
        
        # Check critical paths
        paths_to_check = [
            system_manifest.system.data_path,
            system_manifest.system.logs_path,
            system_manifest.database.vector_store_path
        ]
        
        for p in paths_to_check:
            path_obj = Path(str(p))
            if not path_obj.exists() and not str(p).startswith("data/"):
                # Ignore initial missing data dirs as they might be created later, 
                # but warn about system paths
                issues["invalid_paths"].append(str(p))

        # Check critical keys (example)
        if not system_manifest.ai.provider:
            issues["missing_keys"].append("ai.provider")
            
        return issues

    async def _run_health_checks(self) -> Dict[str, bool]:
        """Testa conectividade com subsistemas"""
        status = {
            "ollama": False,
            "internet": False,
            "camera": False # Implementar verificação real se possível
        }
        
        # Check Internet
        try:
            if requests:
                requests.get("https://www.google.com", timeout=2)
                status["internet"] = True
        except:
            pass
            
        # Check Ollama
        try:
            if requests:
                host = system_manifest.ai.ollama_host
                port = system_manifest.ai.ollama_port
                res = requests.get(f"http://{host}:{port}/api/tags", timeout=2)
                if res.status_code == 200:
                    status["ollama"] = True
        except:
            pass
            
        return status

    def _get_recent_errors(self) -> List[Dict]:
        """Recupera erros recentes do Blackbox Logger"""
        try:
            # Assuming query_logs returns a list of objects or dicts
            logs = blackbox_logger.query_logs(level="ERROR", limit=10)
            return [asdict(l) if hasattr(l, 'asdict') else l for l in logs]
        except Exception:
            return []

# Singleton instance
self_observer = SelfObserver()
